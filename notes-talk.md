
# Python in Fedora: Integrating a language ecosystem in a distro

## Abstract

The Fedora Python SIG and the Python maintenance team at Red Hat
are systems integrators who work at the intersection of two worlds:
a cross-platform ecosystem and a platform open to all kinds of software.

This talk introduces both Python packaging and RPM,
explains why we go through the trouble to repackage Python projects in RPM,
and covers some of the issues we're solving.


## Description

Python packaging is evolving quickly over the past few years,
with a focus on standards that allow cooperation between different tools.
The “traditional” way to package projects – setuptools – is still dominant,
but its new aim is to be just one way to do things, so better competitors
are able to overtake it.

The Python ecosystem is centered on PyPI, the Package Index:
a place where anyone can share their project with the world.
The usual way to install from PyPI is into *virtual environments*,
semi-isolated environments that
don't conflict with each other or the base system (when used well).
Packages from PyPI are generally easy to install on any platform.

RPM is a package format for building a *distro*: collection of packages
that's coherent (designed to work together) and complete
(with everything from the kernel to the GUI apps).
It's used for packaging software written in any language, although
it does have a historical bias for C projects and the Autotools
*configure-make-install* paradigm, and works much better in ecosystems that
care for *distro*-style integration (as opposed to *monorepos*).

RPM (and system packages in general) have several advantages over
Python (and language ecosystems in general): tighter integration with the
system, and common tools for handling packages – installation
(so a non-Pythonista can easily get a Python-based tool/dependency),
auditing delivery pipelines, system integration and integration testing,
and so on.
That makes it worth the time to repackage projects from PyPI as RPMs.

Python packaging's focus on cooperation between different tools
and RPM's focus on combining language ecosystems play together nicely,
with opportinities for collaboration and improvements in both ecosystems.
Our goal in Fedora is to make repackaging a Python project as RPM as
easy as possible. New Python packaging macros and guidelines released
in June 2021 reuse metadata from upstream, leaving packagers to focus on
system integration: applying necessary changes (hopefully ones
that will make it back to the project), running tests (and convincing
people that it's nice to have tests pass in environment other than the
project's CI), integrating non-Python software, and so on.

When bridging the two world, we run into issues with naming, versioning,
licenses, testing, documentation, optional dependencies. Some of which
are solved easily, some of them need more work and discussion.

We hope that the long run, making Fedora and Python work together
helps other distros and language ecosystems as well.

---
---

# Notes

Python in Fedora: Integrating a language ecosystem in a distro

this is a specific account, but should be usable for anyone interested in:

* integrating a language ecosystem in Fedora
* integrating Python in a distro
* integrating a language ecosystem a distro

### DISTROS

We are distro packagers: we integrate software into a cohesive whole.

We take software released by developers, and:

  * (**patching**)
    adapt it to the platform we're building,
    so it works well with all the other parts;
  * (**quality control**)
    run the test suite, tests of dependent packages, and additional checks
    to *ensure* everything works together;
  * we **handle user reports**: these are often specific to the distro,
    and even if not, users might not know who develops the software
    and how to contact them;
  * (**curate metadata**)
    we provide consistent naming, descriptions and links to help users
    find software
  * (**licence checks**) we check licences so users know they can use,
    modify and distribute the open-source software

  * We **specify how software is built**:
    * we document **dependencies** and
    * **build instructions** in machine-readable formats and scripts.
      Anyone can rebuild the software to check our work or to extend it.

  * And we can provide **long-term maintenance**, caring for old versions
    or whole projects even after the authors move on.

Fedora's a volunteer-driven project, so there are no guarantees on reaching
those goals, but the same principles work with paid distros with contracts
on all of that.


mostly cut:

    Fedora is a RPM-based distro.
    RPM is just a container format;
    The problems we solve (and the value we bring) is in integration – making
    every piece of software work with every other piece.
    Still, the day-to-day work is wrangling embedded Bash scripts with RPM macros,

    Like Python, RPM's legacy goes back to FTP'd tarballs.


    ## the C/AUTOTOOLS way (?)

    `./configure`, `make`, `make install`  
    + add `README`!  
    + add “Get a tarball from FTP!”  

    ### PYTHON

    There are other talks in this conference about the long and varied history
    of Python packaging, which goes back to FTP'ing tarballs (which was a pain, so the
    standard library contained most of what you needed), through the hegemony
    of Setuptools (and the failed idea of "eggs" - installing a single zip file),
    standardized installations and the Python Package Index, to the current
    state (and/or future dream) of multiple tools interoperating via well-defined
    standards.

    The Python ecosystem has actually evolved towards something resembling
    `configure`-`make`-`make install`, automating the steps as well:

    * Download the package (by name from a well-known central repository)
    * Get the prerequisites (via machine-readable dependencies, names in the well-known central repository)
    * ~~Configure for the local environment (unnecessary)~~
    * build a "wheel" (zip file + metadata)
    * install (system-wide, or to a venv)

    ### RPM

    RPM build process also mirrors `./configure`, `make`, `make install`,
    with a *spec file*

    * Get sources (stored alongside the spec, somehow)
    * Get the prerequisites (via machine-readable dependencies, names in a central repository)
    * Adapt the sources to the distro (patches, config; ex. add a desktop icon)
    * `%build`
    * `%install`
    * `%check` -- which is sorely missing in the other directories


### DIFFERENCES

We are distro packagers: we integrate <ins>Python</ins> software into a cohesive whole.

Python software is generally distributed through a repository
called the *PythonPackage Index*, or PyPI.
Like a distro, PyPI is a collection of packages, but there are significant
differences between the two.


* PyPI is *distributed*:
  * It's free for all, software is published directly by developers.
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
  * general packaging issues are handled better: some features the Python
    ecosystem recently added or still has in progress (weak deps, dep solving,
    builds correspond to source, license info, audit tools, or
    hand-over of packages whose maintainer went away).

---

* PyPI is *cross-platform*;
* a Distro is, obviously, one platform.

---

* PyPI packages can be installed into various environments;
  usually you'll have several separate environments on a machine,
  which encourages *pinning* specific versions of dependencies
  and *vendoring* – copying a dependency into a project.
* Distro packages are typically installed system-wide,
  and must be compatible with everything else on the system.
  Strict version pinning prevents updating a dependency
  across the system, so we try to avoid that.
  Also, vendoring is problematic for long-term support.
  For example, applying security patches across all distro
  versions and all vendored copies of a library is a major pain.
  
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
  If you're a Python developer, we actually recomennd *not* using the
  distro-packaged libraries for your work. We give you tools
  to create a virtualenv and install into it from PyPI, and then
  get out of your way.
* Distros are targeted for *users*.
  If you want to install an app, and don't care much about how it's being developed,
  learning `pip` for Python, `npm` for JavaScript apps,
  and Web downloads for browsers is suboptimal.

That makes it worth the time to repackage projects from PyPI as RPMs.

We are distro packagers: we ~~integrate software into a cohesive whole.~~
take stuff from PyPI and rebuild as RPM.

And the way we do that is changing.


### PYTHON - TOOLS & STANDARDS

There are other talks in this conference about the history
of Python packaging, and its painful journey from the hegemony
of a single packaging tool, `Setuptools`, to the current state (and/or future dream)
of multiple tools interoperating via well-defined standards.

Setuptools, which handles package creation, dependency solving, downloads,
installation, runtime introspection and a dozen other tasks, is hard to
maintain, but also hard to replace. That's why individual tasks are isolated
and standardized, so they can be done by a variety of other tools: ones
that are better at a single task.
We have `build` for building, `installer` for installing, `importlib.metadata`
for runtime introspection, `flit` or `poetry` for project maintenance,
and `pip` as a generic frontend calling the other tools -- but any of these
can be replaced by a different implementation.

One such implementation is `pyproject-rpm-macros` – tools we're building to
teach `RPMbuild` to understand the Python-specific standards.


### MAPPING THE TWO

Traditionally, packaging a Python project meant looking at the upstream package
and transcribing the info into a RPM spec file.
There were tools to help, but with no standards and everything
defined only by the labyrinthine `Setuptools` implementation, tools had to rely
on heuristics and guesswork. They needed lots of hand-holding.

Now, with everything standardized, creating RPMs from Python projects
can be automated like never before.
`pyproject-rpm-macros` follows standards; any guesswork that's still necessary
is an omission or bug in the standards.
We can fix Fedora's issue in the standards, so everyone else benefits as well.

Automating the manual drudge leaves distro maintainers free to focus
on tasks that really matter. Rather than spend time
transcribing vaguely specified metadata, we spend time on *integration* –
adapting software to the larger collection and verifying that it works.

  * adapting to the target platform ("patching")
  * quality control  (* tests aren't standardized *yet*)
  * handling user reports
  * ~~curating metadata~~ (excl. description, upstream ones are unsuitable)
  * licence checks
  
  * specify how software is built
    * ~~dependencies~~ (only non-Python ones)
    * ~~build instructions/scripts~~

If Fedora can use upstream data directly, any issues we find
can be contributed to the upstream project directly, helping all other users.
We've been reporting and fixing issues like:
* packages mistakenly depending on non-standard implementation details: `pytz>dev`
* undeclared dependencies on a package *almost* everyone already has installed – `setuptools`/`pkg_resources`
* bespoke specification of test dependencies, which is hard to reuse
* removing unneeded dependencies (`importlib.metadata`)

If any metadata changes are necessary, they should be treated the same way
as code patches: explicit downstream modifications.

(XXX give a specific example? or is this too much detail:)
For example, the graphics library Pyglet comes bundled with a simple image
backend, `pypng`. The alternatives are more powerful, but hard to build
or platform-specific.
On Fedora, bundling is discouraged -- it makes long-term maintenance
harder -- but being hard to build or platform specific isn't a problem.
So instead of `pypng`, the Fedora package depends on a full-featured backend,
`Pillow`, instead.

This change is explicit, like any other patches or tweaks.

The *upstream*'s list of dependencies isn't duplicated in the RPM spec,
so if a dependency or a description is changed upstream, the change
should automatically appear the next time there's a Fedora update.
And it should go through the usual testing and review we do for code.

To make this possible, we must be able to *automatically* convert
upstream metadata to the format that RPM expects.


### ISSUES

This isn't always straightforward.
Since RPM supports many ecosystems and languages, the metadata
is necessarily different, and the mapping is not always straightforward.


* (Naming)

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

  This is so messy, we decided the Fedora package name is arbitrary
  (though there are best practices for it).
  We took advantage of RPM's' *virtual provides* – essentially, additional
  package names, and created a secondary, machine-friendly naming scheme:
  
  * `requests` → `python3dist(requests)`
  * ...

  This is ugly, but automated dependency solvers don't care.
  And the human-friendly Fedora names can still be used for manual specification.
  
  Note that by using names from PyPI, Fedora uses the PyPI *namespace*,
  which Fedora doesn't control. This takes away some of Fedora's "sovereignity".
  But that's inevitable: when a Python packager puts `requests` in the dependency
  field, they specifically want the package that's named `requests` on PyPI.

* Versioning

  Python and RPM use different versioning schemes; versions and comparisons
  must be adapted to make RPM work like Python.
  With things like pre-releases and unusual operators, the results sometimes
  look as messy as the names.
  And some of the comparisons need relatively recent versions of RPM.

  a few examples from https://github.com/gordonmessmer/pyreq2rpm/blob/master/tests/test_convert.py:
  * `(['foobar', '<=', '0.0'], 'foobar <= 0'),`
  * `(['foobar', '>=', '2.0.0b5'], 'foobar >= 2~b5'),`
  * `(['foobar', '<=', '2.0.post1'], 'foobar <= 2^post1'),`
  * `(['foobar', '~=', '2.0.post1'], '(foobar >= 2^post1 with foobar < 3)'),`
  * `(['foobar', '<', '2.4.8.0'], 'foobar < 2.4.8~~'),`

* Optional dependencies, in particular, work very differently:

  Python uses *extras* while RPM uses *weak dependencies*.
  Thankfully ~~RPM is general enough~~... well, we can we can twist and bend
  RPM enough to allow extras, through autogenerated metadata-only subpackages.

* XXX Dependency hells & pinning

* Licenses

  Names and versions are critical in making the software *work*,
  but it's only part of the story.
  Licencing is another.

  *Including* license files in Python wheels was an afterthought;
  let alone specifying which files are the license -- that option was only
  added 3 years ago (in PEP 639).

  Popular minimal licenses essentially only require that the license 
  and author name to accompany the software; the fact that this isn't
  always done is another example of PyPI focusing on developers.
  Licencing isn't a problem for developers: it's the *user* that can get sued
  if a malicious megacorp buys the copyright.

* Building *documentation* is not standardized at all.

  This is less important to package – it's all online these days – but
  the success of projects like Zeal and Dash show that offline docs are
  useful.

  Docs frequently aren't released on PyPI, and on Fedora's side,
  `/usr/share/doc` feels like an old, forgotten corner of the distro.

* Running *tests* is not standardized  at all.

  Like docs, tests frequently aren't released on PyPI, but unlike docs,
  they are necessary to ensure that software works.

  IMO:

  * the main test suite should pass anywhere: on the upstream CI, in a distro,
    on a developer machine, (more?).
    (Some tests might be skipped)
    Many projects make it hard to run the test suite outside a single isolated,
    pinned-down environment; this makes a project difficult to integrate into any larger system.
  * linters and code quality checkers are fragile (depend on specific versions),
    and only help the developers.
    These *should* only run in an isolated, pinned-down environment:
    if a newer version of a linter changes its mind on how many blank lines
    should be between functions, we don't care.

  There's interesting work to do in these area.

* Descriptions

  Fedora's package descriptions usually are a few paragraphs at most;
  on PyPI people put README files with CI badges and changelogs.
  
  But if that's the only thing a Fedora packager needs to edit to make
  a first-class Fedora package, we'll be happy.

### Back to big picture

The Python packaging ecosystem aims for multiple tools interoperating via
well-defined standards.
Using those standards, as mindlessly and automatically as possible,
is a nice stress test of how general they are.

If we can reuse upstream metadata as automatically as possible,
we can do what we do for code: check and improve it for everyone, and
treat any adjustments as deliberate patches.









