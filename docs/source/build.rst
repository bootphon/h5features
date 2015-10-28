.. _install:

Installation
============

Getting the source
------------------

The source code is publicly available on GitHub at
https://github.com/mmmaat/h5features2 ::

    $ git clone https://github.com/mmmaat/h5features2.git

.. note::

   In what follows we suppose your current directory is the root of
   h5features::

     $ cd h5features2

Dependancies
------------

h5features relies on external packages you need to install:

* h5py 2.3.0 or newer
* NumPy 1.8.0 or newer
* scipy 0.13.0 or newer
* numpydoc

The simplest way to do this is using *pip*::

    $ pip install -r requirements.txt

Installing
----------

You can use either *pip* or *setuptools*.

* Using *pip*::

    $ [sudo] pip install .

* Using *setuptools*::

    $ python setup.py build
    $ [sudo] python setup.py install

Running the test suite
----------------------

The h5features test suite is runned by `pytest`_, so make sure it is
installed on yous system::

  $ pip install pytest

Then simply run it from the root directory::

  $ py.test

Building the documentation
--------------------------

The documentation is builded with *sphinx*::

  $ pip install sphinx

Then to build the project documentation (the one you are currently
reading), run::

  $ cd docs
  $ make html

The main HTML page is generated to *docs/build/html/index.html*

.. _pytest: http://pytest.org/latest/
