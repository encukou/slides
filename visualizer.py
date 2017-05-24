import random
import math

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
from kivy import graphics
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.clock import Clock

import pygit2


class VisualizationApp(App):
    def __init__(self):
        super().__init__()
        self.visualization_widgets = {}
        self.edges = {}
        Clock.schedule_interval(self.update, 1/30)
        self.repo = pygit2.Repository('/tmp/testrepo')

    def build(self):
        self.layout = RelativeLayout()
        self.edge_widget = Widget()
        self.layout.add_widget(self.edge_widget)

        self.rescan()

        return self.layout

    def add_object_widget(self, blob):
        widget = ObjectWidget(
            blob,
            x=self.layout.width/2, y=self.layout.height/2,
        )
        self.layout.add_widget(widget, 0)
        self.visualization_widgets[blob.hex] = widget
        return widget

    def add_ref_widget(self, ref):
        widget = RefWidget(
            ref,
            x=self.layout.width/2, y=self.layout.height/2,
        )
        self.layout.add_widget(widget, 0)
        self.visualization_widgets[ref.name] = widget
        return widget

    def add_edge(self, cls, a, b):
        edge = cls(
            self.visualization_widgets[a], self.visualization_widgets[b],
            self.edge_widget.canvas,
        )
        self.edges.setdefault((a, b), []).append(edge)
        return edge

    def update(self, t):
        for blob in self.visualization_widgets.values():
            for other in self.visualization_widgets.values():
                fx, fy = self.interaction(blob, other)

                # Attraction to center
                fx += ((self.layout.width/2 - blob.x) / self.layout.width * 10) ** 3
                fy += ((self.layout.height/2 - blob.y) / self.layout.height * 10) ** 3

                if not blob._touches:
                    blob.x += fx * t
                    blob.y += fy * t

                if blob.x < blob.radius:
                    blob.x = blob.radius
                if blob.y < blob.radius:
                    blob.y = blob.radius
                if blob.x > self.layout.width - blob.radius:
                    blob.x = self.layout.width - blob.radius
                if blob.y > self.layout.height - blob.radius:
                    blob.y = self.layout.height - blob.radius

    def interaction(self, obj, obj2):
        fx = fy = 0
        if obj is obj2:
            return 0, 0
        dx = obj.x - obj2.x
        dy = obj.y - obj2.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
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

        for edge in self.edges.get((obj.name, obj2.name), []):
            dfx, dfy = edge.force(distance, ndx, ndy, dx, dy)
            fx += dfx
            fy += dfy
        for edge in self.edges.get((obj2.name, obj.name), []):
            dfx, dfy = edge.force(distance, -ndx, -ndy, -dx, -dy)
            fx -= dfx
            fy -= dfy
            #if obj2.reachable:
            #    obj.reachable = max(obj.reachable, obj2.reachable) * 0.9

        return fx, fy

    def rescan(self):
        self.edge_widget.canvas.before.clear()
        self.edges = {}

        unvisited = set(self.visualization_widgets)
        visited = set()

        def _scan(obj):
            if obj.hex in visited:
                return self.visualization_widgets[obj.hex]
            else:
                visited.add(obj.hex)

            if obj.hex in unvisited:
                unvisited.discard(obj.hex)
            else:
                self.add_object_widget(obj)

            if isinstance(obj, pygit2.Tree):
                for entry in obj:
                    child = self.repo[entry.hex]
                    _scan(child)
                    self.add_edge(TreeContentEdge, obj.hex, child.hex)
            elif isinstance(obj, pygit2.Commit):
                _scan(obj.tree)
                self.add_edge(CommitTreeEdge, obj.hex, obj.tree.hex)
                for parent in obj.parents:
                    _scan(parent)
                    self.add_edge(CommitParentEdge, obj.hex, parent.hex)

            return self.visualization_widgets[obj.hex]

        def _scan_ref(ref_name):
            try:
                ref = self.repo.lookup_reference(ref_name)
            except (KeyError, ValueError):
                return

            if ref.name in visited:
                return self.visualization_widgets[ref.name]
            else:
                visited.add(ref.name)

            if ref.name in unvisited:
                unvisited.discard(ref.name)
            else:
                self.add_ref_widget(ref)

            target = ref.target
            if isinstance(target, str):
                target_widget = _scan_ref(target)
            else:
                target_widget = _scan(self.repo[target])
            if target_widget:
                self.add_edge(RefEdge,
                              ref.name,
                              target_widget.name)

            return self.visualization_widgets[ref.name]

        _scan_ref('HEAD')

        for blob in self.repo.index:
            _scan(blob)

        for old_id in unvisited:
            raise ValueError('old object')


class VisualizationWidget(Scatter):
    size_hint = None, None

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)

        label = Label(
            text=name,
            x=-self.width/2, y=-self.height/2, size=self.size,
            color=(0, 0, 0, 0),
            valign='center', halign='center',
            font_name='LiberationMono-Bold',
        )
        self.add_widget(label)
        Animation(color=(0, 0, 0, 1), duration=0.1).start(label)


class ObjectWidget(VisualizationWidget):
    def __init__(self, blob, **kwargs):
        kwargs.setdefault('size', (50, 50))
        super().__init__(blob.hex[:5], **kwargs)
        self.name = blob.hex

        if isinstance(blob, pygit2.Tree):
            color = 1/2, 1, 1/2
        elif isinstance(blob, pygit2.Blob):
            color = 1/2, 1/2, 1/2
        elif isinstance(blob, pygit2.Commit):
            color = 1/2, 1/2, 1
        else:
            color = 1, 1/2, 1/2

        r = self.radius = self.width / 2

        with self.canvas.before:
            graphics.Color(*color)
            self.bg_ellipse = graphics.Ellipse(pos=(-r, -r), size=self.size)

        self.bg_ellipse.angle_end = 0
        Animation(angle_end=360, duration=0.2).start(self.bg_ellipse)

    def collide_point(self, x, y):
        r = self.size[0]/2
        x +=  - self.pos[0]
        y +=  - self.pos[1]
        return x**2 + y**2 < r ** 2


class RefWidget(VisualizationWidget):
    def __init__(self, ref, **kwargs):
        kwargs.setdefault('size', (80, 20))
        super().__init__(ref.shorthand, **kwargs)
        self.name = ref.name

        color = 1/2, 1, 1

        self.radius = self.height / 2

        pos = -self.width/2, -self.height/2
        with self.canvas.before:
            graphics.Color(*color)
            self.bg_rect = graphics.Rectangle(pos=pos, size=self.size)

        self.bg_rect.size = self.width, 0
        Animation(size=self.size, duration=0.2).start(self.bg_rect)


    def collide_point(self, x, y):
        r = self.size[0]/2
        x +=  - self.pos[0]
        y +=  - self.pos[1]
        return x**2 + y**2 < r ** 2


class Edge:
    color = 1, 1, 1

    size_hint = None, None
    def __init__(self, a, b, canvas):
        self.a = a
        self.b = b
        self.canvas = canvas

        a.bind(pos=self.update_points)
        b.bind(pos=self.update_points)

        with self.canvas.before:
            graphics.Color(*self.color, 1)
            self.line = graphics.Line(
                points=[a.x, a.y, b.x, b.y],
            )

    def update_points(self, x, y):
        self.line.points = [self.a.x, self.a.y, self.b.x, self.b.y]

    def force(self, distance, ndx, ndy, dx, dy):
        return -ndx * 30, -ndy * 30

class TreeContentEdge(Edge):
    color = 1/2, 1, 1/2

    def force(self, distance, ndx, ndy, dx, dy):
        return -ndx * 50, -ndy * 50 + 30

class CommitTreeEdge(Edge):
    color = 1, 1, 1

    def force(self, distance, ndx, ndy, dx, dy):
        return -ndx * 40, -ndy * 40 + 20

class CommitParentEdge(Edge):
    color = 1/2, 1/2, 1

    def force(self, distance, ndx, ndy, dx, dy):
        return -ndx * 40 - 40, -ndy * 40 + 10

class RefEdge(Edge):
    color = 1/2, 1, 1

    def force(self, distance, ndx, ndy, dx, dy):
        return -ndx * 50, -ndy * 50 + 30


VisualizationApp().run()
