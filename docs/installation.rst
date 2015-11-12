.. _install:
.. highlight:: bash

============
Installation
============

Getting the source
==================

The source code is publicly available at
https://github.com/mmmaat/h5features ::

    $ git clone https://github.com/mmmaat/h5features.git

.. note::

   In what follows we suppose your current directory is the root of
   the h5features package you just cloned::

     $ cd h5features

Installing
==========

To install the package, run::

    $ python setup.py build
    $ [sudo] python setup.py install

`h5features` relies on external dependencies. The setup script should
install it automatically, but you may want to install it manually. The
required packages are:

* h5py 2.3.0 or newer
* NumPy 1.8.0 or newer
* scipy 0.13.0 or newer
* pytest
* sphinx

Testing
=======

This package is continuously integrated with travis. You can follow
the build status `here <https://travis-ci.org/mmmaat/h5features>`_.
For testing it on your local machine, simply run from the root
directory::

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
