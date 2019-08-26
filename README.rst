=============
pytest-involve
=============

.. image:: https://img.shields.io/pypi/v/pytest-involve.svg
    :target: https://pypi.org/project/pytest-involve
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-involve.svg
    :target: https://pypi.org/project/pytest-involve
    :alt: Python versions

.. image:: https://travis-ci.org/MisterKeefe/pytest-involve.svg?branch=master
    :target: https://travis-ci.org/MisterKeefe/pytest-involve
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/MisterKeefe/pytest-involve?branch=master
    :target: https://ci.appveyor.com/project/MisterKeefe/pytest-involve/branch/master
    :alt: See Build Status on AppVeyor

`pytest-involve` is a `pytest` plugin for running only tests which cover a given file
or set of files. It's called `pytest-involve` because this involves the normal order of things:
Usually the test set to run is specified and coverage collected based on that set. When `pytest-involve`
is used, instead you specify the file(s) you want to cover, and test files are selected based
on whether they import from those file(s) or not.

TODO: Specify a member or function using the standard :: syntax (this will potentially only
work for top-level members). Also, improve test coverage by a _lot_.

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

* Run unit tests covering specific file(s) via the command line flag `--involving`

Requirements
------------

* `pytest`
* That's it.

Installation
------------

You can install "pytest-involve" via `pip`_ from `PyPI`_::

    $ pip install pytest-involve


Usage
-----

* TODO

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-involve" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/MisterKeefe/pytest-involve/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
