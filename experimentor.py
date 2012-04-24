#! /usr/bin/env python3

import os
import sys
import threading
import traceback

import urwid

class FancyEdit(urwid.ListBox):
    signals = ["change"]

    def __init__(self, text):
        self.lines = []
        self.edit_text = text
        super().__init__(self.lines)

    def _make_line_editor(self, text):
        text = text.expandtabs(4)
        editor = urwid.Edit(edit_text=text, wrap='clip', edit_pos=0)
        urwid.connect_signal(editor, 'change',
            lambda subedit, text: self._emit(self, 'change', text))
        return editor

    @property
    def edit_text(self):
        return '\n'.join(e.edit_text for e in self.lines)

    @edit_text.setter
    def edit_text(self, new_text):
        self.lines[:] = [self._make_line_editor(l)
            for l in new_text.splitlines() + ['']]

    def keypress(self, size, key):
        if key == 'backspace':
            widget, pos = self.get_focus()
            head = widget.edit_text[:widget.edit_pos]
            if head and not head.strip():
                key = 'shift tab'
        elif key == 'home':
            widget, pos = self.get_focus()
            if widget.edit_pos == 0:
                key = 'smart home'
        key = super().keypress(size, key)
        if key == 'left':
            widget, pos = self.get_focus()
            if pos > 0:
                self.set_focus(pos - 1)
                widget, pos = self.get_focus()
                self.keypress(size, 'end')
        elif key == 'right':
            widget, pos = self.get_focus()
            widget.set_edit_pos(0)
            self.set_focus(pos + 1)
        elif key == 'tab':
            widget, pos = self.get_focus()
            old_pos = widget.edit_pos
            widget.set_edit_pos(0)
            widget.insert_text(' ' * 4)
            widget.set_edit_pos(old_pos + 4)
        elif key == 'shift tab':
            widget, pos = self.get_focus()
            old_pos = widget.edit_pos
            for i in range(4):
                if widget.edit_text.startswith(' '):
                    widget.set_edit_pos(widget.edit_pos - 1)
                    widget.edit_text = widget.edit_text[1:]
        elif key == 'enter':
            widget, pos = self.get_focus()
            orig_line = widget.edit_text
            split_point = widget.edit_pos
            head, tail = orig_line[:split_point], orig_line[split_point:]
            widget.edit_text = head
            tail = tail.lstrip()
            self.lines[pos + 1:pos + 1] = [self._make_line_editor(tail)]
            self.keypress(size, 'down')
            widget, pos = self.get_focus()
            widget.edit_pos = 0
            while orig_line.startswith(' ' * 4):
                widget.insert_text(' ' * 4)
                orig_line = orig_line[4:]
            if head.strip().endswith(':'):
                widget.insert_text(' ' * 4)
            self.keypress(size, 'smart home')
        elif key == 'smart home':
            widget, pos = self.get_focus()
            pos = len(widget.edit_text) - len(widget.edit_text.lstrip())
            widget.edit_pos = pos
        elif key == 'backspace':
            widget, pos = self.get_focus()
            if pos:
                text = widget.edit_text
                self.lines[pos:pos + 1] = []
                self.set_focus(pos - 1)
                widget, pos = self.get_focus()
                self.keypress(size, 'end')
                widget.edit_text += text
        elif key == 'delete':
            widget, pos = self.get_focus()
            try:
                next_widget = self.lines[pos + 1]
            except IndexError:
                pass
            else:
                widget.edit_text += next_widget.edit_text.strip()
                self.lines[pos + 1:pos + 2] = []
        else:
            return key


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
        self.textbox = FancyEdit(text)
        self.footer = urwid.AttrWrap(urwid.Text("Python"), 'status')
        self.frame = urwid.Frame(self.textbox, footer=self.footer)
        urwid.WidgetWrap.__init__(self, self.frame)

    def keypress(self, size, key):
        rv = super().keypress(size, key)
        if key:
            self.footer.set_text(key)
        return rv


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
            code = compile(self.code, filename='<experimentor>', mode='exec')
            exec(self.code, dict(print=self.print))
        except BaseException as exc:
            self.result_pipe.write(traceback.format_exc().strip())
        else:
            self.result_pipe.write('Okay!')
        for pipe in self.stdout, self.result_pipe:
            try:
                self.pipe.close()
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
        self.loop.screen.tty_signal_keys(
                susp='undefined',
                stop='undefined',
                start='undefined',
            )
        self.start_exec(self.text.textbox.edit_text)
        self.loop.run()

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
        #Runner(self.stdout_pipe, self.result_pipe, text).start()

    def save(self, text):
        self.result.statusbox.set_text('Saved')
        with open(self.filename, 'w') as f:
            f.write(text)

    def input_filter(self, keys, raw):
        self.text.footer.set_text(key)
        return keys

Experimentor(*sys.argv[1:]).main()
