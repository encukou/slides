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

        Clock.schedule_interval(lambda t: self.rescan(), 2)

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
        try:
            return self.edges[a, b]
        except KeyError:
            edge = cls(
                self.visualization_widgets[a], self.visualization_widgets[b],
                self.edge_widget.canvas,
            )
            self.edges[a, b] = edge
            return edge

    def update(self, t):
        for blob in self.visualization_widgets.values():
            for other in self.visualization_widgets.values():
                fx, fy = self.interaction(blob, other)

                # Attraction to center
                cx = ((self.layout.width/2 - blob.x) / self.layout.width * 10)
                cy = ((self.layout.height/2 - blob.y) / self.layout.height * 10)
                if blob.reachable:
                    fx += cx ** 3
                    fy += cy ** 3
                else:
                    fx -= cx * 30
                    fy -= cy * 30

                if not blob._touches:
                    blob.x += fx * t
                    blob.y += fy * t

                if blob.reachable:
                    threshold = blob.radius
                else:
                    threshold = -blob.radius - 5
                if blob.x < threshold:
                    blob.x = threshold
                if blob.y < threshold:
                    blob.y = threshold
                if blob.x > self.layout.width - threshold:
                    blob.x = self.layout.width - threshold
                if blob.y > self.layout.height - threshold:
                    blob.y = self.layout.height - threshold

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

        edge = self.edges.get((obj.name, obj2.name))
        if edge:
            dfx, dfy = edge.force(distance, ndx, ndy, dx, dy)
            fx += dfx
            fy += dfy
        edge = self.edges.get((obj2.name, obj.name))
        if edge:
            dfx, dfy = edge.force(distance, -ndx, -ndy, -dx, -dy)
            fx -= dfx
            fy -= dfy
            #if obj2.reachable:
            #    obj.reachable = max(obj.reachable, obj2.reachable) * 0.9

        return fx, fy

    def rescan(self):
        print('rescan')
        #self.edge_widget.canvas.before.clear()

        unvisited_widgets = set(self.visualization_widgets)
        unvisited_edges = set(self.edges)
        visited = set()
        to_position = set()

        def _reach(widget):
            if not widget.reachable:
                to_position.add(widget)
            return widget

        def _add_edge(cls, a, b):
            edge = self.add_edge(cls, a, b)
            unvisited_edges.discard((a, b))
            return edge

        def _scan(obj):
            if obj.hex in visited:
                return _reach(self.visualization_widgets[obj.hex])
            else:
                visited.add(obj.hex)

            if obj.hex in unvisited_widgets:
                unvisited_widgets.discard(obj.hex)
            else:
                self.add_object_widget(obj)

            if isinstance(obj, pygit2.Tree):
                for entry in obj:
                    child = self.repo[entry.hex]
                    _scan(child)
                    _add_edge(TreeContentEdge, obj.hex, child.hex)
            elif isinstance(obj, pygit2.Commit):
                _scan(obj.tree)
                _add_edge(CommitTreeEdge, obj.hex, obj.tree.hex)
                for parent in obj.parents:
                    _scan(parent)
                    _add_edge(CommitParentEdge, obj.hex, parent.hex)

            return _reach(self.visualization_widgets[obj.hex])

        def _scan_ref(ref_name):
            try:
                ref = self.repo.lookup_reference(ref_name)
            except (KeyError, ValueError):
                return

            if ref.name in visited:
                return _reach(self.visualization_widgets[ref.name])
            else:
                visited.add(ref.name)

            if ref.name in unvisited_widgets:
                unvisited_widgets.discard(ref.name)
            else:
                self.add_ref_widget(ref)

            target = ref.target
            if isinstance(target, str):
                target_widget = _scan_ref(target)
            else:
                target_widget = _scan(self.repo[target])
            if target_widget:
                _add_edge(RefEdge, ref.name, target_widget.name)

            return _reach(self.visualization_widgets[ref.name])

        _scan_ref('HEAD')

        for entry in self.repo.index:
            _scan(self.repo[entry.id])

        for old_id in unvisited_widgets:
             self.visualization_widgets[old_id].reachable = False

        for old_name in unvisited_edges:
            self.edges[old_name].remove()
            self.edges.pop(old_name)

        for widget in to_position:
            widget.reachable = True
            positions = []
            for other in self.visualization_widgets:
                edge = self.edges.get((widget.name, other))
                if edge:
                    fx, fy = edge.force(0, 0, 0, 0, 0)
                    positions.append((edge.b.x + fx*5, edge.b.y + fy*5))
                edge = self.edges.get((other, widget.name))
                if edge:
                    fx, fy = edge.force(0, 0, 0, 0, 0)
                    positions.append((edge.a.x - fx*5, edge.a.y - fy*5))
            if not positions:
                widget.x = self.layout.width / 2
                widget.y = self.layout.height / 2
            else:
                widget.x = sum(p[0] for p in positions) / len(positions)
                widget.y = sum(p[1] for p in positions) / len(positions)


class VisualizationWidget(Scatter):
    size_hint = None, None

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.reachable = False

        label = Label(
            text=name,
            x=-self.width/2, y=-self.height/2, size=self.size,
            color=(*self.text_color, 0),
            valign='center', halign='center',
            font_name='LiberationMono-Bold',
        )
        self.add_widget(label)
        Animation(color=(*self.text_color, 1), duration=0.7).start(label)


class ObjectWidget(VisualizationWidget):
    def __init__(self, blob, **kwargs):
        kwargs.setdefault('size', (50, 50))


        if isinstance(blob, pygit2.Tree):
            self.text_color = 1/2, 1, 1/2
        elif isinstance(blob, pygit2.Blob):
            self.text_color = 1/2, 1/2, 1/2
        elif isinstance(blob, pygit2.Commit):
            self.text_color = 1/2, 1/2, 1
        else:
            self.text_color = 1, 1/2, 1/2

        super().__init__(blob.hex[:5], **kwargs)
        self.name = blob.hex

        r = self.radius = self.width / 2

        with self.canvas.before:
            graphics.Color(*self.text_color)
            s = r * 2 + 4
            self.bg_ellipse = graphics.Ellipse(pos=(-r-2, -r-2), size=(s, s))
            graphics.Color(0, 0, 0, 0.95)
            s = r * 2
            self.bk_ellipse = graphics.Ellipse(pos=(-r, -r), size=(s, s))

        self.bg_ellipse.angle_end = 0
        Animation(angle_end=360, duration=0.5).start(self.bg_ellipse)

    def collide_point(self, x, y):
        r = self.size[0]/2
        x +=  - self.pos[0]
        y +=  - self.pos[1]
        return x**2 + y**2 < r ** 2


class RefWidget(VisualizationWidget):
    def __init__(self, ref, **kwargs):
        kwargs.setdefault('size', (80, 20))
        color = 1/2, 1, 1
        self.text_color = 0, 0, 0
        super().__init__(ref.shorthand, **kwargs)
        self.name = ref.name

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
            self.color_instruction = graphics.Color(*self.color, 0)
            self.line = graphics.Line(
                points=[a.x, a.y, b.x, b.y],
                width=1.1,
            )

        anim = Animation(rgba=(*self.color, 0), duration=0.1)
        anim += Animation(rgba=(*self.color, 1), duration=0.5)
        anim.start(self.color_instruction)

    def remove(self):
        self.canvas.before.remove(self.color_instruction)
        self.canvas.before.remove(self.line)

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
        return -ndx * 50 + 10, -ndy * 50 + 30


VisualizationApp().run()
