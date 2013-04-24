#! /usr/bin/env python2
"""Simple near-realtime visualization of a Git repository

This only does what it needs to do for my presentation.
It was written as a brainstorm of what this needs to do, so there was not much
design involved. Or refactoring. It somehow hangs together, though, and only
took half a day to make.
Don't judge me by the quality :)

It's meant for small repos with a few commits only.
DO NOT run this on a big repo. It's reeeally inefficient (and it would be
extremely confusing on a complicated repo, too).
"""

from __future__ import print_function, unicode_literals, division

import subprocess
import sys
import os
from math import pi, sin, cos, sqrt
import random

from pyglet import gl
from gillcup_graphics import (Layer, GraphicsObject, Window, RealtimeClock,
                              Text,run)

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


def rectangle(x1, y1, x2, y2):
    gl.glBegin(gl.GL_TRIANGLE_STRIP)
    gl.glVertex2f(x1, y1)
    gl.glVertex2f(x1, y2)
    gl.glVertex2f(x2, y1)
    gl.glVertex2f(x2, y2)
    gl.glEnd()


class Object(GraphicsObject):
    short_name = None
    def __init__(self, graph, name):
        GraphicsObject.__init__(self, height=15)
        self.graph = graph
        self.name = name

        self.radius = 15
        self.pointers_in = set()
        self.drag_starts = {}

        self.vx = self.vy = 0

        self.reachable = 0

        self.text_obj = Text(None, '')
        self.set_size()

    def set_size(self):
        self.size = self.radius * 2, self.radius * 2
        if self.short_name:
            self.width *= 2

    def add_children(self):
        pass

    def draw(self, **kwargs):
        if self.width > self.radius * 2:
            xes = [-self.width / 2 + self.radius, self.width / 2 - self.radius]
            gl.glColor3f(*self.color)
            rectangle(-self.width / 2 + self.radius, -self.height / 2,
                      self.width / 2 - self.radius, self.height / 2)
        else:
            xes = [0]
        for x in xes:
            gl.glColor3f(*self.color)
            circle(x, 0, self.radius)
            self.set_inner_color()
            circle(x, 0, self.radius - 2)
        if self.width > self.radius * 2:
            rectangle(-self.width / 2 + self.radius + 2, -self.height / 2 + 2,
                      self.width / 2 - self.radius - 2, self.height / 2 - 2)
        if self is self.graph.staging_tree:
            gl.glColor3f(*self.color)
            circle(self.width / 2, self.height / 2, 2)
        self.draw_text(**kwargs)

    def set_inner_color(self):
        if self.pointers_in:
            gl.glColor4f(1, 1, 1, 1)
        elif self.reachable:
            gl.glColor4f(0, self.reachable, 1, 1)
        else:
            gl.glColor4f(0, 0, 0, 1)

    def draw_text(self, **kwargs):
        if self.short_name:
            if self.reachable:
                self.text_obj.color = 0, 0, 0
            else:
                self.text_obj.color = 1, 1, 1
            self.text_obj.text = self.short_name
            self.text_obj.scale = (self.width / 2 - 4) / self.text_obj.width * 2
            self.text_obj.position = (
                -self.text_obj.width * self.text_obj.scale_x / 2,
                -self.text_obj.height * self.text_obj.scale_y * 1 / 3)
            self.text_obj.do_draw(**kwargs)

    def hit_test(self, x, y, z):
        if self.width > self.radius * 2:
            return (-self.width / 2 < x < self.width / 2 and
                    -self.height / 2 < y < self.height / 2)
        else:
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
    color = 1, 0, 1
    def __init__(self, graph, sha):
        Object.__init__(self, graph, sha)
        self.parents = []
        self.tree = None
        stdout = run_git('cat-file', sha, '-p')
        for line in stdout:
            line = line.strip()
            name, space, value = line.partition(' ')
            if not space:
                try:
                    self.message = u''.join(stdout)
                except UnicodeDecodeError:
                    self.message = '<Unicode>'
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

    def add_children(self):
        for parent in self.parents:
            self.graph.add_object(parent.name)
        if self.graph.show_trees and self.tree:
            self.graph.add_object(self.tree.name)

    @property
    def summary(self):
        return self.message.partition('\n')[0]

    @property
    def short_name(self):
        return self.name[:7]

@visclass
class Tree(Object):
    type = 'tree'
    color = 0, 1, 0
    summary = None
    def __init__(self, graph, sha):
        Object.__init__(self, graph, sha)
        self.children = {}
        for line in run_git('cat-file', sha, '-p'):
            line = line.strip()
            info, tab, filename = line.partition('\t')
            obj = self.add_child(info, filename)
            self.children[filename] = obj
            graph.add_edge(self, obj, TreeEntry, filename)

    def add_children(self):
        for child in self.children.values():
            self.graph.add_object(child.name)

    def add_child(self, info, name):
        mode, type, sha = info.split(' ')
        child = self.graph.add_object(sha)
        self.children[name] = child
        return child


@visclass
class Blob(Object):
    type = 'blob'
    summary = None
    color = 0, 1, 1
    def __init__(self, graph, sha):
        Object.__init__(self, graph, sha)
        self.contents = run_git('cat-file', sha, '-p').read()


class Ref(Object):
    type = 'ref'
    color = 1, 1, 0
    def __init__(self, graph, name, target):
        Object.__init__(self, graph, name)
        self._target = None
        self.target = target
        if name == 'HEAD':
            self.color = 1, 0.5, 0

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, new):
        if self._target:
            self.graph.edges[self, self._target] = {}
        self._target = new
        self.graph.add_edge(self, new, RefTarget)

    @property
    def summary(self):
        return self.target.name

    @property
    def short_name(self):
        return self.name.rpartition('/')[-1]


class Edge(GraphicsObject):
    def __init__(self, graph, a, b):
        GraphicsObject.__init__(self)
        self.graph = graph
        self.a = a
        self.b = b

    @property
    def summary(self):
        return self.type

    def draw(self, **kwargs):
        dx = self.a.x - self.b.x
        dy = self.a.y - self.b.y
        dist = sqrt(dx ** 2 + dy ** 2)
        if dist == 0:
            return
        width = 1
        cx = dy / dist * width
        cy = dx / dist * width
        gl.glBegin(gl.GL_TRIANGLE_STRIP)
        gl.glColor3f(*self.a.color)
        gl.glVertex2f(self.a.x + cx, self.a.y - cy)
        gl.glColor3f(*self.b.color)
        gl.glVertex2f(self.b.x + cx, self.b.y - cy)
        gl.glColor3f(*self.a.color)
        gl.glVertex2f(self.a.x - cx, self.a.y + cy)
        gl.glColor3f(*self.b.color)
        gl.glVertex2f(self.b.x - cx, self.b.y + cy)
        gl.glEnd()

    def hit_test(self, *args):
        return False

    def force(self, distance, ndx, ndy, dx, dy):
        return -ndx * 1e2, -ndy * 1e2


class CommitTree(Edge):
    type = 'tree'
    color = 0, 1, 0

    def force(self, distance, ndx, ndy, dx, dy):
        return (
            -ndx * (10 + distance ** 2 / 100),
            -ndy * (10 + distance ** 2 / 100) + distance)


class CommitParent(Edge):
    type = 'parent'
    color = 1, 0, 1

    def force(self, distance, ndx, ndy, dx, dy):
        if self.graph.show_trees:
            c = 1000
        else:
            c = 100
        return (
            -ndx * (10 + distance ** 2 / c) - 70,
            -ndy * (10 + distance ** 2 / c) + 70)


class RefTarget(Edge):
    type = 'target'
    color = 1, 1, 0

    def force(self, distance, ndx, ndy, dx, dy):
        return (
            -ndx * (10 + distance ** 2 / 100) + 20,
            -ndy * (10 + distance ** 2 / 100) + 20)


class TreeEntry(Edge):
    type = 'entry'
    color = 0, 1, 0
    def __init__(self, graph, a, b, filename):
        Edge.__init__(self, graph, a, b)
        self.filename = filename
        self.text_obj = Text(None, filename, scale=0.2)

    @property
    def summary(self):
        return './' + self.filename

    def force(self, distance, ndx, ndy, dx, dy):
        return (
            -ndx * (10 + distance ** 2 / 1000),
            -ndy * (10 + distance ** 2 / 1000) + 10 * len(self.a.children))

    def draw(self, **kwargs):
        super(TreeEntry, self).draw(**kwargs)
        if self.graph.show_filenames:
            try:
                children = sorted(self.a.children)
                w2 = (1 + children.index(self.filename)) / (len(children) + 1)
            except LookupError:
                w2 = 1 / 2
            w1 = 1 - w2
            self.text_obj.position = (
                self.a.x * w1 + self.b.x * w2 -
                    self.text_obj.width * self.text_obj.scale_x / 2,
                self.a.y * w1 + self.b.y * w2 -
                    self.text_obj.height * self.text_obj.scale_y / 2)
            if self.b.pointers_in:
                self.text_obj.color = 1, 1, 1
            else:
                self.text_obj.color = 0.5, 1, 1
            self.text_obj.do_draw(**kwargs)


class Graph(Layer):
    def __init__(self,  clock):
        Layer.__init__(self)

        self.show_trees = True
        self.show_refs = False
        self.show_filenames = True

        self.staging_tree = None

        self.clock = clock
        self.last_update_time = clock.time
        self.time = clock.time
        self.simulate = self.simulate
        clock.schedule_update_function(self.simulate)

        self.frozen = set()
        self.lingering = {}
        self.objects = {}
        self.edges = {}
        self.update()
        self.update()

    def update(self):
        try:
            del self._children
        except AttributeError:
            pass
        self.lingering.update(self.objects)
        self.frozen = set(self.objects)
        self.objects = {}
        for line in run_git('write-tree'):
            obj = self.add_object(line.strip())
            self.staging_tree = obj
        for line in run_git('show-ref'):
            sha, name = line.strip().split()
            obj = self.add_object(sha)
            ref = self.add_ref(name, obj)
            if ref:
                ref.target = obj
        for line in run_git('symbolic-ref', 'HEAD'):
            name = line.strip()
            ref = self.add_ref('HEAD')
            if ref:
                ref.target = self.add_ref(name)
            break
        else:
            ref = self.add_ref('HEAD')
            sha = run_git('rev-parse', 'HEAD').read().strip()
            obj = self.add_object(sha)
            if obj:
                ref.target = obj
        self.last_update_time = self.clock.time
        if set(self.objects) != self.frozen:
            for i in range(100):
                self.simulate(0.1)
        self.frozen = set()

    def _add(func):
        def adder(self, name, *args, **kwargs):
            try:
                obj = self.objects[name]
            except KeyError:
                try:
                    obj = self.lingering[name]
                except KeyError:
                    obj = func(self, name, *args, **kwargs)
                    if not obj:
                        return
                else:
                    del self.lingering[name]
                    obj.add_children()
            collection = self.objects
            if obj.type in ('tree', 'blob') and not self.show_trees:
                collection = self.lingering
            elif obj.type in ('ref') and not self.show_refs:
                collection = self.lingering
            collection[name] = obj
            return obj
        return adder

    @_add
    def add_ref(self, name, target=None):
        if target is None:
            for line in run_git('rev-parse', name):
                target = self.add_object(line.strip())
        if target is None:
            return
        return Ref(self, name, target)

    @_add
    def add_object(self, sha):
        obj_type = run_git('cat-file', sha, '-t').read().strip()
        try:
            visclass = visclass_by_type[obj_type]
        except KeyError:
            print('Warning: unknown object type:', obj_type, sha)
            return
        return visclass(self, sha)

    def add_edge(self, a, b, cls, *args):
        try:
            edge = self.edges[a, b][cls, args]
        except KeyError:
            edge = cls(self, a, b, *args)
            self.edges.setdefault((a, b), {})[cls, args] = edge
            for o1, o2 in ((a, b), (b, a)):
                if o1.position == (0, 0, 0):
                    o1.position = o2.position
                    dfx, dfy = self.interaction(o1, o2)
                    print(dfx, dfy, o1, o2)
                    o1.x += o2.x - dfx * 100
                    o1.y += o2.y - dfy * 100
                    print(o1.x, o1.y)
                    o1.vx += -dfx * 100
                    o1.vy += -dfy * 100
        else:
            assert isinstance(edge, cls)
        return edge

    def dump(self):
        for name, obj in self.objects.items():
            print(obj.name, obj.type, obj.summary or '')
            for (a, b), dct in self.edges.items():
                for junk, edge in dct.items():
                    if a is obj:
                        print(' --', edge.summary, '->', b.name)
                    if b is obj:
                        print(' <-', edge.summary, '--', a.name)

    @property
    def children(self):
        try:
            return self._children
        except AttributeError:
            self._children = []
            for (a, b), v in self.edges.items():
                if a.name in self.objects and b.name in self.objects:
                    self._children += v.values()
            self._children += self.objects.values()
        return self._children

    @children.setter
    def children(self, v):
        pass

    def interaction(self, obj, obj2):
        fx = fy = 0
        if obj is obj2:
            return 0, 0
        dx = obj.x - obj2.x
        dy = obj.y - obj2.y
        distance = sqrt(dx ** 2 + dy ** 2)
        if not distance:
            rx = random.random() - 0.5
            ry = random.random() - 0.5
            obj.x += rx * obj.radius * 5
            obj.y += ry * obj.radius * 5
            return 0, 0
        ndx = dx / distance
        ndy = dy / distance
        if distance < 20:
            fx += ndx * 1e3
            fy += ndy * 1e3
        else:
            # Repulsion
            repulsion = 1e7 / distance ** 3
            fx += ndx * repulsion
            fy += ndy * repulsion
        for edge in self.edges.get((obj, obj2), {}).values():
            dfx, dfy = edge.force(distance, ndx, ndy, dx, dy)
            fx += dfx
            fy += dfy
        for edge in self.edges.get((obj2, obj), {}).values():
            dfx, dfy = edge.force(distance, -ndx, -ndy, -dx, -dy)
            fx -= dfx
            fy -= dfy
            if obj2.reachable:
                obj.reachable = max(obj.reachable, obj2.reachable) * 0.9
        return fx, fy

    def simulate(self, dt=None):
        if dt is None:
            dt = self.clock.time - self.time
            dt *= 4
            if dt > 0.1:
                dt = 0.1
            self.time = self.clock.time
        cx = cy = 0
        objects = self.objects.values()
        for obj in objects:
            if obj.name in self.frozen:
                continue
            if not obj.pointers_in:
                obj.position = (
                    obj.x + obj.vx * dt,
                    obj.y + obj.vy * dt)
        for obj in objects:
            if obj.name in self.frozen:
                continue
            fx = fy = 0
            obj.reachable = 1 if obj.pointers_in else 0
            for obj2 in self.objects.values():
                dfx, dfy = self.interaction(obj, obj2)
                fx += dfx
                fy += dfy
            # "Gravity"
            fx -= obj.x / 5
            fy -= obj.y / 5
            # Force
            obj.vx += fx * dt
            obj.vy += fy * dt
            # Resistance
            obj.vx *= 0.9
            obj.vy *= 0.9

        if self.last_update_time + 1 < self.clock.time:
            self.update()


    def on_text(self, keyboard, text):
        if 't' in text.lower():
            self.show_trees = not self.show_trees
            self.update()
        if 'r' in text.lower():
            self.show_refs = not self.show_refs
            self.update()
        if 'f' in text.lower():
            self.show_filenames = not self.show_filenames
            self.update()
        if '+' in text.lower():
            self.scale = self.scale_x + 0.1
        if '-' in text.lower():
            self.scale = self.scale_x - 0.1

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
            self.scale = self.scale_x + scroll_x


class GVWindow(Window):
    def on_resize(self, width, height):
        super(Window, self).on_resize(width, height)
        layer = self.layer
        layer.position = width / 2, height / 2


def main():
    clock = RealtimeClock()
    g = Graph(clock)
    g.dump()

    GVWindow(g, width=400, height=400, resizable=True)
    run()


if __name__ == '__main__':
    os.chdir(sys.argv[1])
    main()
