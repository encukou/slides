## Intro

...


## Distro Packaging

In the old days, software had `README`, `BUILDING` or `INSTALL` files with a list of dependencies, hints onn how to get those dependencies, and instructions for configuring, building and installing the software.
Look at `rpm` today: the `INSTALL `file lists `popt`, `debugedit`, `lua` and so on, along with instructions on how to get it. Later there are compilation instructions, installation instructions and some further discussion.

The `INSTALL` file is human-readable documentation for a manual process.
And like any manual process, people wanted to make it less manual.
There are two ways to do that:

- standardize on a single tool, or
- describe the process in a machine-readable way  (XXX)

The `rpm` project, like most C-based tools,
has you run `./configure`, `make` and `make install`,
the de-facto standard way to get a compiled software onto the system.

These commands use the de-facto standard GNU Autotools,
an extremely powerful ecosystem developed over the last 30 years,
with the vague goal of allowing you to build any software on any system.
The sheer power of what Autotools can do is staggering – but unfortunately,
so is the complexity.
Even more unfortunately, the individual tools are tied so closely together,
it's hard to change them.
There'll always be a project that relies on an otherwise useless feature check,
or a detail of an arcane macro language.
Features never get removed.
The system can never simplified, it can only grow more complex.

There are many other tools that do the same as Autotools,
from `scons` to `cmake`,
each with its own pros and cons.
None of them is as powerful as Autotools,
but for projects that don't need that power,
they're often a good fit.

So sometimes, to install a software,
you need other commands than just `./configure`,
`make` and `make install`.

Naturally, those commands write into a script.
Usually, the script is no longer cross-platform,
but only usable in a limited, (shall I say) controlled environment.
And so, distributions were born.
Some of these distros, like Arch or Debian, literally have
a shell script for each piece of software – with a bunch of tools
to ease common tasks.
Fedora uses RPM, which builds from spec files – somewhat
more complex collections of metadata and shell scripts.

A packager integrates a piece of software into the distro – a cohesive
collection of disparate projects.
Sometimes that means changing the project a bit to fit the other
parts of the distro;
sometimes a bit of extra configuration is all that's needed.

As part of *system integration*, packagers also:

* do quality control – verifying that the entire distro and all its parts
  actually work together,
* check licences – verifying that everything can be legally distributed
  and used together, and
* respond to reports from users, since they ofteh need system-specific info
  added before thay're passed on to the "upstream" project itself.
* curate metadata: provide names that don't conflict,
  version numbers that can be compared uniformly,
  and descriptions that fit the distro's style.

In addition, to actually get a piece of software built, they also:

* specify *build-time* and *run-time* dependencies,
* write down the commands to build and install software,



## Python packaging

But, you say isn't this supposed to be about packaging Python?

It is, and so, let me tell you a very similar story about Python packaging.

In the old days, all reusable software written for Python was part of
Python's standard library.
This didn't scale, of course.
Soon, releases of Python projects started appearing on the internet.
The installation process and tools for these were usually based
on Python itself – a `setup.py` script invoking tools from
the `distutils` library.

When the external projects needed modules that weren't part of the
standard library, they included human-readable instructions
for getting those downloaded.
Installing was easy enough – just run `setup.py install`,
but downloading grew cumbersome, especially with projects that needed
multiple dependencies,
each of which could have yet more dependencies themselves.
The `setuptools` project, a layer on top of `distutils`
solve these problems.
The `easy_install` tool it provided lived up to its name:
it automatically downloaded dependencies from a webpage containing links
to Python projects.
The most complete webpage, pypi.org, was chosen as a default;
others mostly died off.

As far as Python packaging is concerned, `setuptools` does everything,
and what it doesn't do can be added as an extension.
Finding platform-specific dependencies?
Installing projects as zip files?
Building RPM packages?
Building extension modules written in Fortran?
Finding information at runtime?
There's a way to do it.

Unfortunately, `setuptools` doesn't have a well-defined API.
Extensions for the weirder use cases need to reach deep into the internals
and rely on little details.
There'll always be a project that relies on an undocumented function,
or a detail of an arcane class hierarchy.
Features never get removed.
The system can never simplified, it can only grow more complex.

There have been efforts to fork `setuptools` or `distutils` and
restructure them, but they ultimately failed.
Replacing `setuptools` is a hard task.
The one significant intance of reducing setuptools' scope was the installer:
the independent `pip` is now more popular and much better maintained, and
the `easy_install` command was removed in January {2021}.

But some people started building other tools that can make Python packages,
like `flit` and `poetry`.
Each has its own pros and cons.
None of them is as powerful as `setuptools`,
but for projects that don't need that power,
they're often a good fit.

The issue these projects had is that Python's package landscape
was dominated by `setuptools`.
To install a package, it needed to be in the `sdist` or `egg` format,
which weren't formally defined – it was *whatever `setuptools` creates*.

Even so, `flit`'s simplicity and focus on solving *only the easy cases*
showed a way forward: there could be multiple tools,
and as long as they agree on the format of the artifacts they produce
and consume, they could all co-exist and thrive.
And if `setuptools` itself can be broken into pieces that comminicate
using well-defined protocols, perhaps it'll no longer be a nightmare
to maintain it.

And so began the era of standardization: everything `setuptools`
defined implicitly is now written down:

 * how to interpret and compare *version strings* (PEP 440),
 * how project names are normalized for case-insensitive comparison,
 * what a distributed archive containing a project should look like,
 * how a project is built from source,

and so on.
When the data formats are specified, tools that use them can be swapped.
`setuptools` becomes one of many choices, and better alternatives get
a chance to overtake it.


And so, the command to build and install a Python project is no longer
`setup.py install`.
Most people use `pip install .`, but it's perfectly fine to run another tool
that can read the appropriate metadata, install the necessary dependencies
and run project-specific build system, be it `setuptools`, `flit` or `cmake`.


## Fedora

And Fedora now has such a tool.

Taking advantage of the standardization, we want to solve some of the more
tedious tasks the maintainers need to do. At least in the Python ecosystem.

So, for Python packages, spec files can now hopefully be very boring,
with alll the interesting things taken directly from upstream:

* XXX specify *build-time* and *run-time* dependencies,
* XXX write down the commands to build and install software,
* XXX etc - diagram
* (run tests)

All these things now taken from upstream.
Of course, sometimes the metadata needs to be adapted to Fedora,
but that should be done like with the code itself:
any patches are technical debt that should be presented upstream
and eventually fixed there, if that's possible.

It also means that this data is no longer stores in the spec file,
but in the source archive.
Since each project can use a different build system,
finding *where* Requires & BuildRequires are listed can be inconvenient,
especially if you're maintaining many packages.
Still, a grep will usually answer your questions.

Another issue is the namespace that upstreams use.
When you see `requests > 2.0` in a `setup.py` file,
the `requests` doesn't mean the Fedora package `python3-requests`,
but the `requests` package available on PyPI.
Since Fedora names can be quite arbitrary, we use virtual Provides
like `python3.10(requests)`, which correspond to the name in the
Python metadata.
Under the new guidelines, these names *must* correspond to the names on PyPI
– otherwise we couldn't use the upstream names and would have to have some
kind of translation layer.
However, using someone else's namespace does mean that we lose some autonomy:
Python projects in Fedora must be registered on PyPI,
or we at least need to reserve the name.
It's not hard to do that, but the Red Hat Python-maint team
is happy to handle it for you if you want.

Another new guideline has to do with tests:

* If possible, tests must be run when a package is built (in `%check`).
  Python's compiler doesn't catch very many errors, so tests are essential.
* On the other hand, code style checkers and linters should only be used
  in the upstream project, not in Fedora.
  These usually find things like questionable formatting or too-short
  variable names. A distro is not the place to fix issues like that,
  nor to check it.








## Python?





stdlib
package index
distutils
setuptools
easy_install
pip

virtualenv
venv

pipenv
poetry
flit

pep 517 -- pyproject.toml












---

variables are a dict

