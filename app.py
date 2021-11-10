from pathlib import Path
from itertools import count

from flask import Flask, render_template, url_for, redirect, g

app = Flask(__name__)

template_path = Path(app.template_folder)

for i in count():
    path = (template_path / f'slide{i}.html')
    print(path)
    if not path.exists():
        SLIDE_COUNT = i
        break
print(f'There are {i} slides')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/<int:slide_num>')
def first_fragment(slide_num):
    return redirect(url_for('slide', slide_num=slide_num, fragment_num=0))

@app.route('/<int:slide_num>/<int:fragment_num>')
def slide(slide_num, fragment_num):
    if slide_num < 0:
        return redirect(url_for('slide', slide_num=0, fragment_num=fragment_num))
    if slide_num >= SLIDE_COUNT:
        return redirect(url_for('slide', slide_num=SLIDE_COUNT-1, fragment_num=fragment_num))
    if fragment_num < 0:
        return redirect(url_for('slide', slide_num=0, fragment_num=0))
    g._current_fragment = 0
    g.fragment_num = fragment_num
    return render_template(
        f'slide{slide_num}.html',
        slide_num=slide_num,
        slide_count=SLIDE_COUNT,
    )

@app.template_global()
def next_fragment():
    g._current_fragment += 1
    return g._current_fragment <= g.fragment_num

@app.template_global()
def reset_fragment(value=0):
    g._current_fragment = value
    return ''
