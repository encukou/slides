from pathlib import Path
import asyncio
import textwrap

from flask import Flask, render_template, Response
import jinja2
from markupsafe import Markup
from werkzeug.middleware.shared_data import SharedDataMiddleware
from markdown_it import MarkdownIt
import strictyaml
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

app = Flask(__name__)
app.debug = True

formatter = HtmlFormatter(nowrap=True, style='stata')

def highlight_code(code, name, attrs):
    """Highlight a block of code"""
    if not name:
        return code

    #if attrs == 'run':
        #ns = {'asyncio': asyncio}
        #exec(f'async def f():\n{textwrap.indent(code, " ")}', ns)
        #result = asyncio.run(ns['f']())
    #elif attrs:
        #print(f"Ignoring {attrs=}")

    lexer = get_lexer_by_name(name)

    return '<div class="highlight">' + highlight(code, lexer, formatter) + '</div>'

md = (
    MarkdownIt('commonmark', {'highlight': highlight_code})
)

@app.template_filter('md')
def md_filter(text):
    return Markup(md.render(text))

@app.route('/')
def index():
    with open('slides.yaml') as f:
        slides = strictyaml.load(f.read())
    return render_template('slides.html', slides=slides)

@app.route('/pygments.css')
def pygments_style():
    return Response(formatter.get_style_defs(), mimetype='text/css')


app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/reveal.js/plugin': str(Path(__file__).parent / 'reveal.js/plugin'),
    '/reveal.js': str(Path(__file__).parent / 'reveal.js/dist'),
    '/live.js': str(Path(__file__).parent / 'live.js'),
})
