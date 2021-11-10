# Python in Fedora: Integrating a language ecosystem in a distro

Slides for a talk for PackagingCon 2021

by Petr Viktorin & Miro Hrončok

## Slides

The slides do not stand on their own;
please read the script below or watch the recording.
To see the slides:

 1. clone the repository
 2. checkout this branch
 3. install the required Python packages listed in requirements.txt
 4. run Flask
 5. see the presentation in your web browser

For example on Fedora:

```console
$ git clone https://github.com/encukou/slides.git
$ cd slides/2021-11-10-packagingcon
$ python3 -m venv venv
$ . venv/bin/activate
(venv) $ python -m pip install -r requirements.txt
(venv) $ flask run
```

The `flask run` command should give you an URL to visit in your web browser.

## Slides

* Licence for the talk: [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode)
* “Laptop in Pieces” by [Diabolic Preacher on Flickr](https://www.flickr.com/photos/dpreacher/106889272), CC-BY 2.0
* “Abandoned Library” by [Andy Bagley on Flickr](https://www.flickr.com/photos/24402504@N05/8354302511), CC-BY 2.0
* “Packaging Platypus” from [monotreme.club](https://monotreme.club/) (used as intended)
* Icons from [Font Awesome 5](https://fontawesome.com/) and [Devicon](https://devicon.dev/)
* Fedora, Python, PyPI logos belong to the respective projects/owners
* Turbo Framework Copyright (c) 2021 Basecamp; MIT license (see `static/bundled/`)

## Script

This is what we *wanted* to say. We didn't read it word for ford.

---

The language ecosystem is Python, but i hope the ideas from this talk will be relevant to any other scosystem you want to integrate.
And the same goes for the distro: I'll talk about Fedora, and hopefully you can generalize things to another distro.

This word, integrating, is pretty important: when I want to summarize what we do as a distro packagers, I say that

### DISTROS

we integrate software into a cohesive whole.

We take software released by developers, and:

### JOBS

  * **adapt** it to the platform we're building,
    so it works well with all the other parts;
  * we run the **test** suite, tests of dependent packages, and additional checks
    to ensure everything works together;
  * we **handle user reports**: these are often specific to the distro,
    and even if not, users might not know who develops the software
    and how to contact them.
  * We aim to provide **long-term maintenance**. We can care of projects even after their authors move on, and a lot of what we do is for this reason: we want to make it easy for us to maintain software. And that's different from developing software.

Fedora's a volunteer-driven project, so there are no guarantees on reaching
those goals, but the same principles work with paid distros with contracts
on all of that.

Now, some of the more specific jobs we do are

  * curating **metadata**:
    providing consistent naming, descriptions and links to help users
    find software,
  * **licencing** checks: ensuring users know they can use,
    modify and distribute the software wepackage,

  * And we **specify how software is built**:
    * we document the build **dependencies** and we write **build instructions** in machine-readable formats and scripts.
      Anyone can rebuild the software to check our work or to extend it.


This all goes for any distro packager.
We two specialize on integrating <ins>Python</ins> software into Fedora.

### PyPI

Python software is generally distributed through a repository
called the *PythonPackage Index*, or PyPI.
Like a distro, PyPI is a collection of packages, but there are significant
differences between the two.

### DIFFERENCES

* PyPI is *free for all*:
  * Packages are published directly by developers.
  * It's designed to make it simple to publish a package.
* A Distro is *integrated*:
  * Everything in it should work together;
  * it includes a curated set of software.
  * It's harder to maintain, but it's simpler to *use* a package from it.

---

* PyPI covers *one language ecosystem*:
  * Non-Python dependencies installed manually or vendored – duplicated;
  * and PyPI better handles Python-specific issues like virtual environments
    or files that don't depend on the CPU architecture.
* A Distro, on the other hand, covers all languages and packaging mechanisms:
  * Cross-ecosystem dependencies are normal;
  * general packaging issues are handled better. There are many features the Python
    ecosystem recently added or still lacks: weak dependencies, dependency solving,
    license info, ensuring builds correspond to source, audit tools, or
    hand-over of packages whose maintainer went away.

---

* PyPI is *cross-platform*;
* a Distro is, obviously, just one platform.

---

* PyPI packages can be installed into various environments;
  usually you'll have several separate environments on a machine,
  which encourages *pinning* and *vendoring* dependencies.
* Distro packages are typically installed system-wide,
  so they must be compatible with everything else on the system.
  
  (leave out mention of:
    * manual pages
    * desktop "launcher" icons
    * system-wide config (`/etc`)
    )

---

To summarize,

* PyPI's audience is *developers*.
  If you want to install a Python library, or a tool written in Python,
  it's a great choice.
  If you want to publish what you wrote, it's the easiest way.
  If you're a Python developer, we actually recomennd *not* using the
  distro-packaged libraries for your work. Fedora gives you tools
  to create a virtualenv and install into it from PyPI, and then
  it gets out of your way.
* Distros are targeted for *users*.
  If you want to install an app, and don't care much about how it's being developed,
  learning `pip` for Python apps, `npm` for JavaScript apps,
  and Web downloads for browsers is suboptimal.

That makes it worth the time to repackage projects from PyPI as RPMs.

### DP

But still, if you look at the day-to-day work, it's less about the noble goal of integrating software into a cohesive whole.
It's more of taking stuff from PyPI and rebuilding as RPM.

Thankfully, the way we do that is changing.


### PYTHON PACKAGING TOOLS

There are other talks in this conference about the history
of Python packaging, and its painful journey from the hegemony
of a single packaging tool, `Setuptools`, to the current state (and/or future dream)
of multiple tools interoperating via well-defined standards.

Setuptools, which handles package creation, dependency solving, downloads,
installation, runtime introspection and a dozen other tasks, is hard to
maintain, but also hard to replace. That's why individual tasks -- building, downloading, installing, querying metadata -- are isolated
and standardized, so they can be done by a variety of other tools: ones
that are better at a single task.
We have `build` for building, `installer` for installing, `importlib.metadata`
for runtime introspection, `flit` or `poetry` for project maintenance,
and `pip` as a generic frontend calling the other tools -- but any of these
can be replaced by a different implementation.

Altogether, the chaotic mess that prompted the creation of the Packaging Platypus mascot is evolving into a diverse, but friendly and clear ecosystem of tools.

And one of the tools is `pyproject-rpm-macros` – which we're building to
teach `RPMbuild` to understand the Python-specific standards.


### MAPPING THE TWO

Traditionally, in a RPM distro, packaging a Python project meant looking at the upstream package
and transcribing the info into a RPM spec file.
There were tools to help, but with no standards and everything
defined only by the labyrinthine `Setuptools` implementation, tools had to rely
on heuristics and guesswork. They needed lots of hand-holding.

Now, with everything standardized, creating RPMs from Python projects
can be automated like never before.
`pyproject-rpm-macros` follows standards; any guesswork that's still necessary
is an omission or bug in the standards.
And as we find such omissions, we can help fix them, so everyone else benefits as well.
This is a long-term project, but it's on the right track.

Automating the manual drudge leaves distro maintainers free to focus
on tasks that really matter. Rather than spend time
transcribing vaguely specified metadata, we can take the name, version, license, dependencies and build from the upstream package, and spend time on actual *integration* –
adapting software to the larger collection and verifying that it works.

And if it isn't, we can fix all this upstream instead of patching our own copy. This helps all other users.

We've been reporting and fixing issues like:
* packages depending on non-standard implementation details – usually by mistake, like making a typo that happened to work
* undeclared dependencies on a package *almost* everyone already has installed – `setuptools`/`pkg_resources`
* bespoke specification of test dependencies, which were hard to reuse
* removing unneeded dependencies (`importlib.metadata`)

If any metadata changes are necessary, they should be treated the same way
as code patches: explicit downstream modifications.

(XXX give a specific example? or is this too much detail:)

> For example, the graphics library Pyglet comes bundled with a simple image
    backend, `pypng`. The alternatives are more powerful, but hard to build
    or platform-specific.
    On Fedora, bundling is discouraged -- it makes long-term maintenance
    harder -- but being hard to build or platform specific isn't a problem.
    So instead of `pypng`, the Fedora package depends on a full-featured backend,
    `Pillow`, instead.
>
> This change is explicit, like any other patches or tweaks.
>
> The *upstream*'s list of dependencies isn't duplicated in the RPM spec,
    so if a dependency or a description is changed upstream, the change
    should automatically appear the next time there's a Fedora update.
    And it should go through the usual testing and review we do for code.

To make this possible, we must be able to *automatically* convert
upstream metadata to the format that RPM expects.


This isn't always straightforward.
Since RPM supports many ecosystems and languages, the metadata
is necessarily different, and the mapping is not always straightforward.


### NAMING

  We need to map names.
  We add a `python` prefix to prevent conflicts with other ecosystems:

  * `requests` → `python-requests`
  * `python-ldap` → `python-ldap`

  But this isn't always straightforward:

  * `bugzilla` → `python-bugzilla`
  * `python-bugzilla` → `python-bugzilla`  !?!

  * `u-msgpack-python` →`python-u-msgpack-python` ?

  Sometimes, when Python is just an implementation detail, we don't want 
  the prefix:

  * `ansible` → `ansible`

  This is so messy, we decided the Fedora package name is arbitrary.
  There are best practices for deriving it, but they're not hard rules.
  Instead, we took advantage of RPM's' *virtual provides* – essentially, additional
  package names – and created a secondary machine-friendly naming scheme, which all the automation uses:
  
  * `requests` → `python3dist(requests)`

  This looks ugly, but automated dependency solvers don't care.
  And the human-friendly Fedora names can still be used in manual specifications.
  
  Note that by using names from PyPI, we ned to use the PyPI *namespace*,
  which Fedora doesn't control. This takes away some of Fedora's "sovereignity": decisions on the PyPI side, like who can take over an abandoned package, dictate how we do things in Fedora.
  But that's inevitable: when a Python packager puts `requests` in the dependency
  field, they specifically want the package that's named `requests` on PyPI.

Naming is hard.

### VERSIONING

But when it's solved, another problem comes up: version specifications like

`foo > 1.4`


  Python and RPM use different versioning schemes; versions and comparisons
  must be adapted to make RPM work like Python.
 
`foo > 1.0`
 
For example, Python versioning ignores trailing zeros, so we need tostrip them for RPM.

`foo >= 2.0post1`
`foo >= 2.4.0b5`

There's different syntax for pre- and post-releases,

`foo < 2.4`

and the semantics are also different,
so the equivalent version string depends on the operator you use.
The tildes are necessary to avoid installing 2.4 beta.

`foo ~= 2.0`

And unusual operators need overwriting using complex syntax that RPM only added relatively recently.

Thankfully, this is all possible to do – although we're still finding bugs here.

But when version are solved, more problems come up.

### EXTRAS

Optional dependencies work very differently:
  Python uses *extras* while RPM uses *weak dependencies*.
  Thankfully ~~RPM is general enough~~... well, we can twist and bend
  RPM enough to allow extras, through metadata-only subpackages.
  The mechanism to do this automatically is still not there, though.

### Dependency hells & pinning

Another issue for us is pinning and vendoring.

  Our community expects Fedora to integrate new software versions from various upstreams into our repositories quickly,
  but with minimal disruption and in a way that fits nicely with other packages.

  Python packages often pin their dependencies to specific version ranges.
  In virtual environments and small deployments, this isn't a big deal,
  but in Fedora everything is installed to one system and resoled by one global dependency solver.

  Generally, only one version of each package is available in the repository.
  If e.g. `packaging` requires `pyparsing < 3` and `matplotlib` requires `pyparsing >= 3`,
  we need to make some tough choices.
  To a certain degree, we can package multiple versions of `pyparsing` but users cannot install both at the same time.
  
  Hence, we often need to drive porting projects to newer versions of dependencies, or restoring backwards compatiility in the new dependencies.

  Another way upstream packages handle dependencies – especially ones that are hard to install – is vendoring: copying the dependency into the package that uses it.
  Vendoring is very problematic for long-term support.
  For example, applying security patches for a popular library across all distro
  versions and all the recursively vendored copies is a major pain.

### Licenses

  Names and versions are critical in making the software *work*,
  but it's only part of the story.
  Licensing is another.

  Popular minimal licenses essentially say: I made this. Use it, change it, share it, do anything else with it, but keep the author's name on it, and keep the licence text that says you need to do that.
  
  But *including* the license text in Python wheels was an afterthought;
  let alone specifying which files are the license -- that option was only
  added 3 years ago (in PEP 639), and
  many projects still don't use the option.
  
  This is another example of PyPI focusing on developers.
  Licencing isn't a problem for developers: it's the *user* that can get sued
  if a malicious corporation buys the copyright.

I could rant about licences all day,
but let's look at another area of packaging.

### DOCS

Documentation for Python projects is almost always online these days.
Building docs is not standardized at all: it depends on the project and the tools it uses, and you're not really expected to build your own.

The success of projects like Zeal and Dash show that offline docs can be useful.
But at least in Fedora, `/usr/share/doc` feels like an old, forgotten corner of the distro.
Unfortunately, renovating it isn't exactly on top of *our* priority list either.

### Tests

What we do care about is running *tests*.

  Like docs, tests frequently aren't released on PyPI, but unlike docs,
  they are necessary to ensure that software works.

In Fedora, we use RPM check scripts whenever a package is built, and additional integration tests and impact checks to help ensure everything works together.

In Python, running tests is another area that's not standardized at all.

In my opinion:

  * each project should have a main test suite should pass on the upstream CI, in a distro,
    on a developer machine, or anywhere else you want to run it.
    Many projects make it hard to run the test suite outside a single isolated,
    pinned-down environment; this makes them difficult to integrate into any larger system.
  * And then there are linters and code quality checkers, which are fragile -- they report suggestions about formatting rather than hard errors, and they depend on specific tool versions.
    These only help the developers.
    Unlike tests, they *should* only run in an isolated, pinned-down environment:
    if a newer version of a linter changes its mind on how many blank lines
    should be between functions, we don't care.

  There's interesting work to do in these area.

### Descriptions

And finally, descriptions.

  Fedora's package descriptions usually are a few paragraphs at most;
  on PyPI many people put full README files with CI badges and changelogs.
  
  But if that's the only thing a Fedora packager needs to edit to make
  a first-class Fedora package, we'll be happy.

### Back to big picture

While there are issues, we love Python,
and we love the new packaging ecosystem of
multiple tools interoperating via
well-defined standards.
Using those standards, as mindlessly and automatically as possible,
is a nice stress test of how general they are.

If we can reuse upstream metadata as automatically as possible,
we can do what we do for code: package it up for users, check and improve it for everyone, and
treat any adjustments as deliberate patches.


