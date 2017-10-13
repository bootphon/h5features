.. _install:

============
Installation
============

Getting the source
==================

The source code is publicly available at
https://github.com/bootphon/h5features ::

    $ git clone https://github.com/bootphon/h5features.git

.. note::

   In what follows we suppose your current directory is the root of
   the h5features package you just cloned::

     $ cd h5features

Installing
==========

Dependancies
------------

`h5features` relies on external dependencies. The setup script should
install it automatically, but you may want to install it manually. The
required packages are:

* h5py 2.3.0 or newer
* NumPy 1.8.0 or newer
* scipy 0.13.0 or newer

On Debian/Ubuntu::

  sudo apt-get install python3-numpy python3-scipy python3-h5py

Using Python anaconda::

  conda install numpy scipy h5py

Setup
-----

To install the package, run::

    python setup.py build
    [sudo] python setup.py install


Testing
=======

This package is continuously integrated with travis. You can follow
the build status `here <https://travis-ci.org/bootphon/h5features>`_.

For testing it on your local machine, make sure you have `pytest` installed::

  pip install pytest

Then simply run from the root directory::

  pytest -v ./test


Building the documentation
==========================

The documentation (the one you are currently reading) is builded with
`sphinx`. The main HTML page is generated to
*docs/build/html/index.html*::

  pip install Sphinx mock sphinx_rtd_theme

  python setup.py build_sphinx

Or::

  cd docs && make html

.. _pytest: http://pytest.org/latest/
