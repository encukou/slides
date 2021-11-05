# packaging-con.org proposal

* Title: Python in Fedora: Integrating a language ecosystem in a distro

* Session type: Talk (20 minutes)

## Abstract (max 200 words)

The Fedora Python SIG and the Python maintenance team at Red Hat
are systems integrators who work at the intersection of two worlds:
a cross-platform ecosystem and a platform open to all kinds of software.

This talk introduces both Python packaging and RPM,
explains why we go through the trouble to repackage Python projects in RPM,
and covers some of the issues we're solving.


## Description (optional) (max 500 words)

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



## Notes (optional) (for organizers)

If someone else has a talk about Python or RPM packaging in general,
it would be great to know about them so I can adjust this talk,
and possibly to be scheduled after them.


## Details

* Recording: allowed
* Image (JPG): —
* Additional speaker (e-mail): mhroncok@redhat.com
