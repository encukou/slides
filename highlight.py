#! /usr/bin/python
# Encoding: UTF-8

import pygments
from pygments.lexers import PythonLexer, PythonConsoleLexer
from pygments.formatters import LatexFormatter
from pygments.style import Style
import pygments
from pygments.token import Generic, Comment

class CustomStyle(Style):
    default_style = 'default'
    styles = dict(pygments.styles.get_style_by_name('default').styles)
    styles.update({
        Generic.Traceback:    '#f00',
        Generic.Output:       '#668',
    })

def makeLexer(file):
    if file.startswith('>>>'):
        return PythonConsoleLexer()
    else:
        return PythonLexer()

def makeFormatter(verboptions='', nolinenos=False):
    return LatexFormatter(
            verboptions=verboptions.replace('!', '\\'),
            linenos = not nolinenos,
            style=CustomStyle,
        )


if __name__ == '__main__':
    import sys
    try:
        filename = sys.argv[1]
    except IndexError:
        print makeFormatter().get_style_defs()
    else:
        if filename.startswith('='):
            file = filename[1:]
        else:
            file = open(filename).read()
        rv = (pygments.highlight(file, makeLexer(file), makeFormatter(*sys.argv[2:]))
                .replace('~', r'{\texttildelow}')
                .replace("'", r'{\textquotesingle}')
                .replace('<BLANKLINE>', '')
                .replace(u'नमस्कार संसार', r'\includegraphics[height=.7em]{helloworldr}', 1)
                .replace(u'नमस्कार संसार', r'\includegraphics[height=.7em]{helloworldg}', 1)
            )
        print rv.encode('utf-8')
