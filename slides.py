#! /bin/env python2
# Encoding: UTF-8

from __future__ import unicode_literals

import re
import functools
import time
import random
import sys

import urwid
import yaml
import pygments
import pygments.formatter
import pygments.token
from pygments.lexers.agile import PythonLexer

import fib

class reify(object):
    # https://github.com/Pylons/pyramid/blob/master/pyramid/decorator.py
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def addattrs(string):
    result = []
    for part in string.split('»'):
        normal, sep, emph  = part.partition('«')
        if normal:
            result.append(normal)
        if '≈' in emph:
            prop, sep, emph = emph.partition('≈')
        else:
            prop = 'emph'
        if emph:
            result.append((prop, emph))
    if not result:
        result = ['']
    return result


class ReplaceWidget(BaseException):
    def __init__(self, widget):
        BaseException.__init__(self, widget)
        self.widget = widget


def make_directive(spec):
    spec = spec.strip()
    if not spec or spec.startswith(('Note:', 'X' 'XX:')):
        return lambda text, **kw: text
    if spec == 'hr':
        return hr_directive
    if spec == 'fib':
        return fib_directive
    if spec == 'progressbar':
        return progressbar_directive
    if spec == 'widget':
        return widget_directive
    if spec == 'widget_canvas':
        return widget_canvas_directive
    if spec == 'center':
        return lambda text, **kw: text.strip()
    match = re.match(r'\[(?P<num>[0-9]+)\] (?P<pattern>.*)', spec)
    if match:
        return HideDirective(attr='hide', **match.groupdict())
    match = re.match(r'@(?P<attr>[^[]+)\[(?P<num>[0-9]+)\] ?(?P<pattern>.*)',
                     spec)
    if match:
        return AttrDirective(**match.groupdict())
    match = re.match(r'animate (?P<marker>[^=]+)=(?P<animation>.*)', spec)
    if match:
        return functools.partial(animate_directive, **match.groupdict())
    match = re.match(r'reveal\[(?P<num>[0-9]+)\]', spec)
    if match:
        # XXX: reveal
        return lambda text, **kw: text
    match = re.match(r'rainbow\[(?P<num>[0-9]+)\]', spec)
    if match:
        return functools.partial(rainbow_directive, **match.groupdict())
    #return lambda text, **kw: text
    raise ValueError(repr(spec))


class AttrDirective(object):
    def __init__(self, attr, num, pattern):
        self.attr = attr
        self.num = self.max_subslide = int(num)
        self.pattern = pattern

    def sub_callback(self, text):
        return "«%s≈%s»" % (self.attr, text.group().replace('»', ''))

    def __call__(self, text, subslide_number):
        if self.num <= subslide_number:
            return re.sub(self.pattern, self.sub_callback, text)
        else:
            return text


class HideDirective(AttrDirective):
    def __call__(self, text, subslide_number):
        if self.num > subslide_number:
            return re.sub(self.pattern, self.sub_callback, text)
        else:
            return text


class Animation(urwid.Text):
    def __init__(self, text, marker, animation, *args, **kwargs):
        self.marker = marker
        self.animation = animation.split(',')
        self.orig_text = text
        super(Animation, self).__init__(text, *args, **kwargs)

    def render(self, size, focus=True):
        frame = self.animation[int(time.time() * 5) % len(self.animation)]
        self.set_text(self.orig_text.replace(self.marker, frame))
        rv = super(Animation, self).render(size, focus=True)
        self._invalidate()
        return rv


def animate_directive(text, subslide_number, **kwargs):
    kwargs.setdefault('align', 'center')
    raise ReplaceWidget(Animation(text, **kwargs))


def hr_directive(text, subslide_number):
    raise ReplaceWidget(urwid.BoxAdapter(urwid.SolidFill('─'), 1))


def fib_directive(text, subslide_number):
    widget = urwid.ListBox(fib.FibonacciWalker())
    widget = urwid.BoxAdapter(widget, 7)
    widget = urwid.LineBox(widget)
    widget = urwid.Padding(widget, width=30, align='center')
    raise ReplaceWidget(widget)


class Progress(urwid.ProgressBar):
    def render(self, size, focus=True):
        self.current = int((time.time() * 2 % 100))
        self.set_completion(self.current)
        rv = super(Progress, self).render(size, focus)
        self._invalidate()
        return rv


class TimeChunkProgress(urwid.ProgressBar):
    def __init__(self, chunk_seconds):
        super(TimeChunkProgress, self).__init__('normal', 'reverse', done=chunk_seconds)
        self.chunk_seconds = chunk_seconds

    def render(self, size, focus=True):
        self.current = int((time.time() % self.chunk_seconds))
        self.set_completion(self.current)
        rv = super(TimeChunkProgress, self).render(size, focus)
        self._invalidate()
        return rv

    def get_text(self):
        return "-{0:02d}:{1:02d}".format(
            *divmod(self.chunk_seconds - int((time.time() % self.chunk_seconds)), 60))


class FractionProgress(urwid.ProgressBar):
    def get_text(self):
        return "{0}/{1}".format(self.current, self.done)


def progressbar_directive(text, subslide_number):
    raise ReplaceWidget(urwid.Padding(Progress('normal', 'reverse', done=100)))


class Rainbow(urwid.Text):
    def __init__(self, text, *args, **kwargs):
        self.orig_text = text
        super(Rainbow, self).__init__(text, *args, **kwargs)

    def render(self, size, focus=True):
        text = []
        rng = random.WichmannHill(int(time.time() * 10))
        for char in self.orig_text:
            color = '#' + ''.join(rng.choice('0068068ad') for i in range(3))
            text.append((urwid.AttrSpec(color, 'white'), char))
        self.set_text(text)
        rv = super(Rainbow, self).render(size, focus)
        self._invalidate()
        return rv


def rainbow_directive(text, subslide_number, num):
    if subslide_number >= int(num):
        raise ReplaceWidget(Rainbow(text, align='center'))
    else:
        return text


def make_demo_widget():
    return urwid.Pile([
        urwid.Text(['ab', ('red', 'C'), 'd'], align='center'),
        urwid.Text(['e', ('green', 'f'), 'gh'], align='center'),
    ])


def widget_directive(text, subslide_number):
    w = urwid.Padding(make_demo_widget())
    raise ReplaceWidget(urwid.Padding(urwid.LineBox(w),
                                      width=22, align='center'))


def widget_canvas_directive(text, subslide_number):
    widget = make_demo_widget()
    canvas = widget.render(size=(10,))
    import pprint
    raise ReplaceWidget(urwid.Text(pprint.pformat(list(canvas.content()), width=40)))


class Movie(urwid.BoxWidget):
    #chars = 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワ'
    chars = 'ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜ'
    colors = [
            '#000',
            '#060',
            '#080',
            '#0a0',
            '#0d0',
            '#0f0',
            '#6f6',
            '#8f8',
            '#afa',
            '#dfd',
            '#fff',
        ]

    no_cache = ['render']

    def __init__(self):
        self.slots = {}

    def make_row(self, size, row_num):
        #row = ''.join(random.choice(self.chars) for i in range(size // 2))
        #if size % 2:
        #    row += ' '
        row = ''.join(random.choice(self.chars) for i in range(size))
        return row.encode('utf-8')

    def get_color(self, x, y, first=False):
        try:
            intensity, speed, seed_counter = self.slots[x, y]
        except Exception:
            intensity = 0
            speed = random.uniform(0.05, 0.2)
            seed_counter = 0
        top = self.slots.get((x, y+1))
        if top:
            if top[2] == 3:
                seed_counter = 1
        if random.random() < 0.001 or seed_counter == 1:
            intensity = 1
            speed = random.expovariate(10)
        else:
            intensity -= speed
        if random.random() < 0.001 or (first and random.random() < 0.005):
            seed_counter = 1
        if seed_counter:
            seed_counter += 1
        self.slots[x, y] = intensity, speed, seed_counter

        if intensity < 0:
            intensity = 0
        color_index = int((intensity ** 2) * len(self.colors))
        if color_index < 0:
            color_index = 0
        if color_index >= len(self.colors):
            color_index = len(self.colors) - 1
        return self.colors[color_index]

    def make_attr_row(self, size, row_num, first=False):
        length = len(self.chars[0].encode('utf-8'))
        return [(urwid.AttrSpec(self.get_color(i, row_num, first), 'black'),
                 length)
                for i in range(size)]

    def render(self, size, focus=False):
        (maxcol, maxrow) = size
        rows = [self.make_row(maxcol, i) for i in range(maxrow)]
        arows = [self.make_attr_row(maxcol, i, i == maxrow - 1)
                 for i in range(maxrow)]
        arows.reverse()
        return urwid.TextCanvas(rows, arows)

    def keypress(self, v, k):
        return k


class Line(object):
    def __init__(self, linespec, align='center'):
        directives = linespec.split('♢')
        self.text = directives.pop(0)
        self.directives = [make_directive(d) for d in directives]
        if not self.directives:
            self.max_subslide = 0
        else:
            self.max_subslide = max(getattr(d, 'max_subslide', 0)
                                    for d in self.directives)
        self.align = align

    def str(self, subslide_number):
        return self.text

    def ljust(self, length):
        self.text += ' ' * (length - len(self))

    def __len__(self):
        text = addattrs(self.text)
        length = 0
        for part in text:
            if isinstance(part, tuple):
                attr, part = part
            length += len(part)
        return length

    def widget(self, subslide_number):
        text = self.text
        for directive in self.directives:
            try:
                text = directive(text, subslide_number=subslide_number)
            except ReplaceWidget as e:
                return e.widget
        return urwid.Text(addattrs(text), align=self.align)


class Slide(object):
    def __init__(self, slidespec):
        text = slidespec.get('text') or slidespec['fixtext']
        if slidespec.get('pygments'):
            text = pygments.highlight(text, PythonLexer(),
                                      SlidePygmentsFormatter())
        lines = text.splitlines()
        align = slidespec.get('align', 'center')
        lines = [Line(l, align=align) for l in lines]
        if 'fixtext' in slidespec:
            maxlen = max(len(line) for line in lines)
            for line in lines:
                line.ljust(maxlen)
        self.lines = lines
        self.subslide_count = max(line.max_subslide for line in lines)
        self.notes = slidespec.get('note')

    def __new__(cls, slidespec):
        if slidespec.get('special') == 'movie':
            return lambda num: Movie()
        else:
            return object.__new__(cls, slidespec)

    def __call__(self, subslide_number):
        return urwid.Filler(urwid.Pile([
            line.widget(subslide_number) for line in self.lines]))


class SlidePygmentsFormatter(pygments.formatter.Formatter):
    """
    Output the text unchanged without any formatting.
    """
    name = 'Text only'
    aliases = ['text', 'null']
    filenames = ['*.txt']

    def format(self, tokensource, outfile):
        enc = self.encoding
        for ttype, value in tokensource:
            attr = None
            if ttype in pygments.token.Token.Keyword:
                attr = 'pygments_kwd'
            if ttype in pygments.token.Operator.Word:
                attr = 'pygments_kwd'
            elif ttype in pygments.token.Token.String:
                attr = 'pygments_string'
            elif ttype in pygments.token.Token.Comment:
                attr = 'deemph'
            elif ttype in pygments.token.Token.Name.Decorator:
                attr = 'pygments_kwd'
            if attr:
                value = '«%s≈%s»' % (attr, value)
            if enc:
                outfile.write(value.encode(enc))
            else:
                outfile.write(value)


def get_blank_slide():
    return urwid.AttrMap(urwid.SolidFill(), 'normal')


class SlideLoop(urwid.MainLoop):
    def __init__(self, slidespecs, current_slide=0):
        self.inner_widget = get_blank_slide()
        self.top_widget = wrap_slide_widget(self.inner_widget)
        self.inner_next_widget = get_blank_slide()
        self.next_widget = wrap_slide_widget(self.inner_next_widget)
        self.notes_widget = urwid.Text('')
        super(SlideLoop, self).__init__(
                urwid.AttrMap(self.top_widget, {'hide': 'hidden'}),
                self.palette,
                unhandled_input=self.handle_input,
                handle_mouse=False,
            )
        self.screen.set_terminal_properties(colors=256)
        self.slides = [Slide(s) for s in slidespecs if not s.get('skip')]
        self.progress_widget = FractionProgress('normal', 'reverse',
                                                done=len(self.slides) - 1)
        self.current_slide = current_slide
        self.current_subslide = 0
        self.reset_alarm()
        try:
            self.update_slide()
        except IndexError:
            self.current_slide = 0
            self.update_slide()

    def reset_alarm(self, loop=None, data=None):
        self.set_alarm_in(0.03, self.reset_alarm)

    palette = [
        ('hide', 'light gray', 'white'),
        ('hidden', 'white', 'white'),
        ('emph', 'dark blue,bold', 'white', 'standout'),
        ('deemph', 'light gray', 'white'),
        ('bold', 'black,bold', 'white', 'standout'),
        ('normal', 'black', 'white'),
        ('reverse', 'white', 'black'),
        ('red', 'light red', 'white'),
        ('green', 'light green', 'white'),

        ('pygments_kwd', 'dark blue', 'white'),
        ('pygments_string', 'dark blue', 'white'),
    ]

    def update_slide(self):
        slide = self.slides[self.current_slide]
        widget = slide(self.current_subslide)
        self.inner_widget.original_widget = widget

        notes = getattr(slide, 'notes', None)
        if isinstance(notes, list):
            self.notes_widget.set_text('\n'.join(unicode(n) for n in notes))
        elif isinstance(notes, basestring):
            self.notes_widget.set_text(notes)
        elif notes:
            self.notes_widget.set_text(unicode(notes))
        else:
            self.notes_widget.set_text('')

        try:
            next_slide = self.slides[self.current_slide + 1]
        except IndexError:
            self.inner_next_widget.original_widget = get_blank_slide()
        else:
            widget = next_slide(getattr(next_slide, 'subslide_count', 0))
            self.inner_next_widget.original_widget = widget

        self.progress_widget.set_completion(self.current_slide)

        with open('last_slide', 'w') as savefile:
            savefile.write(str(self.current_slide))

    def handle_input(self, key):
        if isinstance(key, tuple) and key[0] == 'mouse press':
            if key[1] in (5, 1):
                key = 'right'
            if key[1] in (4, 3):
                key = 'left'

        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key in ('s', 'S'):
            env = {'PS1': '$ ', 'PS2': '. '}
            cmd = ['bash', '--rcfile', '/dev/null']
            widget = urwid.Terminal(cmd, env=env)
            widget = urwid.LineBox(widget)
            self.inner_widget.original_widget = widget
        elif key in ('r', 'R'):
            self.update_slide()
        elif key in ('n', ' ', 'right'):
            try:
                slide = self.slides[self.current_slide]
            except IndexError:
                pass
            else:
                if self.current_subslide < getattr(slide, 'subslide_count', 0):
                    self.current_subslide += 1
                    self.update_slide()
                    return
            key = 'page down'
        elif key in ('p', 'backspace', 'left'):
            if self.current_subslide:
                self.current_subslide -= 1
                self.update_slide()
            elif self.current_slide > 1:
                self.current_slide -= 1
                slide = self.slides[self.current_slide]
                self.current_subslide = getattr(slide, 'subslide_count', 0)
                self.update_slide()
        elif key in ('0',):
            self.current_slide = self.current_subslide = 0
            self.update_slide()

        if key == 'page down' and self.current_slide <= len(self.slides) - 2:
            self.current_slide += 1
            self.current_subslide = 0
            self.update_slide()
        elif key == 'page up' and self.current_slide > 1:
            self.current_slide -= 1
            self.current_subslide = 0
            self.update_slide()
        else:
            #raise SystemExit(repr(key))
            pass


class ExtraLoop(urwid.MainLoop):
    # Very dirty hack for a "confidence monitor" on another TTY
    def __init__(self, device, main_loop):
        self.main_loop = main_loop
        old_stdout = sys.stdout
        try:
            sys.stdout = open(device, 'w')
            screen = urwid.raw_display.Screen()
        finally:
            sys.stdout = old_stdout
        self.top_widget = main_loop.top_widget
        self.next_widget = main_loop.next_widget
        self.top_widget = urwid.Pile([
            (19, urwid.Columns([
                wrap_slide_widget(self.top_widget),
                wrap_slide_widget(self.next_widget),
            ])),
            urwid.Filler(main_loop.notes_widget),
            (1, urwid.Filler(TimeChunkProgress(30 * 60))),
            (1, urwid.Filler(main_loop.progress_widget)),
        ])
        super(ExtraLoop, self).__init__(
                self.top_widget,
                main_loop.palette,
                handle_mouse=False,
                event_loop=main_loop.event_loop,
                screen=screen,
            )
        self.screen.set_terminal_properties(colors=256)
        self.screen.get_cols_rows = self.screen_get_cols_rows
        self.screen.start()
        def enter_idle():
            # We don't get SIGWINCH :(
            # recalc size every time
            self.screen_size = None
            self.entering_idle()
        self.event_loop.enter_idle(enter_idle)


    def screen_get_cols_rows(self):
        """Monkeypatch for urwid.raw_display.Screen.get_cols_rows

        This un-hardcodes the assumption that we're dealing with stdout (fd 0)
        """
        import fcntl, struct, termios
        screen = self.screen

        buf = fcntl.ioctl(screen._term_output_file, termios.TIOCGWINSZ, ' '*4)
        y, x = struct.unpack('hh', buf)
        self.screen.maxrow = y
        return x, y


def wrap_slide_widget(widget):
    widget = urwid.Padding(widget, width=41, align='center')
    widget = urwid.Filler(widget, height=17)
    return widget


if __name__ == '__main__':
    try:
        with open('last_slide') as slidefile:
            current_slide = int(slidefile.read())
    except Exception as e:
        print(e)
        current_slide = 0
    with open('slides.yaml') as slide_file:
        loop = SlideLoop(yaml.safe_load(slide_file), current_slide)
        extra_loop = None
        if len(sys.argv) > 1:
            extra_loop = ExtraLoop(sys.argv[1], loop)
        loop.run()
        if extra_loop:
            extra_loop.screen.stop()
