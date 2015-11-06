================
Package overview
================

.. highlight:: python
.. note::

   In the following code samples, the h5features package is imported as::

     import h5features as h5f

Description
===========

The h5features package allows you to easily **interface your code
with a HDF5 file**. It is designed to efficiently **read and write
large features datasets**. It is a wrapper on `h5py`_ and and is
used for exemple in the `ABXpy`_ package.

* Package organization:

    The **main classes** composing the package are ``h5f.Writer`` and
    ``h5f.Reader``, which respectively write to and read from HDF5
    files, and ``h5f.Data`` which interface that data with your code.

* Data structure:

    The **h5features data** is structured as a follows

    * a list of **items** represented by their names (files names for
      exemple),

    * for each item, some attached **features** as a numpy array,

    * some **labels** information attached to features, also as numpy arrays.

* File structure:

    In a h5features file, **data is stored as a HDF5 group**.  The
    underlying group structure directly follows data organization. A
    h5features *group* mainly stores a *version* attribute and the
    following datasets: *items*, *labels*, *features* and *index*.


Basic usage
===========

.. include:: ../exemple.py
   :code: python

.. _h5py: http://docs.h5py.org
.. _HDF5: http://www.hdfgroup.org/HDF5/
.. _ABXpy: https://github.com/bootphon/ABXpy
