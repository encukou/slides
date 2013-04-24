from __future__ import print_function, unicode_literals, division

import subprocess
import sys


def run(*command):
    print(command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    return process.stdout


visclass_by_type = {}
def visclass(cls):
    visclass_by_type[cls.type] = cls
    return cls


@visclass
class Commit(object):
    type = 'commit'
    def __init__(self, graph, sha):
        self.graph = graph
        self.name = sha
        self.parents = []
        stdout = run('git', 'cat-file', sha, '-p')
        for line in stdout:
            line = line.strip()
            name, space, value = line.partition(' ')
            if not space:
                self.message = ''.join(stdout)
                break
            if name == 'tree':
                self.tree = self.graph.add_object(value)
                graph.add_edge(self, self.tree, CommitTree)
            elif name == 'author':
                self.author = value
            elif name == 'committer':
                self.committer = value
            elif name == 'parent':
                parent = self.graph.add_object(value)
                self.parents.append(parent)
                graph.add_edge(self, parent, CommitParent)
            else:
                print('Warning: unknown commit line:', line)

    @property
    def summary(self):
        return self.message.partition('\n')[0]

@visclass
class Tree(object):
    type = 'tree'
    summary = None
    def __init__(self, graph, sha):
        self.graph = graph
        self.name = sha
        self.children = {}
        for line in run('git', 'cat-file', sha, '-p'):
            line = line.strip()
            info, tab, filename = line.partition('\t')
            obj = self.add_child(info, filename)
            graph.add_edge(self, obj, TreeEntry, filename)

    def add_child(self, info, name):
        mode, type, sha = info.split(' ')
        child = self.graph.add_object(sha)
        self.children[name] = child
        return child


@visclass
class Blob(object):
    type = 'blob'
    summary = None
    def __init__(self, graph, sha):
        self.graph = graph
        self.name = sha
        self.contents = run('git', 'cat-file', sha, '-p').read()


class Ref(object):
    type = 'ref'
    def __init__(self, graph, name, target):
        self.graph = graph
        self.name = name
        self.target = target
        graph.add_edge(self, target, RefTarget)

    @property
    def summary(self):
        return self.target.name


class Edge(object):
    def __init__(self, graph, a, b):
        self.graph = graph
        self.a = a
        self.b = b

    @property
    def summary(self):
        return self.type


class CommitTree(Edge):
    type = 'tree'


class CommitParent(Edge):
    type = 'parent'


class RefTarget(Edge):
    type = 'target'


class TreeEntry(Edge):
    type = 'entry'
    def __init__(self, graph, a, b, filename):
        Edge.__init__(self, graph, a, b)
        self.filename = filename

    @property
    def summary(self):
        return './' + self.filename


class Graph(object):
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.objects = {}
        self.edges = {}
        self.update()

    def update(self):
        self.lingering = self.objects
        self.objects = {}
        for line in run('git', 'show-ref'):
            sha, name = line.strip().split()
            obj = self.add_object(sha)
            self.add_ref(name, obj)
        for line in run('git', 'symbolic-ref', 'HEAD'):
            name = line.strip()
            self.add_ref('HEAD', self.add_ref(name))

    def _add(func):
        def adder(self, name, *args, **kwargs):
            try:
                obj = self.objects[name]
            except KeyError:
                try:
                    obj = self.lingering[name]
                    del self.lingering[name]
                except KeyError:
                    obj = func(self, name, *args, **kwargs)
            self.objects[name] = obj
            return obj
        return adder

    @_add
    def add_ref(self, name, target=None):
        if target is None:
            for line in run('git', 'rev-parse', name):
                target = self.add_object(line.strip())
        assert target is not None
        return Ref(self, name, target)

    @_add
    def add_object(self, sha):
        obj_type = run('git', 'cat-file', sha, '-t').read().strip()
        try:
            visclass = visclass_by_type[obj_type]
        except KeyError:
            print('Warning: unknown object type:', obj_type)
            return
        return visclass(self, sha)

    def add_edge(self, a, b, cls, *args):
        try:
            edge = self.edges[a, b, cls, args]
        except Exception:
            edge = cls(self, a, b, *args)
            self.edges[a, b, cls, args] = edge
        else:
            assert isinstance(edge, cls)
        return edge

    def dump(self):
        for name, obj in self.objects.items():
            print(obj.name, obj.type, obj.summary or '')
            for key, edge in self.edges.items():
                a, b = key[:2]
                if a is obj:
                    print(' --', edge.summary, '->', b.name)
                if b is obj:
                    print(' <-', edge.summary, '--', a.name)


def main(repo_path):
    g = Graph(repo_path)
    g.dump()


if __name__ == '__main__':
    main(sys.argv[1])
