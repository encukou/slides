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
operations_var = contextvars.ContextVar('operations_var')


class Array:
    def __init__(self, values):
        self.values = tuple(
            tuple(v if isinstance(v, Scalar) else Scalar(v) for v in row)
            for row in values
        )

    def to_numpy(self):
        return numpy.array(self.values, dtype=float)

    def __matmul__(self, other):
        result = type(other)(self.to_numpy() @ other.to_numpy())
        operations = operations_var.get(None)
        if operations:
            operations.append(MatmulOperation(self, other, result))
        return result

    def __len__(self):
        return len(self.values)

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

    def __len__(self):
        return len(self.values)

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

    def __abs__(self):
        return abs(self.value)

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

def _label(point, text, color=(10, 150, 200, 150)):
    x, y, *_ = point
    label.x = x + 3
    label.y = y + 5
    label.text = text
    label.size = 1/10
    label.color = color
    label.draw()


def _fmt(number):
    if abs(round(number) - number) < 0.01:
        return str(int(round(number)))
    return format(number, '.2f')

def draw_point(npass, vert, point):
    pyglet.gl.glColor4f(0, 0, 0, 1)
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


label = pyglet.text.Label(' ', font_size=18, font_name='Mali')


class Presentation:
    def __init__(self):
        self.demo_path = Path('demo.py')
        self.last_mtime = 0
        self.draw_instructions = []
        self.operations = []

    def draw(self, window):
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
        pyglet.gl.glLineWidth(1)

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

    def draw_operations(self, window):
        height_so_far = 0
        pyglet.gl.glTranslatef(0, window.height, 0)
        pyglet.gl.glLineWidth(2)
        for operation in self.operations:
            operation.draw()
            height_so_far += operation.height
            if height_so_far > window.height:
                break

    def tick(self, dt):
        mtime = self.demo_path.stat().st_mtime
        if mtime != self.last_mtime:
            self.last_mtime = mtime
            print('\x1b[2J\x1b[;H', end='')
            print('Reload:', datetime.datetime.fromtimestamp(mtime))
            draw_instructions = []
            operations = []
            token1 = draw_instructions_var.set(draw_instructions)
            token2 = operations_var.set(operations)
            try:
                demo_ns = FunkyNamespace()
                try:
                    code = compile(
                        self.demo_path.read_text(),
                        self.demo_path.name,
                        'exec',
                    )
                    exec(code, demo_ns.dict, demo_ns)
                except Exception as e:
                    traceback.print_exc()
                    self.draw_instructions = []
                    self.operations = [ErrorOperation(e)]
                except SystemExit:
                    self.draw_instructions = draw_instructions
                    self.operations = operations
                else:
                    self.draw_instructions = draw_instructions
                    self.operations = operations
            finally:
                draw_instructions_var.reset(token1)
                operations_var.reset(token2)


class FunkyNamespace:
    def __init__(self):
        self.dict = {}

    def __setitem__(self, key, value):
        self.dict[key] = value
        if isinstance(value, Scalar):
            operations_var.get().append(ScalarOperation(key, value))

    def __getitem__(self, key):
        return self.dict[key]


class ScalarOperation:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.height = label.content_height

    def draw(self):
        pyglet.gl.glPointSize(6)
        pyglet.gl.glEnable(pyglet.gl.GL_POINT_SMOOTH)
        pyglet.gl.glTranslatef(0, -self.height, 0)
        _label(
            (0, 0), f'{self.name} = {_fmt(self.value)}',
            color=(0, 0, 0, 255),
        )


class MatmulOperation:
    def __init__(self, left, right, result):
        self.left = left
        self.right = right
        self.result = result
        self.height = label.content_height * len(left)
        if isinstance(right, Vector):
            self.height += label.content_height * 2

    def draw(self):
        label.text = '['
        bracket_width = label.content_width
        label.text = '  =  '
        eq_width = label.content_width
        label.text = '-0.00,'
        number_width = label.content_width
        line_height = label.content_height

        black = 0, 0, 0, 255
        pyglet.gl.glColor4i(*black)

        def numcolor(number):
            if abs(number) > 9.5:
                return 200, 50, 10, 255
            if abs(number-1) < 0.01:
                return 10, 100, 150, 255
            elif abs(number) >= 0.01:
                return black
            else:
                return 10, 50, 100, 100

        def draw_line(numbers, y=0):
            for i, number in enumerate(numbers):
                color = numcolor(number)
                label.anchor_x = 'right'
                _label(
                    (bracket_width + (i+1) * number_width, y),
                    format(number, '.2f'),
                    color=color,
                )
                label.anchor_x = 'left'
                if i < len(numbers) - 1:
                    _label((bracket_width + (i+1) * number_width, y), ',',
                        color=color)

        def draw_vector(vector):
            _label((0, 0), '[', color=black)
            draw_line(vector)
            _label((bracket_width + len(vector) * number_width, 0), ']',
                   color=black)
            pyglet.gl.glColor4f(0, 0, 0, 1)

        def draw_matrix(mat):
            for i, line in enumerate(mat):
                draw_line(line, -line_height*(i+1))
            start = -0.2 * line_height
            end = -(len(mat)) * line_height
            x1 = bracket_width * 0.6
            x2 = bracket_width * 1.1
            pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
            pyglet.gl.glVertex2f(x2, start)
            pyglet.gl.glVertex2f(x1, start)
            pyglet.gl.glVertex2f(x1, end)
            pyglet.gl.glVertex2f(x2, end)
            pyglet.gl.glEnd()
            x1 = number_width * len(mat[0]) + bracket_width * 3 - x1
            x2 = number_width * len(mat[0]) + bracket_width * 3 - x2
            pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
            pyglet.gl.glVertex2f(x2, start)
            pyglet.gl.glVertex2f(x1, start)
            pyglet.gl.glVertex2f(x1, end)
            pyglet.gl.glVertex2f(x2, end)
            pyglet.gl.glEnd()

        pyglet.gl.glPushMatrix()
        if isinstance(self.right, Vector):
            pyglet.gl.glTranslatef(0, -line_height * 1.25, 0)
            draw_vector(self.right)
            pyglet.gl.glTranslatef(0, -line_height / 4, 0)
            pyglet.gl.glBegin(pyglet.gl.GL_POINTS)
            pyglet.gl.glVertex2f(
                bracket_width + len(self.right) * number_width/2,
                0,
            )
            pyglet.gl.glEnd()
        else:
            draw_matrix(self.right.values)
            pyglet.gl.glTranslatef(
                bracket_width * 2 + number_width * len(self.right.values[0]) + eq_width/2,
                0, 0,
            )
            pyglet.gl.glBegin(pyglet.gl.GL_POINTS)
            pyglet.gl.glVertex2f(
                -(eq_width/2-bracket_width) / 2,
                -line_height * len(self.left) / 2,
            )
            pyglet.gl.glEnd()
        draw_matrix(self.left.values)
        pyglet.gl.glTranslatef(
            bracket_width * 2 + number_width * len(self.left.values[0]) + eq_width,
            0, 0,
        )
        _label(
            (-eq_width, -line_height * (len(self.left)+1) / 2),
            '  =  ',
            color=black,
        )
        if isinstance(self.result, Vector):
            label.anchor_x = 'right'
            for i, number in enumerate(self.result):
                _label(
                    (number_width,
                        -line_height * (i+1)),
                    format(number, '.2f') + ',',
                    color=numcolor(number),
                )
            label.anchor_x = 'left'
            start = -0.2 * line_height
            end = -(len(self.result)) * line_height
            y1 = bracket_width * 0.6
            y2 = bracket_width * 1.1
            pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
            pyglet.gl.glVertex2f(0, y1)
            pyglet.gl.glVertex2f(0, y2)
            pyglet.gl.glVertex2f(number_width, y2)
            pyglet.gl.glVertex2f(number_width, y1)
            pyglet.gl.glEnd()
            y1 = end - y1
            y2 = end - y2
            pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
            pyglet.gl.glVertex2f(0, y1)
            pyglet.gl.glVertex2f(0, y2)
            pyglet.gl.glVertex2f(number_width, y2)
            pyglet.gl.glVertex2f(number_width, y1)
            pyglet.gl.glEnd()
        else:
            draw_matrix(self.result.values)
        pyglet.gl.glPopMatrix()
        pyglet.gl.glTranslatef(0, -self.height, 0)


class ErrorOperation:
    def __init__(self, error):
        self.error = error
        self.tb = [line for line in '\n'.join(
            traceback.format_exception(None, error, error.__traceback__)
        ).splitlines() if line.rstrip()]
        self.height = label.content_height * len(self.tb)

    def draw(self):
        for line in self.tb:
            pyglet.gl.glTranslatef(0, -label.content_height, 0)
            color = 255, 100, 25, 255
            if line.startswith('  '):
                color = 100, 100, 255, 255
            if line.startswith('    '):
                color = 100, 100, 100, 255
            _label((0, 0), line, color=color)


if __name__ == '__main__':
    sys.modules['presentation'] = sys.modules['__main__']
    presentation = Presentation()
    presentation.tick(0)

    display = pyglet.window.get_platform().get_default_display()
    screen = display.get_default_screen()

    window = pyglet.window.Window(
        resizable=True, caption='Diagram',
        width=screen.width//2, height=screen.height//2)
    window.set_location(screen.width//2, 0)

    fps_display = pyglet.window.FPSDisplay(window)
    fps_display.label.font_size = 8

    @window.event
    def on_draw():
        pyglet.gl.glClearColor(1, 1, 1, 1)
        window.clear()
        presentation.draw(window)
        pyglet.gl.glLoadIdentity()
        fps_display.draw()

    oper_height = window.get_location()[1]+window.height
    oper_window = pyglet.window.Window(
        resizable=True, caption='Operations',
        width=screen.width//2, height=screen.height-oper_height)
    oper_window.set_location(screen.width//2, oper_height)

    oper_fps_display = pyglet.window.FPSDisplay(window)
    oper_fps_display.label.font_size = 8

    @oper_window.event
    def on_draw():
        pyglet.gl.glClearColor(1, 1, 1, 1)
        window.clear()
        presentation.draw_operations(oper_window)
        pyglet.gl.glLoadIdentity()
        oper_fps_display.draw()

    pyglet.clock.schedule_interval(presentation.tick, 1/30)

    @window.event
    @oper_window.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        if scroll_y < 0:
            for i in range(-scroll_y):
                if label.font_size > 3:
                    label.font_size /= 1.5
        else:
            for i in range(scroll_y):
                label.font_size *= 1.5


    pyglet.app.run()
