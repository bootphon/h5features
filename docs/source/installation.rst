.. _install:

============
Installation
============

Getting the source
==================

The source code is publicly available at
https://github.com/mmmaat/h5features2 ::

    $ git clone https://github.com/mmmaat/h5features2.git

.. note::

   In what follows we suppose your current directory is the root of
   the h5features package you just cloned::

     $ cd h5features2

Installing
==========

`h5features` relies on external dependencies you need to install
first:

* h5py 2.3.0 or newer
* NumPy 1.8.0 or newer
* scipy 0.13.0 or newer
* numpydoc
* pytest
* sphinx

The simplest way to do this is using *pip*::

    $ [sudo] pip install -r requirements.txt

Then to install the package itself, you can use either *pip* or
*setuptools*.

* Using *pip*::

    $ [sudo] pip install .

* Using *setuptools*::

    $ python setup.py build
    $ [sudo] python setup.py install


Testing
=======

You can follow the build status of the package at
https://travis-ci.org/mmmaat/h5features2 .

The h5features test suite is runned by `pytest`_. Simply run it from
the root directory::

  $ py.test


Building the documentation
==========================

The documentation (the one you are currently reading) is builded with
`sphinx`. The main HTML page is generated to
*docs/build/html/index.html*::

  $ python setup.py build_sphinx

Or::

  $ cd docs && make html

.. _pytest: http://pytest.org/latest/
