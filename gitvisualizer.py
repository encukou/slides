from __future__ import print_function, unicode_literals, division

import subprocess
import sys
from math import pi, sin, cos

from pyglet import gl
from gillcup_graphics import Layer, GraphicsObject, Window, RealtimeClock, run

tau = 2 * pi

def run_git(*command):
    print(command)
    process = subprocess.Popen(('git',) + command, stdout=subprocess.PIPE)
    return process.stdout


visclass_by_type = {}
def visclass(cls):
    visclass_by_type[cls.type] = cls
    return cls


def circle(x, y, radius):
    iterations = int(tau * radius) * 2
    s = sin(tau / iterations)
    c = cos(tau / iterations)
    gl.glBegin(gl.GL_TRIANGLE_FAN)
    gl.glVertex2f(x, y)
    dx, dy = radius, 0
    for i in range(iterations + 1):
        gl.glVertex2f(x + dx, y + dy)
        dx, dy = (dx * c - dy * s), (dy * c + dx * s)
    gl.glEnd()


class Object(GraphicsObject):
    def __init__(self, graph, name):
        GraphicsObject.__init__(self)
        self.graph = graph
        self.name = name

        self.radius = 10
        self.pointers_in = set()
        self.drag_starts = {}

    def draw(self, **kwargs):
        if self.pointers_in:
            gl.glColor4f(1, 0, 0, 1)
        else:
            gl.glColor4f(1, 1, 1, 1)
        circle(self.x, self.y, self.radius + 2)
        gl.glColor4f(0, 0, 0, 1)
        circle(self.x, self.y, self.radius)

    def hit_test(self, x, y, z):
        return x ** 2 + y ** 2 < self.radius ** 2

    def on_pointer_motion(self, pointer, x, y, z, **kwargs):
        self.pointers_in.add(pointer)
        return True

    def on_pointer_leave(self, pointer, x, y, z, **kwargs):
        self.pointers_in.remove(pointer)
        return True

    def on_pointer_press(self, pointer, x, y, z, button, **kwargs):
        self.drag_starts[pointer, button] = x, y
        return True

    def on_pointer_drag(self, pointer, x, y, z, button, **kwargs):
        start_x, start_y = self.drag_starts[pointer, button]
        self.position = self.x + x - start_x, self.y + y - start_y
        return True

    def on_pointer_release(self, pointer, x, y, z, button, **kwargs):
        del self.drag_starts[pointer, button]
        return True


@visclass
class Commit(Object):
    type = 'commit'
    def __init__(self, graph, sha):
        Object.__init__(self, graph, sha)
        self.parents = []
        stdout = run_git('cat-file', sha, '-p')
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
class Tree(Object):
    type = 'tree'
    summary = None
    def __init__(self, graph, sha):
        Object.__init__(self, graph, sha)
        self.children = {}
        for line in run_git('cat-file', sha, '-p'):
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
class Blob(Object):
    type = 'blob'
    summary = None
    def __init__(self, graph, sha):
        Object.__init__(self, graph, sha)
        self.contents = run_git('cat-file', sha, '-p').read()


class Ref(Object):
    type = 'ref'
    def __init__(self, graph, name, target):
        Object.__init__(self, graph, name)
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


class Graph(Layer):
    def __init__(self, repo_path, clock):
        Layer.__init__(self)
        self.repo_path = repo_path
        self.objects = {}
        self.edges = {}
        self.update()

    def update(self):
        self.lingering = self.objects
        self.objects = {}
        for line in run_git('show-ref'):
            sha, name = line.strip().split()
            obj = self.add_object(sha)
            self.add_ref(name, obj)
        for line in run_git('symbolic-ref', 'HEAD'):
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
            for line in run_git('rev-parse', name):
                target = self.add_object(line.strip())
        assert target is not None
        return Ref(self, name, target)

    @_add
    def add_object(self, sha):
        obj_type = run_git('cat-file', sha, '-t').read().strip()
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

    @property
    def children(self):
        return self.objects.values()

    @children.setter
    def children(self, v):
        pass


class GVWindow(Window):
    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)
        layer = self.layer
        layer.position = width / 2, height / 2


def main(repo_path):
    clock = RealtimeClock()
    g = Graph(repo_path, clock)
    g.dump()

    GVWindow(g, width=400, height=400, resizable=True)
    run()


if __name__ == '__main__':
    main(sys.argv[1])
