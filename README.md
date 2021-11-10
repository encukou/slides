Slides for a talk for PackagingCon 2021

by Petr Viktorin & Miro Hrončok

To see the slides:

 1. clone the repository
 2. checkout this branch
 3. install the required Python packages listed in requirements.txt
 4. run Flask
 5. see the presentation in your web browser

For example on Fedora:

```console
$ git clone https://github.com/encukou/slides.git --branch packagingcon
$ cd slides
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ python -m pip install -r requirements.txt
(venv) $ flask run
```

The `flask run` command should give you an URL to visit in your web browser.

* Licence for the talk: [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode)
* “Laptop in Pieces” by [Diabolic Preacher on Flickr](https://www.flickr.com/photos/dpreacher/106889272), CC-BY 2.0
* “Abandoned Library” by [Andy Bagley on Flickr](https://www.flickr.com/photos/24402504@N05/8354302511), CC-BY 2.0
* “Packaging Platypus” from [monotreme.club](https://monotreme.club/) (used as intended)
* Icons from [Font Awesome 5](https://fontawesome.com/) and [Devicon](https://devicon.dev/)
* Fedora, Python, PyPI logos belong to the respective projects/owners
* Turbo Framework Copyright (c) 2021 Basecamp; MIT license (see `static/bundled/`)
