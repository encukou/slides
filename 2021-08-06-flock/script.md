## Intro

Welcome to the Modern Python Packaging Hackfest!
As you might know, the Python Packaging Guidelines were recently rewritten
and there's a bunch of new macros around that can help you simplify Python
packaging for Fedora.

In this workshop, we can look at your spec file and introduce the new macros,
or we can help you package something new in Fedora.


## Python packaging improvements

For a long time, upstream Python packaging was done with `setuptools`.
To build a package, you'd use `python setup.py build`;
to install it, you'd use `python setup.py install`;
and to run these commands, you'd need `setuptools` installed.

However, `setuptools` has its issues.
It's not a good fit for *all* projects,
and yet, it was hard to *not* use it.

There are other tools that can make Python packages,
like `flit` and `poetry`.
They had a rough start, since Python's package landscape
was dominated by `setuptools`,
but `flit`'s simplicity and focus on solving *only the easy cases*
showed a way forward: multiple interoperating tools
that agree on the format of the artifacts they produce
and consume.

And so began the era of standardization: everything `setuptools`
defined implicitly is now written down:

 * how to interpret and compare *version strings* (PEP 440),
 * how project names are normalized for case-insensitive comparison,
 * what a distributed archive containing a project should look like,
 * how a project is built from source,

and so on.

When the data formats are specified, individual tools can be swapped around.
`setuptools` becomes one of many choices, and better alternatives get
a chance to overtake it.

And so, the command to build and install a Python project is no longer
`setup.py install`.
Most people should use `pip install .`, but it's perfectly fine to run another
tool that can read the appropriate metadata, install the necessary dependencies
and run project-specific build system, be it `setuptools`, `flit` or `cmake`.

Fedora now has such tools: instead of `%py_build` and `%py3_setup`,
the old macros that call `setup.py`,
you can use `%pyproject_build` and `%pyproject_install`.

These are named after the new configuration file, `pyproject.toml`,
but they fall back to `setuptools` if the file is missing.

Unfortunately, there are some build systems that do not have the newly
standardized hooks.
If your package uses something else than `setuptools`, `flit` or `poetry`,
we'll be glad to chat about it and see how we can move forward,
but we might not end up with a refreshed specfile.


## Upstream metadata

As we designed the new macros, we considered what a Fedora packager *does*.

Our job as distro packagers is to integrate software into
a larger, cohesive system.

Sometimes that means patching – changing the software a bit to fit the other
parts of the distro;
sometimes a bit of extra configuration is all that's needed.

As part of this system integration, packagers also:

* do quality control – verify that the entire distro and all its parts
  actually work together,
* check licences – verifying that everything can be legally distributed
  and used together, and
* respond to reports from users, since these often need system-specific info
  added before thay're passed on to the "upstream" project itself.
* curate metadata: provide names that don't conflict,
  version numbers that can be compared uniformly,
  and descriptions that fit the distro's style.

And to actually get a piece of software built, they also:

* specify build-time and run-time dependencies,
* write down the commands to build and install software,

The question is, how much of this actually adds value, and how much is
repeating what upstream projects already do?

[crossing off items from the lists:]

Since the requirements of Python projects are now available in
well-specified formats, there's no reason to repeat itthem in the spec file.

Version numbers are now also standardized.
The mechanics of Python versions are a bit different from what RPM needs,
but we can convert automatically and use RPM for dependencies.



Verification – running tests – is not officially standardized,
but the popular (`tox`)[https://tox.readthedocs.io/en/latest]
project aims *to automate and standardize testing in Python* – and allowing
Fedora's use cases fits their mission.
So, we can automate this for most projects.

Licence checks can't be automated, although there are some efforts in this area.
Descriptions currently don't Fedora's unique style upstream,
and names are, well, a can of worms I'll open later.
But still, we can save a lot of the copying data around – and just use
upstream metadata.

Of course, sometimes the metadata needs to be adapted to Fedora,
but the metadata should be treated the same as the code itself:
usually, with patches.
Any patches are technical debt; they should be presented upstream
and ideally eventually fixed there, if that's possible.

Since we aim to not have metadata and dependencies in the spec file,
and each project can use a different build system,
finding *where* Requires & BuildRequires are listed can be inconvenient,
especially if you're maintaining many packages.
Still, a repoquery or grep will usually answer your questions.
Once you switch, you're not likely to go back :)


## Names

Now, names.

Naming is hard.
Python packages have four kinds of names, which you *should* keep as smimilar
as possible, but sometimes it's not possible.

They are:

[table from https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#_naming ]

* the Fedora source package name (or component name),
* the Fedora built RPM name,
* the project name used on PyPI or by pip, and
* the importable module name used in Python.

Usually, the latter two are the same, and for the Fedora ones you add `python-`
or `python3-` prefix, but you might run into complications.

One of those complications is that upstream projects use the PyPI namespace.
If you see `requests >= 2.0` in an upstream Python project,
that means Requests from PyPI.
Allowing alternative namespaces has been discussed upstream,
but so far, no one thinks it's worth their effort to allow it.

And so, the *project name* for Fedora packages MUST match the project on PyPI,
or at least the name needs to be reserved on PyPI to avoid future
duplicates there.
That's a hard requirement in the new guidelines,
and the automation relies on this.
It's not too hard to deal with PyPI, but the Red Hat Python-maint team
is happy to handle it for you if you want.


## Tests

Another new guideline has to do with tests:

* If possible, tests must be run when a package is built (in `%check`).
  Python's compiler doesn't catch very many errors, so tests are essential.
* On the other hand, code style checkers and linters should only be used
  in the upstream project, not in Fedora.
  These usually find things like questionable formatting or too-short
  variable names. A distro is not the place to fix issues like that,
  nor to check it.


## Let's go!

And that's it!
If you're on the workshop, go ahead and show us your package or project.

If you're watching this after the workshop, check out the links:

* The new guidelines:
  https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#_macro_reference
* The *macro reference* in the new guidelines:
* Fedora Change, with a "before & after" spec file example:
  https://fedoraproject.org/wiki/Changes/PythonPackagingGuidelines202x

.. and direct any wuestions to the [Python SIG mailing list](https://lists.fedoraproject.org/archives/list/python-devel@lists.fedoraproject.org/)
or `#fedora-python` on Libera.chat.

