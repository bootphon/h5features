.. _usage:

================
Package overview
================


The h5features package provides **efficient read and write of
features** to/from the `HDF5`_ binary file format.  It is a wrapper on
`h5py`_ and and is used for exemple in the `ABXpy`_ package.

It is designed whith the following objectives in mind:

* Deals with large amount of numerical data (e.g. a
  speech corpus).

* Asymetric usage (you write once and read a lot), optimized reading.

* Well structured features data (see below).


Following sections brifly introduce the new user to the h5features
package architecture and recommended usage.


h5features data format
======================

Basically the h5features data is composed of three componants:

* a set of **items** represented by their names (speech wav files for
  exemple),

* for each item, some attached **features** as numpy arrays (a set of
  Fourier vectors over a time window for exemple).

* some **times** information attached to features, as numpy arrays (the
  center of each Fourier time window for exemple).


h5features file structure
=========================

A h5features file is simply a `HDF file
<http://docs.h5py.org/en/latest/quick.html>`_ with a custom
structure. Given *h5features* the name of the h5features root group in
the file, the file is organized as follow:

- *file/h5features/*

  - *items*
  - *times*
  - *features*
  - *index*

Basic usage
===========

data generation
---------------



writing data
------------

In the following exemple we write the generated data to a h5features
file.

.. code-block:: python

   from h5features.write import Writer


reading data
------------

.. _h5py: http://docs.h5py.org
.. _HDF5: http://hdfgroup.org
.. _ABXpy: https://github.com/bootphon/ABXpy
