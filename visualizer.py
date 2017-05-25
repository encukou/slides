# Hacky code to visualize a Git repo.
#
# Will crash on any nontrivial repo; use tho visualize very early history.

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
from kivy.core.window import Window

import pygit2


class VisualizationApp(App):
    def __init__(self):
        self.scale = 1
        super().__init__()
        self.visualization_widgets = {}
        self.edges = {}
        Clock.schedule_interval(self.update, 1/30)

    def set_repo(self):
        try:
            self.repo = pygit2.Repository('/tmp/testrepo')
        except KeyError:
            pass

    def build(self):
        self.layout = RelativeLayout()
        self.edge_widget = Widget()
        self.layout.add_widget(self.edge_widget)

        Clock.schedule_interval(lambda t: self.rescan(), 2)

        kbd = Window.request_keyboard(lambda: None, self.edge_widget, 'text')
        kbd.bind(on_key_down=self._on_keyboard_down)

        self.option_widgets = []
        # Finding objects to show
        self.add_option('a', 'all', 'All', (1, 1, 1))
        self.add_option('i', 'index', 'Idx', (1, 1/2, 1))
        self.add_option('f', 'list-refs', 'reF', (1/2, 1, 1))
        self.add_option('l', 'reflog', 'Log', (1, 1/2, 1/2), default=False)
        # Filer shown objects
        self.add_option('b', 'blobs', 'Blb', (1/2, 1/2, 1/2))
        self.add_option('t', 'trees', 'Tre', (1/2, 1, 1/2))
        self.add_option('c', 'commits', 'Com', (1/2, 1/2, 1))
        self.add_option('r', 'refs', 'Ref', (1/2, 1, 1), default=False)

        return self.layout

    def add_option(self, shortcut, ident, name, color, default=True):
        self.options[ident] = default
        widget = OptionWidget(
            self, shortcut, ident, name, color,
            pos=(0, 20 * len(self.option_widgets)),
        )
        self.option_widgets.append(widget)
        self.layout.add_widget(widget)

    def add_object_widget(self, blob):
        widget = ObjectWidget(
            blob,
            x=self.layout.width/2, y=self.layout.height/2,
        )
        widget.scale = self.scale
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
                    blob.x += fx * t * self.scale ** 2
                    blob.y += fy * t * self.scale ** 2

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
        dx = (obj.x - obj2.x) / self.scale
        dy = (obj.y - obj2.y) / self.scale
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
        try:
            self.repo
        except AttributeError:
            self.set_repo()
            try:
                self.repo
            except AttributeError:
                print('no repo')
                return

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
            if isinstance(obj, pygit2.Commit) and not self.options['commits']:
                return
            if isinstance(obj, pygit2.Tree) and not self.options['trees']:
                return
            if isinstance(obj, pygit2.Blob) and not self.options['blobs']:
                return

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
                    if _scan(child):
                        _add_edge(TreeContentEdge, obj.hex, child.hex)
            elif isinstance(obj, pygit2.Commit):
                if _scan(obj.tree):
                    _add_edge(CommitTreeEdge, obj.hex, obj.tree.hex)
                for parent in obj.parents:
                    if _scan(parent):
                        _add_edge(CommitParentEdge, obj.hex, parent.hex)

            return _reach(self.visualization_widgets[obj.hex])

        def _scan_ref(ref_name):
            try:
                ref = self.repo.lookup_reference(ref_name)
            except (KeyError, ValueError):
                return

            if self.options['refs']:
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

            if self.options['refs']:
                if target_widget:
                    _add_edge(RefEdge, ref.name, target_widget.name)


                if self.options['reflog']:
                    for item in ref.log():
                        if item.oid_old != pygit2.Oid(hex='0'*40):
                            target_widget = _scan(self.repo[item.oid_old])
                            if target_widget:
                                _add_edge(RefLogEdge, ref.name, target_widget.name)

                return _reach(self.visualization_widgets[ref.name])

        _scan_ref('HEAD')

        if self.options['index']:
            for entry in self.repo.index:
                _scan(self.repo[entry.id])

        if self.options['all']:
            for oid in self.repo:
                _scan(self.repo[oid])

        if self.options['list-refs']:
            for ref in self.repo.listall_references():
                _scan_ref(ref)

        for old_id in unvisited_widgets:
             self.visualization_widgets[old_id].fade_out()
             del self.visualization_widgets[old_id]
             #self.visualization_widgets[old_id].reachable = False

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

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        num, letter = keycode
        if letter in ('=', '+'):
            self.update_scale(1.1)
        if letter in ('-', '_'):
            self.update_scale(0.9)
        for option in self.option_widgets:
            if option.shortcut == letter:
                option.toggle()

    def update_scale(self, factor):
        self.scale *= factor
        for widget in self.visualization_widgets.values():
            widget.scale = self.scale


class VisualizationWidget(Scatter):
    size_hint = None, None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print(keyboard, keycode, text, modifiers)

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.reachable = False

        self.name_label = Label(
            text=name,
            x=-self.width/2, y=-self.height/2, size=self.size,
            color=(*self.text_color, 0),
            valign='center', halign='center',
            font_name='LiberationMono-Bold',
        )
        self.add_widget(self.name_label)
        Animation(color=(*self.text_color, 1), duration=0.7).start(self.name_label)

    def fade_out(self, *args):
        self.parent.remove_widget(self)


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
            s = r * 2
            graphics.Color(0, 0, 0, 0.95)
            self.bk_ellipse = graphics.Ellipse(pos=(-r, -r), size=(s, s))

        self.bg_ellipse.angle_end = 0
        Animation(angle_end=360, duration=0.5).start(self.bg_ellipse)

    def collide_point(self, x, y):
        r = self.size[0]/2
        x +=  - self.pos[0]
        y +=  - self.pos[1]
        return x**2 + y**2 < r ** 2

    def fade_out(self, *args):
        Animation(color=(*self.text_color, 0), duration=0.2).start(self.name_label)
        anim = Animation(angle_start=360, duration=0.3)
        anim.start(self.bg_ellipse)
        anim.bind(on_complete=lambda *a: self.parent.remove_widget(self))


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

    def fade_out(self, *args):
        anim = Animation(size=(self.width, 0), duration=0.1)
        anim.start(self.bg_rect)
        anim.bind(on_complete=lambda *a: self.parent.remove_widget(self))


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

class RefLogEdge(Edge):
    color = 1, 1/2, 1/2

    def force(self, distance, ndx, ndy, dx, dy):
        return -ndx * 5 + 5, -ndy * 5 + 5


class OptionWidget(Widget):
    size_hint = None, None

    def __init__(self, app, shortcut, ident, name, color, **kwargs):
        kwargs.setdefault('size', (50, 20))
        super().__init__(**kwargs)
        self.app = app
        self.shortcut = shortcut
        self.ident = ident
        self.name = name
        self.color = color

        print(self.pos, kwargs)

        with self.canvas.before:
            self.bg_color = graphics.Color(1, 1, 1, 1)
            self.bg_rect = graphics.Rectangle(pos=self.pos, size=self.size)

        self.label = Label(
            text=self.name,
            pos=(10, self.y), height=self.height,
            color=(*self.color, 1),
            valign='center', halign='right',
            font_name='LiberationMono-Bold',
            size_hint=(1.0, 1.0),
        )
        self.label.bind(texture_size=self.label.setter('size'))
        self.add_widget(self.label)
        self.set_appearance()

    def set_appearance(self):
        if self.app.options[self.ident]:
            self.bg_color.rgba = *self.color, 1/2
            self.label.color = 0, 0, 0, 1
        else:
            self.bg_color.rgba = 0, 0, 0, 0
            self.label.color = *self.color, 1/2

    def toggle(self):
        self.app.options[self.ident] = not self.app.options[self.ident]
        self.set_appearance()
        self.app.rescan()


VisualizationApp().run()
