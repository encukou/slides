"""Use urwid.html_fragment to convert the slides to HTML
"""

import sys

import yaml
import urwid
from urwid import html_fragment

from slides import SlideLoop


template = """
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <style>
            body {
                font-family: monospace;
                background-color: #AAA;
                text-align: center;
            }
            .slide {
                page-break-after: always;
            }
        </style>
    </head>
    <body>
        {}
    </body>
</html>
"""


def main(slidespec):
    loop = SlideLoop(slidespec)
    palette = list(loop.palette)
    slides = loop.slides
    size = 41, 17
    generator = html_fragment.HtmlGenerator()
    generator.set_terminal_properties(256)
    generator.register_palette(palette)
    for slide in slides:
        widget = slide(getattr(slide, 'subslide_count', 0))
        for i in range(40):
            canvas = widget.render(size)
        generator.draw_screen(size, canvas)

    outfile = sys.stdout
    templ_start, templ_end = template.split('{}')
    outfile.write(templ_start)
    for fragment in html_fragment.screenshot_collect():
        outfile.write('<div class="slide">')
        outfile.write(fragment)
        outfile.write('</div>')
    outfile.write(templ_end)
    outfile.flush()


if __name__ == '__main__':
    with open('slides.yaml') as slide_file:
        main(yaml.safe_load(slide_file))
