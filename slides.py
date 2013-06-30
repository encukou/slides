#! /bin/env python2
# Encoding: UTF-8

from __future__ import unicode_literals

import re
import functools
import time

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
    raise ReplaceWidget(urwid.Padding(urwid.LineBox(urwid.BoxAdapter(urwid.ListBox(fib.FibonacciWalker()), 7)), width=30, align='center'))


class Progress(urwid.ProgressBar):
    def render(self, size, focus=True):
        self.current = int((time.time() * 2 % 100))
        self.set_completion(self.current)
        rv = super(Progress, self).render(size, focus)
        self._invalidate()
        return rv


def progressbar_directive(text, subslide_number):
    raise ReplaceWidget(urwid.Padding(Progress('normal', 'reverse', done=100)))


class Line(object):
    def __init__(self, linespec):
        directives = linespec.split('♢')
        self.text = directives.pop(0)
        self.directives = [make_directive(d) for d in directives]
        if not self.directives:
            self.max_subslide = 0
        else:
            self.max_subslide = max(getattr(d, 'max_subslide', 0)
                                    for d in self.directives)

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
        return urwid.Text(addattrs(text), align='center')


class Slide(object):
    def __init__(self, slidespec):
        text = slidespec.get('text') or slidespec['fixtext']
        if slidespec.get('pygments'):
            text = pygments.highlight(text, PythonLexer(),
                                      SlidePygmentsFormatter())
        lines = text.splitlines()
        lines = [Line(l) for l in lines]
        if 'fixtext' in slidespec:
            maxlen = max(len(line) for line in lines)
            for line in lines:
                line.ljust(maxlen)
        self.lines = lines
        self.subslide_count = max(line.max_subslide for line in lines)

    def get_widget(self, subslide_number):
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


class SlideLoop(urwid.MainLoop):
    def __init__(self, slidespecs, current_slide=0):
        self.inner_widget = urwid.AttrMap(urwid.SolidFill(), 'normal')
        self.top_widget = self.inner_widget
        self.top_widget = urwid.Padding(self.top_widget, width=41,
                                        align='center')
        self.top_widget = urwid.Filler(self.top_widget, height=17)
        super(SlideLoop, self).__init__(
                self.top_widget,
                self.palette,
                unhandled_input=self.handle_input,
                handle_mouse=False,
            )
        self.screen.set_terminal_properties(colors=256)
        self.slides = [Slide(s) for s in slidespecs]
        self.current_slide = current_slide
        self.current_subslide = 0
        self.reset_alarm()
        try:
            self.update_slide()
        except IndexError:
            self.current_slide = 0
            self.update_slide()

    def reset_alarm(self, loop=None, data=None):
        self.set_alarm_in(0.1, self.reset_alarm)

    palette = [
        ('hide', 'light gray', 'white'),  # 'white' to hide notes!
        ('emph', 'dark blue,bold', 'white', 'standout'),
        ('deemph', 'light gray', 'white'),   # XXX: Not bold!
        ('bold', 'black,bold', 'white', 'standout'),
        ('normal', 'black', 'white'),
        ('reverse', 'white', 'black'),

        ('pygments_kwd', 'dark blue', 'white'),
        ('pygments_string', 'dark blue', 'white'),
    ]

    def update_slide(self):
        slide = self.slides[self.current_slide]
        widget = slide.get_widget(self.current_subslide)
        self.inner_widget.original_widget = widget
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
        elif key in ('n', ' ', 'right'):
            try:
                slide = self.slides[self.current_slide]
            except IndexError:
                pass
            else:
                if self.current_subslide < slide.subslide_count:
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
                self.current_subslide = slide.subslide_count
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


if __name__ == '__main__':
    try:
        with open('last_slide') as slidefile:
            current_slide = int(slidefile.read())
    except Exception as e:
        print(e)
        current_slide = 0
    with open('slides.yaml') as slide_file:
        SlideLoop(yaml.safe_load(slide_file), current_slide).run()
