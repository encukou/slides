#! /bin/env python2
# Encoding: UTF-8

from __future__ import unicode_literals

import os
import textwrap

import urwid  # pip install urwid
import yaml  # pip install yaml

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

def make_line(string, length=None):
    if string == '─────────────────────────────────────────':
        return urwid.BoxAdapter(urwid.SolidFill('─'), 1)
    else:
        if length:
            string = string.ljust(length)
        return urwid.Text(addattrs(string), align='center')

def make_slide(slidespec):
    text = slidespec.get('text')
    fixtext = slidespec.get('fixtext')
    if text:
        lines = text.splitlines()
        lines = [l.partition('♢')[0] for l in lines]
        return urwid.Filler(urwid.Pile([
            make_line(line.strip()) for line in lines]))
    elif fixtext:
        lines = list(textwrap.dedent(fixtext).splitlines())
        lines = [l.partition('♢')[0] for l in lines]
        maxlen = max(len(l) for l in lines)
        return urwid.Filler(urwid.Pile([
            make_line(l, maxlen) for l in lines]))

class SlideLoop(urwid.MainLoop):
    def __init__(self, slides, current_slide=0):
        self.inner_widget = urwid.AttrMap(urwid.SolidFill(), 'normal')
        self.top_widget = self.inner_widget
        self.top_widget = urwid.Padding(self.top_widget, width=41)
        self.top_widget = urwid.Filler(self.top_widget, height=17)
        self.top_widget = urwid.Padding(self.top_widget)
        super(SlideLoop, self).__init__(
                self.top_widget,
                self.palette,
                unhandled_input=self.handle_input,
            )
        self.screen.set_terminal_properties(colors=256)
        self.slides = [make_slide(s) for s in slides]
        self.current_slide = current_slide
        try:
            self.update_slide()
        except IndexError:
            self.current_slide = 0
            self.update_slide()

    palette = [
        ('hide', 'light gray', 'white', 'standout'),  # change to 'white', 'white' to hide notes!
        ('emph', 'dark blue,bold', 'white', 'standout'),
        ('deemph', 'dark gray', 'white', 'standout'),   # XXX: Not bold!
        ('bold', 'black,bold', 'white', 'standout'),
        ('normal', 'black', 'white'),
    ]

    def update_slide(self):
        self.inner_widget.original_widget = self.slides[self.current_slide]
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
            self.current_slide += 1
            try:
                self.update_slide()
            except IndexError:
                raise urwid.ExitMainLoop()
        elif key in ('p', 'backspace', 'left') and self.current_slide > 1:
            self.current_slide -= 1
            self.update_slide()
        else:
            #raise SystemExit(key)
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
