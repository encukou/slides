https://www.flickr.com/photos/24402504@N05/8354302511
https://www.flickr.com/photos/tirrell/111707059

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

## Notes

Python in Fedora: Integrating a language ecosystem in a distro

this is a specific account, but should be usable for anyone interested in:

* integrating a language ecosystem in Fedora
* integrating Python in a distro
* integrating a language ecosystem a distro

### DISTROS

We are distro packagers: we integrate software into a cohesive whole.

  * patching
  * quality control
  * handle user reports
  * curate metadata

  * specify how software is built
    * dependencies
    * build instructions/scripts

  * long-term maintenance


cut:

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
    of Python packaging, going back to FTP'ing tarballs (which was a pain, so the
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

* PyPI -- distributed
  * free for all, published directly by developers
  * simple to publish a package
* Distro -- integrated
  * everything should work together
  * simple to use a package

---

* PyPI -- one language ecosystem
  * non-Python dependencies installed manually
  * better handles Python-specific issues (venvs, noarch)
* Distro -- covers all languages and packaging mechanisms
  * no tight support
  * better handling of general packaging issues (weak deps, dep solving,
    builds correspond to source, license info, audit tools)

---

* PyPI -- cross-platform
* Distro -- is one platform

---

* PyPI -- installs to "virtual environments"
* Distro -- typically system-wide
  * manual pages
  * desktop "launcher" icons
  * system-wide config (`/etc`)

---

* PyPI -- designed for virtual environments, pinning
* Distro -- each package in one version, coordinated updates


### MAPPING THE TWO

We are distro packagers: we ~~integrate software into a cohesive whole.~~
take stuff from PyPI and rebuild as RPM.

Traditionally, this meant looking at the upstream package and transcribing
the info into a RPM spec file.
There were tools to help, but with no standards and everything
defined by the labyrinthine `Setuptools` implementation, they were fragile
and needed lots of hand-holding.

Now, with everything standardized, creating RPMs from Python projects
can be automated like never before.
The Python packaging ecosystem is explicitly built for multiple interoperating
tools; *`rpmbuild` with `pyproject-rpm-macros`* is one of them.

Automating the manual drudge leaves distro maintainers free to focus
on tasks that really matter:

  * adapting to the target platform ("patching")
  * quality control  (* tests aren't standardized *yet*)
  * handling user reports
  * ~~curating metadata~~ (excl. description, upstream ones are unsuitable)

  * specify how software is built
    * ~~dependencies~~ (only non-Python ones)
    * ~~build instructions/scripts~~




### ISSUES

But the mapping is not always straightforward.

* Naming

  * `requests` → `python-requests`
  * `python-ldap` → `python-ldap`

  * `bugzilla` → `python-bugzilla`
  * `python-bugzilla` → `python-bugzilla`  !?!
 
  * `ansible` → `ansible`

* Versioning

  Python and RPM use different versioning schemes; versions and comparisons
  must be adapted to make RPM work like Python.

  a few examples from https://github.com/gordonmessmer/pyreq2rpm/blob/master/tests/test_convert.py:
  * `(['foobar', '<=', '0.0'], 'foobar <= 0'),`
  * `(['foobar', '>=', '2.0.0b5'], 'foobar >= 2~b5'),`
  * `(['foobar', '<=', '2.0.post1'], 'foobar <= 2^post1'),`
  * `(['foobar', '~=', '2.0.post1'], '(foobar >= 2^post1 with foobar < 3)'),`
  * `(['foobar', '<', '2.4.8.0'], 'foobar < 2.4.8~~'),`

* Licenses

  *Including* license files in Python wheels was an afterthought;
  let alone specifying which files are the license.

  note?
    Popular minimal licenses essentially only require that the license 
    and author name to accompany the software; the fact that this isn't done
    tells you something about the state of licensing on developer-focused
    repositories like PyPI.
    This isn't a problem for developers: it's the *user* that can get sued
    if a malicious megacorp buys the copyright.

* Optional dependencies work very differently:

  Python uses *extras* while RPM uses *weak dependencies*.
  Thankfully ~~RPM is general enough to allow extras~~
  we can twist and bend RPM enough to allow extras.

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
  * linters and code checkers are fragile (depend on specific versions),
    and only help the developers.
    They should only run in the upstream CI (and on developer machines).

  There's interesting work to do in these area.

* Descriptions

  Fedora's package descriptions usually are a few paragraphs at most;
  on PyPI people put README files with CI badges and changelogs.


### Back to big picture

The Python packaging ecosystem aims for multiple tools interoperating via
well-defined standards.
Using those standards, as mindlessly and automatically as possible,
is a nice stress test of how general they are.

It also frees Fedora packagers to *adapt* and *verify* software,
rather than 




