================
Package overview
================

.. highlight:: python
.. note::

   In the following code samples, the h5features package is imported as::

     import h5features as h5f

Brief
=====

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


Description
===========

The h5features package provides efficient and flexible I/O on a
(potentially large) collection of (potentially small) 2D datasets with
one fixed dimension (the ‘feature’ dimension, identical for all
datasets) and one variable dimension (the ’label’ dimension, possibly
different for each dataset). For example, the collection of datasets
can correspond to speech features (e.g. MFC coefficients) extracted
from a collection of speech recordings with variable durations. In
this case, the ‘label’ dimension corresponds to time and the meaning
of the 'feature' dimension depends on the type of speech features
used.

The h5features package can handle small or large collections of small
or large datasets, but the case that motivated its design is that of
large collections of small datasets. This is a common case in speech
signal processing, for example, where features are often extracted
separately for each sentence in multi-hours recordings of speech
signal. If the features are stored in individual files, the number of
files becomes problematic. If the features are stored in a single big
file which does not support partial I/O, the size of the file becomes
problematic. To solve this problem, h5features is built on top of
h5py, a python binding of the HDF5 library, which supports partial
I/O. All the items in the collection of datasets are stored in a
single file and an indexing structure allows for efficient I/O on
single items or on contiguous groups of items. h5features also indexes
the ‘label’ dimension of each individual dataset and allow partial I/O
along it. To continue our speech features example, this means that it
is possible to load just the features for a specific time-interval in
a specific utterance (corresponding to a word or phone of interest for
instance). The labels indexing the ‘label’ dimension typically
correspond to center-times or time-intervals associated to each
feature vector in a dataset.


Command line converter
======================

The scipt ``convert2h5features`` allows you to simply convert a set of
files to a single h5features file. Supported files format are numpy
NPZ and Octave/Matlab mat files.

.. highlight:: bash

For more info on that script, have a::

  $ convert2h5features --help

Basic usage
===========

.. include:: exemple.py
   :code: python

.. _h5py: http://docs.h5py.org
.. _HDF5: http://www.hdfgroup.org/HDF5/
.. _ABXpy: https://github.com/bootphon/ABXpy
