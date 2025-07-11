Build and install
=================

Python installation
-------------------

h5features can be installed from PyPI with::

    pip install h5features

h5features requires Python >= 3.12 and depends on ``numpy``. Pre-built wheels are
available for Linux x86-64 (with glibc 2.34 or later), macOS arm64, and Windows x86-64.

Build from source
-----------------

Build requirements
~~~~~~~~~~~~~~~~~~

* The `hdf5>=1.10 <https://www.hdfgroup.org/solutions/hdf5>`_ library.
* A C++ compiler with C++17 support.

Optional:

* The `cmake>=3.12 <https://cmake.org>`_ build system to build only the C++ library.
* The `boost>=1.55 <https://www.boost.org>`_ library (Boost.Test and Boost.Filesystem) for the test suite of the C++ library.
* The `doxygen <https://www.doxygen.org>`_ tool to build the documentation.

On Ubuntu install those dependencies with::

    apt install git libhdf5-dev build-essential cmake libboost-test-dev libboost-filesystem-dev doxygen

Python API
~~~~~~~~~~

First, clone the `h5features repository <https://github.com/bootphon/h5features>`_::

    git clone --recursive https://github.com/bootphon/h5features.git
    cd h5features

Then simply build and install the h5features package with your favorite build frontend::

    pip install .

Run the tests with::

    pytest


C++ API
~~~~~~~

Similarly, clone the `h5features repository <https://github.com/bootphon/h5features>`_::

    git clone --recursive https://github.com/bootphon/h5features.git
    cd h5features

In order to only build the C++ h5features library, create a ``build`` directory
(to store intermediate and compiled files) and run ``cmake`` from it and
finally compile the project::

    mkdir -p build && cd build
    cmake .. && cmake --build . -j

Install with::

    make install

.. note::

   By default *h5features* is installed to ``/usr/local`` on UNIX and
   ``C://Program Files/h5features`` on Windows. To install it in another
   directory use the following option to cmake::

        cmake -DCMAKE_INSTALL_PREFIX=<installation path> ..


The compilation of the C++ test suite is not included by default in the cmake
configuration. To enable it, you first need to have the
`boost>=1.55 <https://www.boost.org>`_ library available.

Run cmake with the ``-DH5FEATURES_BUILD_TEST=ON`` option, then compile the project and
execute the tests with ``make test``::

    cmake -DH5FEATURES_BUILD_TEST=ON .. && cmake --build . -j
    make test


Build the documentation
~~~~~~~~~~~~~~~~~~~~~~~

Build the C++ API reference with ``doxygen`` and the full documentation with ``sphinx``
using the following commands::

	doxygen doc/Doxyfile
	uv run --group doc sphinx-build -b html doc doc/build

.. note::

    The ``conf.py`` and ``Doxyfile`` files are configured so that the build
    commands are invoked from the root directory of the project.