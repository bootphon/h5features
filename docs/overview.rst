================
Package overview
================

The h5features package provides **efficient reading and writing of
features data** to/from the `HDF5`_ binary file format.  It is a
wrapper on `h5py`_ and and is used for exemple in the `ABXpy`_
package.

It is designed with the following objectives in mind:

* Compliant with very large datasets.

* Asymetric usage with optimized read.

* Well structured features data.

Following sections brifly introduce the new user to the h5features
package and it's recommended usage.

How it works ?
==============

h5features data format
----------------------

Basically the h5features data is composed of three componants:

* a set of **items** represented by their names (speech wav files for
  exemple),

* for each item, some attached **features** as numpy arrays (a set of
  Fourier vectors over a time window for exemple).

* some **times** information attached to features, as numpy arrays (the
  center of each Fourier time window for exemple).


h5features file structure
-------------------------

A h5features file is simply a `HDF file
<http://docs.h5py.org/en/latest/quick.html>`_ with a custom
structure. Given *h5features* the name of the h5features root group in
the it, the file is organized as follow:

- *file/h5features/*

  - *items*
  - *times*
  - *features*
  - *index*

Basic usage
===========

.. include:: ../exemple.py
   :code: python

.. _h5py: http://docs.h5py.org
.. _HDF5: http://hdfgroup.org
.. _ABXpy: https://github.com/bootphon/ABXpy
