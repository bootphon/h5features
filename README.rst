.. image:: https://readthedocs.org/projects/h5features/badge/?version=master
   :target: http://h5features.readthedocs.org
   :alt: Documentation Status

.. image:: https://travis-ci.org/bootphon/h5features.svg?branch=master
    :target: https://travis-ci.org/bootphon/h5features

==========
h5features
==========

.. highlight:: bash

The h5features **python package** provides easy to use and efficient
storage of **large features data** on the HDF5 binary file format.


Installation
------------

The package depends on *numpy*, *scipy* and *h5py* (automatically
installed by the setup script). Install it with::

  $ python setup.py build && python setup.py install


Documentation
-------------

* See the complete documentation `online
  <http://h5features.readthedocs.org>`_

* Or build it with::

    $ pip install Sphinx
    $ cd docs && make html

  The home page of the compiled documentation is
  ``docs/_build/html/index.html``.

Test
----

The package comes with a unit-tests suit. To run it, first install *pytest* on your Python environment::

  $ pip install pytest

Then run the tests with::

  $ pytest
