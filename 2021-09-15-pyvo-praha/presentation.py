# This one-off code was written for a presentation, as a welcome respite from
# writing highly maintainable code.
#
# It has served its purpose.
#
# Don't try to read it; it hurts.

# Needs the playful "Mali" font installed system-wide:
# https://fonts.google.com/specimen/Mali

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
import weakref
import operator
import functools

ZOOM = 20

draw_instructions_var = contextvars.ContextVar('draw_instructions_var')
operations_var = contextvars.ContextVar('operations_var')
labels_var = contextvars.ContextVar('labels_var')


class Matrix:
    def __init__(self, values, pedigree=None):
        self.descendants = weakref.WeakSet()
        self.pedigree = pedigree
        if pedigree:
            self.pedigree = pedigree
            self.refresh()
        else:
            self._set_values(values)
            for row in self.values:
                for s in row:
                    s.descendants.add(self)

    def _set_values(self, values):
        self.values = tuple(
            tuple(v if isinstance(v, Scalar) else Scalar(v) for v in row)
            for row in values
        )

    def to_numpy(self):
        return numpy.array(self.values, dtype=float)

    def __str__(self):
        return '[' + ', '.join(
            '[' + ', '.join(_fmt(c) for c in row) + ']'
            for row in self.values
        ) + ']'

    def refresh(self):
        if self.pedigree:
            a, op, b = self.pedigree
            self._set_values(op(a.to_numpy(), b.to_numpy()))
        for d in self.descendants:
            d.refresh()

    def __matmul__(self, other):
        result = type(other)(None, pedigree=(self, operator.matmul, other))
        self.descendants.add(result)
        other.descendants.add(result)
        return result

    def __len__(self):
        return len(self.values)

    def __enter__(self):
        labels_var.set(False)
        draw_instructions_var.get().append((self._enter, (), {}))

    def _enter(self, passn, vert):
        pyglet.gl.glPushMatrix()
        m = self.to_numpy().T
        m = m.astype('float32', order='C').flat
        pyglet.gl.glMultMatrixf( (pyglet.gl.GLfloat * len(m))(*m) )

    def __exit__(self, *exc_info):
        draw_instructions_var.get().append((self._exit, (), {}))

    def _exit(self, passn, vert):
        pyglet.gl.glPopMatrix()
    
    def __str__(self):
        return (
            '['
            + '\n '.join('[' + ', '.join(str(n) for n in r) + ']' for r in self.values)
            + ']'
        )
Array = Matrix

class Vector:
    def __init__(self, values, pedigree=None):
        self.descendants = weakref.WeakSet()
        self.pedigree = pedigree
        if pedigree:
            self.pedigree = pedigree
            self.refresh()
        else:
            self._set_values(values)
            for s in self.values:
                s.descendants.add(self)

    def _set_values(self, values):
        self.values = (
            tuple(v if isinstance(v, Scalar) else Scalar(v) for v in values)
        )

    def refresh(self):
        if self.pedigree:
            a, op, b = self.pedigree
            self._set_values(op(a.to_numpy(), b.to_numpy()))
        for d in self.descendants:
            d.refresh()

    def __len__(self):
        return len(self.values)

    def __getitem__(self, i):
        return self.values[i]

    def to_numpy(self):
        return numpy.array(self.values, dtype=float)

    def __repr__(self):
        return f'<{self.values}>'

    def __str__(self):
        return '[' + ', '.join(_fmt(c) for c in self.values) + ']'

    def __iter__(self):
        return iter(self.values)

    def __sub__(self, other):
        return Vector(a - b for a, b in zip(self, other))

    def __add__(self, other):
        result = Vector(None, pedigree=(self, operator.add, other))
        self.descendants.add(result)
        other.descendants.add(result)
        return result

    def __truediv__(self, other):
        return Vector(c / other for c in self)

    def __mul__(self, other):
        return Vector(c * other for c in self)

    def __abs__(self):
        return math.sqrt(sum(c**2 for c in self))

    def __neg__(self):
        return Vector(-c for c in self)

class Scalar:
    adjusted = False
    def __init__(self, value=None, pedigree=None):
        self.descendants = weakref.WeakSet()
        if pedigree:
            op, *args = self.pedigree = pedigree
            self.refresh()
            for arg in args:
                if isinstance(arg, Scalar):
                    arg.descendants.add(self)
        else:
            self.value = value

    def refresh(self):
        if self.pedigree:
            op, *args = self.pedigree
            self.value = op(*(
                a.value if isinstance(a, Scalar) else a for a in args
            ))
        for d in self.descendants:
            d.refresh()

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value
        for d in self.descendants:
            d.refresh()

    def adjust(self, d):
        self.value += d
        self.adjusted = True

    def __repr__(self):
        return str(self.value)

    def __float__(self):
        return float(self.value)

    def __round__(self, n=0):
        return round(float(self.value), n)

    def __sub__(self, other):
        return Scalar(pedigree=(operator.sub, self, other))

    def __rsub__(self, other):
        return Scalar(pedigree=(operator.sub, other, self))

    def __add__(self, other):
        return Scalar(pedigree=(operator.add, self, other))

    def __radd__(self, other):
        return Scalar(pedigree=(operator.add, other, self))

    def __pow__(self, other):
        return Scalar(pedigree=(operator.pow, self, other))

    def __truediv__(self, other):
        return Scalar(pedigree=(operator.truediv, self, other))

    def __rtruediv__(self, other):
        return Scalar(pedigree=(operator.truediv, other, self))

    def __mul__(self, other):
        return Scalar(pedigree=(operator.mul, self, other))

    def __rmul__(self, other):
        return Scalar(pedigree=(operator.mul, other, self))

    def __neg__(self):
        return Scalar(pedigree=(operator.neg, self))

    def __format__(self, spec):
        return format(self.value, spec)

    def __abs__(self):
        return Scalar(pedigree=(abs, self))

    def __lt__(self, other):
        return Scalar(pedigree=(operator.lt, self, other))

    def __gt__(self, other):
        return Scalar(pedigree=(operator.gt, self, other))

    def __le__(self, other):
        return Scalar(pedigree=(operator.le, self, other))

    def __ge__(self, other):
        return Scalar(pedigree=(operator.ge, self, other))

    def __int__(self):
        return int(self.value)

    def __bool__(self):
        return bool(self.value)

def sin(s):
    return Scalar(pedigree=(math.sin, s))

def cos(s):
    return Scalar(pedigree=(math.cos, s))

class _Draw:
    red = 1, 0, 0, 1
    green = 0, 1, 0, 1
    blue = 0, 0, 1, 1
    black = 0, 0, 0, 1
    white = 1, 1, 1, 1
    yellow = 1, 1, 0, 1
    cyan = 0, 1, 1, 1
    magenta = 1, 0, 1, 1
    gray = 1/2, 1/2, 1/2, 1

    def _draw(self, func, *args, position=None, **kwargs):
        entry = func, args, kwargs
        instructions = draw_instructions_var.get()
        if position is None:
            instructions.append(entry)
        else:
            instructions.insert(0, entry)

    def point(self, point, label='depends', **kwargs):
        if label == 'depends':
            label = labels_var.get()
        self._draw(draw_point, point, **kwargs)
        if label:
            self._draw(draw_label, point, position=0, doit=label)

    __call__ = point

    def arrow(self, a, b, points=True, **kwargs):
        if points:
            self.point(a, **kwargs)
            self.point(b, **kwargs)
        self._draw(draw_arrow, a, b)

    def line(self, a, b, points=False, label='depends', **kwargs):
        self._draw(draw_line, a, b)
        if points:
            self.point(a, **kwargs, label=False)
            self.point(b, **kwargs, label=False)
        if label:
            self._draw(draw_label, a, position=0, doit=label)
            self._draw(draw_label, a, position=0, doit=label)

    def polygon(self, *pts, points=False, color=(0.5, 0.5, 0.5, 1), **kwargs):
        self._draw(draw_polygon, *pts, color=color)
        if points:
            for point in pts:
                self.point(point, **kwargs)

    @property
    def labels(self):
        return labels_var.get()

    @labels.setter
    def labels(self, new):
        return labels_var.set(new)


draw = _Draw()

font_size = 18

@functools.lru_cache()
def _label(point, text, color=(10, 150, 200, 150), anchor_x='left'):
    label = pyglet.text.Label(' ', font_size=font_size, font_name='Mali')
    x, y, *_ = point
    label.x = x + 3
    label.y = y + 5
    label.text = text
    label.size = 1/10
    label.color = color
    label.anchor_x = anchor_x
    return label

def paint_label(*a, **ka):
    _label(*a, **ka).draw()

def _fmt(number):
    if abs(round(number) - number) < 0.01:
        return str(int(round(number)))
    return format(number, '.2f')

def draw_point(npass, vert, point, color=(0, 0, 0, 1)):
    pyglet.gl.glColor4f(*color)
    pyglet.gl.glBegin(pyglet.gl.GL_POINTS)
    pyglet.gl.glVertex3f(*vert(point), 0)
    pyglet.gl.glEnd()

def draw_label(npass, vert, point, doit=True, text=None):
    if doit == 'depends':
        doit = draw_labels
    if not doit:
        return
    px, py, *rest = vert(point)
    frest = ''.join(', ' + _fmt(v) for v in rest)
    if text is None:
        text = f'[{px:.2f}, {py:.2f}{frest}]'
    label = _label((0, 0), text)
    pyglet.gl.glPushMatrix()
    pyglet.gl.glScalef(1/ZOOM, 1/ZOOM, 1)
    pyglet.gl.glTranslatef(px * ZOOM, py * ZOOM, 1)
    label.draw()
    pyglet.gl.glPopMatrix()

def _arrow(vert, a, b):
    absab = abs(a - b)
    if absab:
        unit = (b - a) / (absab / 0.7)
        x1, y1, *_ = a
        x2, y2, *_ = bb = b - unit * 0.2
        x3, y3, *_ = unit
        tip_len = min(0.5, absab/3)
        pyglet.gl.glVertex3f(*vert(a), 0)
        pyglet.gl.glVertex3f(*vert(bb), 0)
        pyglet.gl.glVertex3f(*vert([x2-(x3+y3)*tip_len, y2-(y3-x3)*tip_len]), 0)
        pyglet.gl.glVertex3f(*vert(bb), 0)
        pyglet.gl.glVertex3f(*vert([x2-(x3-y3)*tip_len, y2-(y3+x3)*tip_len]), 0)
        pyglet.gl.glVertex3f(*vert(bb), 0)


def draw_arrow(npass, vert, a, b):
    pyglet.gl.glColor4f(0.5, 0.5, 0.5, 1)
    pyglet.gl.glBegin(pyglet.gl.GL_LINES)
    _arrow(vert, a, b)
    pyglet.gl.glEnd()


def draw_line(npass, vert, a, b):
    if npass == 0:
        pyglet.gl.glColor4f(0.5, 0.5, 0.5, 1)
        pyglet.gl.glBegin(pyglet.gl.GL_LINES)
        pyglet.gl.glVertex3f(*vert(a), 0)
        pyglet.gl.glVertex3f(*vert(b), 0)
        pyglet.gl.glEnd()


def draw_polygon(npass, vert, *points, color=(0.5, 0.5, 0.5, 1)):
    if npass == 0:
        pyglet.gl.glColor4f(*color)
        pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
        for point in (*points, points[0]):
            pyglet.gl.glVertex3f(*vert(point), 0)
        pyglet.gl.glEnd()


class Presentation:
    def __init__(self):
        self.demo_path = Path('demo.py')
        self.last_mtime = 0
        self.draw_instructions = []
        self.operations = []
        self.presentation = 0, 0

    def draw(self, window):
        def vert(point):
            x = float(point[0])
            y = float(point[1])
            if len(point) > 2:
                z = float(point[2])
            else:
                z = 0
            if len(point) > 3:
                x *= float(point[3])
                y *= float(point[3])
                z *= float(point[3])
            return x, y, z # * ZOOM, y * ZOOM, z * ZOOM
        pyglet.gl.glLoadIdentity()
        pyglet.gl.glTranslatef(window.width/2, window.height/2, 0)
        pyglet.gl.glScalef(ZOOM, ZOOM, 0)
        pyglet.gl.glPointSize(6)
        six = ctypes.c_float(6)
        #pyglet.gl.glPointParameterfv(pyglet.gl.GL_POINT_SIZE_MIN, ctypes.POINTER(ctypes.c_float)(six))
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
        for x, y, text in (11, -0.4, 'x'), (-0.4, 11, 'y'):
            draw_label(0, vert, [x, y], text=text)

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

    def adjust(self, window, x, y, dx, dy):
        for operation in self.operations:
            y += operation.height
            if y > window.height:
                operation.adjust(x, y - window.height, dy/50+dx/20)
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
            token3 = labels_var.set('depends')
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
                labels_var.reset(token3)

class FunkyNamespace:
    def __init__(self):
        self.dict = {'print': functools.partial(explain, is_print=True)}

    def __setitem__(self, key, value):
        self.dict[key] = value
        if isinstance(value, (Scalar)):
            operations_var.get().append(ScalarOperation(value))
        if isinstance(value, (Scalar, Vector, Array)):
            value.name = key

    def __getitem__(self, key):
        return self.dict[key]



def explain(thing, *args, is_print=False, **kwargs):
    if kwargs:
        return print(thing, *args, **kwargs)
    if args:
        explain(' '.join(str(s) for s in (thing, *args)))
    if not is_print:
        if isinstance(thing, Scalar):
            return operations_var.get().append(ScalarOperation(thing))
        elif isinstance(thing, (Array, Vector)) and thing.pedigree:
            a, op, b = thing.pedigree
            if op == operator.matmul:
                return operations_var.get().append(MatmulOperation(a, b, thing))
        if isinstance(thing, Array):
            return operations_var.get().append(MatmulOperation(thing, None, None))
        if isinstance(thing, Vector):
            mat = Matrix([thing])
            try:
                mat.name = thing.name
            except AttributeError:
                pass
            return explain(mat)

    for line in str(thing).splitlines():
        operations_var.get().append(TextOperation(line))


class TextOperation:
    def __init__(self, text):
        self.text = str(text)
        label = _label((0, 0), self.text, color=(0, 0, 0, 200))
        self.height = label.content_height

    def draw(self):
        pyglet.gl.glTranslatef(0, -self.height, 0)
        paint_label((0, 0), self.text, color=(0, 0, 0, 200))

    def adjust(self, x, y, d):
        ...


class ScalarOperation:
    def __init__(self, value):
        self.value = value
        label = _label((0, 0), 'Scalar: ', color=(0, 0, 0, 255))
        self.height = label.content_height

    def draw(self):
        pyglet.gl.glPointSize(6)
        pyglet.gl.glEnable(pyglet.gl.GL_POINT_SMOOTH)
        pyglet.gl.glTranslatef(0, -self.height, 0)
        if hasattr(self.value, 'name'):
            text = f'{self.value.name} = '
        else:
            text = 'Scalar: '
        label = _label((0, 0), text, color=(0, 0, 0, 255))
        label.draw()
        paint_label(
            (label.content_width, 0), _fmt(self.value),
            color=numcolor(self.value),
        )

    def adjust(self, x, y, d):
        self.value.adjust(d)



def numcolor(number):
    if abs(number) > 9.5:
        return 200, 50, 10, 255
    if getattr(number, 'adjusted'):
        return 50, 200, 10, 255
    if abs(number-1) < 0.01:
        return 10, 100, 150, 255
    elif abs(number) >= 0.01:
        return 0, 0, 0, 255
    else:
        return 10, 50, 100, 100


class MatmulOperation:
    _name_width = 0
    def __init__(self, left, right, result):
        self.left = left
        self.right = right
        self.result = result
        self.label = _label((0, 0), '[')
        self.height = self.label.content_height * len(left)
        if isinstance(right, Vector):
            self.height += self.label.content_height * 2

    def _sizes(self):
        label = self.label
        label.text = '['
        yield label.content_width
        label.text = '  =  '
        yield label.content_width
        label.text = '-0.00,'
        yield label.content_width
        yield label.content_height

    def draw(self):
        bracket_width, eq_width, number_width, line_height = self._sizes()

        black = 0, 0, 0, 255
        pyglet.gl.glColor4i(*black)

        def draw_line(numbers, y=0):
            for i, number in enumerate(numbers):
                color = numcolor(number)
                paint_label(
                    (bracket_width + (i+1) * number_width, y),
                    format(number, '.2f'),
                    color=color,
                    anchor_x = 'right',
                )
                if i < len(numbers) - 1:
                    paint_label((bracket_width + (i+1) * number_width, y), ',',
                        color=color)

        def draw_vector(vector):
            paint_label((0, 0), '[', color=black)
            draw_line(vector)
            paint_label((bracket_width + len(vector) * number_width, 0), ']',
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
        name = getattr(self.result, 'name', None)
        if not self.result and hasattr(self.left, 'name'):
            name = self.left.name
        if name:
            adj = self.height/2 + line_height/2
            pyglet.gl.glTranslatef(0, -adj, 0)
            label = _label((0, 0), f'{name} = ', color=black)
            label.draw()
            pyglet.gl.glTranslatef(label.content_width, adj, 0)
            self._name_width = label.content_width
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
        elif self.right:
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
        if self.result:
            paint_label(
                (-eq_width, -line_height * (len(self.left)+1) / 2),
                '  =  ',
                color=black,
            )
        if isinstance(self.result, Vector):
            for i, number in enumerate(self.result):
                paint_label(
                    (number_width,
                        -line_height * (i+1)),
                    format(number, '.2f') + ',',
                    color=numcolor(number),
                    anchor_x = 'right',
                )
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
        elif self.result:
            draw_matrix(self.result.values)
        pyglet.gl.glPopMatrix()
        pyglet.gl.glTranslatef(0, -self.height, 0)

    def adjust(self, x, y, d):
        bracket_width, eq_width, number_width, line_height = self._sizes()
        x -= self._name_width
        x -= bracket_width * 2

        def adjust_matrix(mat):
            nx = x / number_width
            ny = y / line_height
            if (
                0 <= ny < len(mat.values)
                and 0 <= nx < len(mat.values[0])
            ):
                mat.values[-int(ny)-1][int(nx)].adjust(d)

        if isinstance(self.right, Vector):
            if y > len(self.result) * line_height:
                x /= number_width
                if x < len(self.right.values):
                    self.right.values[int(x)].adjust(d)
                return
        elif self.right:
            if x < len(self.right.values[0]) * number_width:
                adjust_matrix(self.right)
                return
            x -= bracket_width * 2 + number_width * len(self.right.values[0]) + eq_width/2
        if x < len(self.left.values[0]) * number_width:
            adjust_matrix(self.left)
            return


class ErrorOperation:
    def __init__(self, error):
        self.error = error
        self.tb = [line for line in '\n'.join(
            traceback.format_exception(None, error, error.__traceback__)
        ).splitlines() if line.rstrip()]
        label = _label((0, 0), 'Oh, My!', color=(0, 0, 0, 255))
        self.height = label.content_height * len(self.tb)

    def draw(self):
        for line in self.tb:
            color = 255, 100, 25, 255
            if line.startswith('  '):
                color = 100, 100, 255, 255
            if line.startswith('    '):
                color = 100, 100, 100, 255
            label = _label((0, 0), line, color=color)
            pyglet.gl.glTranslatef(0, -label.content_height, 0)
            label.draw()

    def adjust(self, x, y, d):
        ...

draw_labels = True

if __name__ == '__main__':
    sys.modules['presentation'] = sys.modules['__main__']
    presentation = Presentation()
    presentation.tick(0)

    display = pyglet.canvas.get_display()
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
        resizable=True, caption='Explain',
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

    mouse_pos = 0, 0

    @oper_window.event
    def on_mouse_press(x, y, button, mod):
        presentation.mouse_pos = x, y

    @oper_window.event
    def on_mouse_drag(x, y, dx, dy, button, mod):
        x, y = presentation.mouse_pos
        presentation.adjust(oper_window, x, y, dx, dy)

    pyglet.clock.schedule_interval(presentation.tick, 1/30)

    @window.event
    @oper_window.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        global font_size
        _label.cache_clear()
        presentation.last_mtime = None
        if scroll_y < 0:
            for i in range(-scroll_y):
                if font_size > 3:
                    font_size /= 1.5
        else:
            for i in range(scroll_y):
                font_size *= 1.5

    @window.event
    @oper_window.event
    def on_key_press(key, mod):
        global draw_labels
        if key == pyglet.window.key.L:
            draw_labels = not draw_labels


    pyglet.app.run()
