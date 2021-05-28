.. image:: https://readthedocs.org/projects/h5features/badge/?version=master
   :target: http://h5features.readthedocs.org
   :alt: Documentation status

.. image:: https://travis-ci.org/bootphon/h5features.svg?branch=master
    :target: https://travis-ci.org/bootphon/h5features
    :alt: Tests status

.. image:: https://codecov.io/gh/bootphon/h5features/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/bootphon/h5features
    :alt: Coverage status

.. image:: https://anaconda.org/coml/h5features/badges/version.svg
   :target: https://anaconda.org/coml/h5features
   :alt: Anaconda

==========
h5features
==========

The h5features **python package** provides easy to use and efficient
storage of **large features data** on the HDF5 binary file format.


Installation from conda
-----------------------

``conda install -c coml h5features``


Installation from pip
---------------------

``pip install h5features``


Installation from sources
-------------------------

* **dependencies**

  The package depends on *numpy*, *scipy* and *h5py*. They can be
  automatically installed by the setup script but it takes a long time
  (full compilation). You may want to install the dependancies through
  your system package manager.

  On Debian/Ubuntu::

    sudo apt-get install python3-numpy python3-scipy python3-h5py

  Using Python anaconda::

    conda install numpy scipy h5py

* **h5features**

  Install it from the sources with::

    python setup.py build && python setup.py install


Documentation
-------------

* See the complete documentation `online
  <http://h5features.readthedocs.org>`_

* Or build it with::

    pip install Sphinx
    cd docs && make html

  The home page of the compiled documentation is
  ``docs/_build/html/index.html``.

Test
----

The package comes with a unit-tests suit. To run it, first install *pytest* on your Python environment::

  pip install pytest

Then run the tests with::

  pytest -v ./test
