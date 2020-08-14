Installation
============

Installation from sources
-------------------------

Dependencies
~~~~~~~~~~~~

The following dependencies need to be installed in order to install ``h5features``:

* `git <https://www.git-scm.com/>`_ to clone the source code.

* A recent C++ compiler supporting the ``C++17`` standard (tested with *gcc-9*).

* The `hdf5>=1.10 <https://www.hdfgroup.org/solutions/hdf5>`_ library.

* The `boost>=1.55 <https://www.boost.org>`_ library.

* A ``python3`` interpreter (to build the documentation and the Python API).

* The `cmake>=3.10 <https://cmake.org>`_ build system.


On Ubuntu install those dependencies with::

    sudo apt install git build-essential libhdf5-dev libboost-dev python3 cmake


Compilation and installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, clone the ``h5features`` repository from github and go to its root
directory::

    git clone --recursive https://github.com/bootphon/h5features.git
    cd h5features

Then create a ``build`` directory (to store intermediate and compiled files) and
run ``cmake`` from it (alternatively you can use ``cmake-gui`` to easily
customize build options) and finally compile the project::

    mkdir -p build
    cd build
    cmake ..
    make  # or "make -j4" to speed up compilation using 4 CPU cores


Test suite
~~~~~~~~~~

The compilation of the test suite is not included by default in the cmake
configuration. To enable it, run it with the ``-DH5FEATURES_BUILD_TEST=ON``
option, then compile the project and execute the tests with ``make test``::

    cmake -DH5FEATURES_BUILD_TEST=ON ..
    make
    make test


Documentation
~~~~~~~~~~~~~

The compilation of the documentation (the one you are currently reading) is not
included by default in the cmake configuration. To enable it, tun it with the
``-DH5FEATURES_BUILD_DOC=ON`` option and build the docs in html with ``make doc``::

    cmake -DH5FEATURES_BUILD_DOC=ON ..
    make doc

The documentation website is available at ``build/doc/html``.
