#! /usr/bin/env python3

import os
import sys
import threading
import traceback

import urwid

class FancyEdit(urwid.Edit):
    def keypress(self, size, key):
        if key == 'tab':
            self.insert_text('    ')
        else:
            super().keypress(size, key)


class ResultColumn(urwid.WidgetWrap):
    def __init__(self):
        self.statusbox = urwid.Text('Ready')
        self.foot = urwid.AttrWrap(self.statusbox, 'status')
        self.items = urwid.SimpleListWalker([])
        self.body = urwid.ListBox(self.items)
        self.frame = urwid.Frame(self.body, footer=self.foot)
        urwid.WidgetWrap.__init__(self, self.frame)


class TextColumn(urwid.WidgetWrap):
    def __init__(self, text):
        self.textbox = FancyEdit(edit_text=text, multiline=True)
        self.walker = urwid.SimpleListWalker([self.textbox])
        self.listbox = urwid.ListBox(self.walker)
        self.footer = urwid.AttrWrap(urwid.Text("Python"), 'status')
        self.frame = urwid.Frame(self.listbox, footer=self.footer)
        urwid.WidgetWrap.__init__(self, self.frame)


class Runner(threading.Thread):
    def __init__(self, stdout, result_pipe, code):
        self.stdout = os.fdopen(stdout, 'w')
        self.result_pipe = os.fdopen(result_pipe, 'w')
        self.code = code
        super().__init__()

    def print(self, *args, file=None, **kwargs):
        if file is None or file == sys.stdout:
            file = self.stdout
            print(*args, file=self.stdout, **kwargs)
            self.stdout.flush()
        else:
            print(*args, file=file, **kwargs)

    def run(self):
        try:
            code = compile(self.code, filename='<input>', mode='exec')
            exec(self.code, dict(print=self.print))
        except BaseException as exc:
            self.result_pipe.write(traceback.format_exc().strip())
        else:
            self.result_pipe.write('Okay!')
        try:
            self.result_pipe.close()
        except IOError:
            pass


class Experimentor(object):
    palette = [
            ('status', 'white', 'dark blue'),
        ]

    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            with open(filename) as f:
                text = f.read()
        else:
            text = ''
        self.text = TextColumn(text)
        self.result = ResultColumn()
        self.columns = urwid.Columns([self.text, self.result], 1)
        self.col_list = self.columns.widget_list
        self.view = urwid.Frame(self.columns)
        self.stdout_pipe = None

        urwid.connect_signal(self.text.textbox, 'change', self.text_changed)

    def main(self):
        self.loop = urwid.MainLoop(self.view, self.palette)
        self.loop.run()

        self.start_exec(text)

    def text_changed(self, edit, text):
        self.start_exec(text)

    def start_exec(self, text):
        self.save(text)
        if self.stdout_pipe:
            self.loop.remove_watch_pipe(self.stdout_pipe)
            self.loop.remove_watch_pipe(self.result_pipe)
        result = self.result = ResultColumn()
        def set_result(text):
            if text:
                result.statusbox.set_text(text)
                self.loop.draw_screen()
        def add_text(text):
            if text:
                result.items.append(urwid.Text(text))
                self.loop.draw_screen()
        self.stdout_pipe = self.loop.watch_pipe(add_text)
        self.result_pipe = self.loop.watch_pipe(set_result)
        self.columns.widget_list[1] = result
        Runner(self.stdout_pipe, self.result_pipe, text).start()

    def save(self, text):
        self.result.statusbox.set_text('Saved')
        with open(self.filename, 'w') as f:
            f.write(text)


Experimentor(*sys.argv[1:]).main()
