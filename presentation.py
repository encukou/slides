from pathlib import Path
import inspect
import numpy
import datetime
import pyglet
import math
import traceback
import sys
import contextvars
import ctypes


draw_instructions_var = contextvars.ContextVar('draw_instructions_var')


class Array:
    def __init__(self, values):
        self.values = tuple(
            tuple(v if isinstance(v, Scalar) else Scalar(v) for v in row)
            for row in values
        )

    def to_numpy(self):
        return numpy.array(self.values, dtype=float)

    def __matmul__(self, other):
        return type(other)(self.to_numpy() @ other.to_numpy())

    def __enter__(self):
        draw_instructions_var.get().append((self._enter, (), {}))

    def _enter(self, passn, vert):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glLoadMatrixf(self.to_numpy().ctypes.data_as(ctypes.POINTER(ctypes.c_float)))

    def __exit__(self, *exc_info):
        draw_instructions_var.get().append((self._exit, (), {}))

    def _exit(self, passn, vert):
        pyglet.gl.glPopMatrix()

class Vector:
    def __init__(self, values):
        self.values = (
            tuple(v if isinstance(v, Scalar) else Scalar(v) for v in values)
        )

    def to_numpy(self):
        return numpy.array(self.values, dtype=float)

    def __repr__(self):
        return f'<{self.values}>'

    def __iter__(self):
        return iter(self.values)

    def __sub__(self, other):
        return Vector(a - b for a, b in zip(self, other))

    def __truediv__(self, other):
        return Vector(c / other for c in self)

    def __mul__(self, other):
        return Vector(c * other for c in self)

    def __abs__(self):
        return math.sqrt(sum(c**2 for c in self))

    def __neg__(self):
        return Vector(-c for c in self)

class Scalar:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)

    def __float__(self):
        return float(self.value)

    def __round__(self, n=0):
        return round(float(self.value), n)

    def __sub__(self, other):
        return self.value - other

    def __rsub__(self, other):
        return other - self.value

    def __add__(self, other):
        return self.value + other

    def __radd__(self, other):
        return other + self.value

    def __pow__(self, other):
        return self.value ** other

    def __truediv__(self, other):
        return self.value / other

    def __rtruediv__(self, other):
        return other / self.value

    def __mul__(self, other):
        return self.value * other

    def __rmul__(self, other):
        return other * self.value

    def __neg__(self):
        return -self.value

    def __format__(self, spec):
        return format(self.value, spec)

class sin(Scalar):
    def __init__(self, angle):
        self.angle = angle

    @property
    def value(self):
        return math.sin(self.angle)

class cos(Scalar):
    def __init__(self, angle):
        self.angle = angle

    @property
    def value(self):
        return math.cos(self.angle)

class _Draw:
    def _draw(self, func, *args, **kwargs):
        draw_instructions_var.get().append((func, args, kwargs))

    def __call__(self, point):
        self._draw(draw_point, point)

    def arrow(self, a, b):
        self._draw(draw_arrow, a, b)

    def line(self, a, b):
        self._draw(draw_line, a, b)

    def polygon(self, *points):
        self._draw(draw_polygon, *points)


draw = _Draw()

def _label(point, text):
    pyglet.gl.glColor4f(0.1, 0.2, 0.3, 1)
    x, y, *_ = point
    label.x = x + 3
    label.y = y + 5
    label.text = text
    label.size = 1/10
    label.color = 10, 150, 200, 150
    label.draw()


def _fmt(number):
    if abs(round(number) - number) < 0.01:
        return str(int(round(number)))
    return format(number, '.2f')

def draw_point(npass, vert, point):
    pyglet.gl.glColor4f(1, 1, 1, 1)
    pyglet.gl.glBegin(pyglet.gl.GL_POINTS)
    pyglet.gl.glVertex3f(*vert(point), 0)
    pyglet.gl.glEnd()

    if npass == 0:
        px, py, *rest = point
        frest = ''.join(', ' + _fmt(v) for v in rest)
        _label(vert(point), f'[{px:.2f}, {py:.2f}{frest}]')


def _arrow(vert, a, b):
    absab = abs(a - b)
    if absab:
        unit = (b - a) / (absab / 0.7)
        x1, y1, *_ = a
        x2, y2, *_ = bb = b - unit * 0.2
        x3, y3, *_ = unit
        pyglet.gl.glVertex3f(*vert(a), 0)
        pyglet.gl.glVertex3f(*vert(bb), 0)
        pyglet.gl.glVertex3f(*vert([x2-x3+y3/2, y2-y3-x3/2]), 0)
        pyglet.gl.glVertex3f(*vert(bb), 0)
        pyglet.gl.glVertex3f(*vert([x2-x3-y3/2, y2-y3+x3/2]), 0)
        pyglet.gl.glVertex3f(*vert(bb), 0)


def draw_arrow(npass, vert, a, b):
    if npass == 0:
        pyglet.gl.glColor4f(0.5, 0.5, 0.5, 1)
        pyglet.gl.glBegin(pyglet.gl.GL_LINES)
        _arrow(vert, a, b)
        pyglet.gl.glEnd()

    draw_point(npass, vert, a)
    draw_point(npass, vert, b)


def draw_line(npass, vert, a, b):
    if npass == 0:
        pyglet.gl.glColor4f(0.5, 0.5, 0.5, 1)
        pyglet.gl.glBegin(pyglet.gl.GL_LINES)
        pyglet.gl.glVertex3f(*vert(a), 0)
        pyglet.gl.glVertex3f(*vert(b), 0)
        pyglet.gl.glEnd()

    draw_point(npass, vert, a)
    draw_point(npass, vert, b)


def draw_polygon(npass, vert, *points):
    if npass == 0:
        pyglet.gl.glColor4f(0.5, 0.5, 0.5, 1)
        pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
        for point in (*points, points[0]):
            pyglet.gl.glVertex3f(*vert(point), 0)
        pyglet.gl.glEnd()

    for point in points:
        draw_point(npass, vert, point)


label = pyglet.text.Label(font_size=18, font_name='Mali')


class FunkyNamespace:
    def __init__(self):
        self.dict = {}

    def __setitem__(self, key, value):
        self.dict[key] = value
        if isinstance(value, Scalar):
            print(key, value)

    def __getitem__(self, key):
        return self.dict[key]


class Presentation:
    def __init__(self):
        self.demo_path = Path('demo.py')
        self.last_mtime = 0
        self.draw_instructions = []

    def draw(self, window):
        window.clear()
        def vert(point):
            x, y, *rest = point
            if len(rest) > 1:
                x *= rest[1]
                y *= rest[1]
            return x * 20, y * 20
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(window.width/2, window.height/2, 0)
        pyglet.gl.glPointSize(6)
        pyglet.gl.glEnable(pyglet.gl.GL_POINT_SMOOTH)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

        pyglet.gl.glColor4f(0.5, 0.6, 0.9, 0.25)
        pyglet.gl.glBegin(pyglet.gl.GL_LINES)
        for i in (*range(-10, 0), *range(1, 11)):
            pyglet.gl.glVertex3f(*vert([-10, i]), 0)
            pyglet.gl.glVertex3f(*vert([10, i]), 0)
            pyglet.gl.glVertex3f(*vert([i, -10]), 0)
            pyglet.gl.glVertex3f(*vert([i, 10]), 0)
        pyglet.gl.glEnd()
        pyglet.gl.glColor4f(0.5, 0.6, 0.9, 0.5)
        pyglet.gl.glBegin(pyglet.gl.GL_LINES)
        _arrow(vert, Vector([-10, 0]), Vector([11, 0]))
        _arrow(vert, Vector([0, -10]), Vector([0, 11]))
        pyglet.gl.glEnd()
        for x, y, n in (11, -0.4, 'x'), (-0.4, 11, 'y'):
            _label(vert([x, y]), n)

        for func, args, kwargs in self.draw_instructions:
            func(0, vert, *args, **kwargs)
        for func, args, kwargs in self.draw_instructions:
            func(1, vert, *args, **kwargs)

    def tick(self, dt):
        mtime = self.demo_path.stat().st_mtime
        if mtime != self.last_mtime:
            self.last_mtime = mtime
            print('\x1b[2J\x1b[;H', end='')
            print('Reload:', datetime.datetime.fromtimestamp(mtime))
            draw_instructions = []
            token = draw_instructions_var.set(draw_instructions)
            try:
                demo_ns = FunkyNamespace()
                try:
                    exec(self.demo_path.read_text(), demo_ns.dict, demo_ns)
                except Exception as e:
                    traceback.print_exc()
                    self.draw_instructions = []
                else:
                    self.draw_instructions = draw_instructions
            finally:
                draw_instructions_var.reset(token)


if __name__ == '__main__':
    sys.modules['presentation'] = sys.modules['__main__']
    presentation = Presentation()
    presentation.tick(0)

    window = pyglet.window.Window(resizable=True, caption='Diagram')
    window.set_location(1000, 300)

    fps_display = pyglet.clock.ClockDisplay()

    @window.event
    def on_draw():
        presentation.draw(window)
        fps_display.draw()

    pyglet.clock.schedule_interval(presentation.tick, 1/30)

    pyglet.app.run()
