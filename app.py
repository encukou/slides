from pathlib import Path
from itertools import count

from flask import Flask, render_template, url_for, redirect

app = Flask(__name__)

template_path = Path(app.template_folder)

for i in count():
    path = (template_path / f'slide{i}.html')
    print(path)
    if not path.exists():
        NUM_SLIDES = i
        break
print(f'There are{i} slides')

@app.route('/')
def index():
    return redirect(url_for('slide', n=0))

@app.route('/<int:n>')
def slide(n):
    if n < 0:
        return redirect(url_for('slide', n=0))
    if n >= NUM_SLIDES:
        return redirect(url_for('slide', n=NUM_SLIDES-1))
    return render_template(
        f'slide{n}.html',
        n=n,
        num_slides=NUM_SLIDES,
    )

