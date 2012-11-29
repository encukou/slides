#! /bin/env python2
# Encoding: UTF-8

from __future__ import unicode_literals

import urwid
import yaml

def addattrs(string):
    result = []
    for part in string.split('»'):
        normal, sep, emph  = part.partition('«')
        if normal:
            result.append(normal)
        if '≈' in emph:
            prop, sep, emph = emph.partition('≈')
        else:
            prop, emph = 'emph', emph
        if emph:
            result.append((prop, emph))
    if not result:
        result = ['']
    return result

def make_line(string):
    return urwid.Text(addattrs(string), align='center')

def make_slide(string):
    return urwid.Filler(urwid.Pile([
        make_line(line.strip()) for line in string.splitlines()]))

class SlideLoop(urwid.MainLoop):
    def __init__(self, slides, current_slide=0):
        self.top_widget = urwid.AttrMap(urwid.SolidFill(), 'normal')
        super(SlideLoop, self).__init__(
                self.top_widget,
                self.palette,
                unhandled_input=self.handle_input,
            )
        self.screen.set_terminal_properties(colors=256)
        self.slides = [make_slide(s) for s in slides]
        self.current_slide = current_slide
        self.update_slide()

    palette = [
        ('hide', 'light gray', 'white', 'standout'),
        ('emph', 'dark blue,bold', 'white', 'standout'),
        ('normal', 'black', 'white'),
    ]

    def update_slide(self):
        self.top_widget.original_widget = self.slides[self.current_slide]

    def handle_input(self, key):
        if key in ('q', 'Q'):
            raise urwid.ExitMainLoop()
        elif key in ('n', ' '):
            self.current_slide += 1
            try:
                self.update_slide()
            except IndexError:
                raise urwid.ExitMainLoop()
        elif key in ('p', 'backspace') and current_slide > 0:
            self.current_slide -= 1
            self.update_slide()
        else:
            raise SystemExit(key)

if __name__ == '__main__':
    SlideLoop(yaml.load(open('slides.yaml'))).run()
