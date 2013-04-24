import subprocess
import sys
import io


def run(*command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    return io.TextIOWrapper(process.stdout, encoding='utf-8')


visclass_by_type = {}
def visclass(cls):
    visclass_by_type[cls.type] = cls
    return cls


@visclass
class Commit(object):
    type = 'commit'
    def __init__(self, graph, sha):
        self.graph = graph
        self.sha = sha
        for line in run('git', 'cat-file', sha, '-p'):
            line = line.strip()
            name, space, value = line.partition(' ')
            if not space:
                break
            if name == 'tree':
                self.tree = self.graph.add_object(value)
            elif name == 'author':
                self.author = value
            elif name == 'committer':
                self.committer = value
            else:
                print('Warning: unknown commit line:', line)

@visclass
class Tree(object):
    type = 'tree'
    def __init__(self, graph, sha):
        self.graph = graph
        self.sha = sha
        self.children = {}
        for line in run('git', 'cat-file', sha, '-p'):
            line = line.strip()
            info, tab, name = line.partition('\t')
            self.add_child(info, name)
    
    def add_child(self, info, name):
        mode, type, sha = info.split(' ')
        self.children[name] = self.graph.add_object(sha)


@visclass
class Blob(object):
    type = 'blob'
    def __init__(self, graph, sha):
        self.graph = graph
        self.sha = sha
        self.contents = run('git', 'cat-file', sha, '-p').read()


class Graph(object):
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.objects = {}
        self.edges = set()
        self.update()

    def update(self):
        self.lingering = self.objects
        self.objects = {}
        for line in run('git', 'show-ref', '--head'):
            sha, name = line.strip().split()
            self.add_object(sha)

    def add_object(self, sha):
        try:
            obj = self.objects[sha]
        except KeyError:
            try:
                obj = self.lingering[sha]
                del self.lingering[sha]
            except KeyError:
                obj_type = run('git', 'cat-file', sha, '-t').read().strip()
                obj = visclass_by_type[obj_type](self, sha)
        self.objects[sha] = obj
        return obj

    def dump(self):
        for sha, obj in self.objects.items():
            print(obj.sha, obj.type)


def main(repo_path):
    g = Graph(repo_path)
    g.dump()


if __name__ == '__main__':
    main(sys.argv[1])
