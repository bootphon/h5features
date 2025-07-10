Overview
========


Motivations
-----------

The ``h5features`` library provides efficient and flexible I/O on a (potentially
large) collection of (potentially small) 2D datasets with one fixed dimension
(the *features* dimension, identical for all datasets) and one variable
dimension (the *times* dimension, possibly different for each dataset). For
example, the collection of datasets can correspond to speech features (e.g. MFC
coefficients) extracted from a collection of speech recordings with variable
durations. In this case, the *times* dimension corresponds to timestamps of each
frame and the *features* dimension store a features vector for each frame, its
meaning depends on the type of speech features used.

The ``h5features`` library can handle small or large collections of small or
large datasets, but the case that motivated its design is that of large
collections of small datasets. This is a common case in speech signal
processing, for example, where features are often extracted separately for each
sentence in multi-hours recordings of speech signal. If the features are stored
in individual files, the number of files becomes problematic. If the features
are stored in a single big file which does not support partial I/O, the size of
the file becomes problematic. To solve this problem, ``h5features`` is built on
top of the HDF5 library, which supports partial I/O.

All the items of a dataset are stored in a single file. This allows for
efficient I/O on a single item. ``h5features`` also indexes the *times*
dimension of each item and allow partial I/O along it. To continue our speech
features example, this means that it is possible to load just the features for a
specific time-interval in a specific utterance (corresponding to a word or phone
of interest for instance). The labels indexing the *times* dimension typically
correspond to a pair ``(tstart, tstop)`` associated to each feature vector in a
dataset.

Along with times and features, an item can also have attached *properties*
defined by the user. This can be used for instance to store metadata on the
stored features (author, parameters, origin of the data, preprocessing, etc).


The *h5features* file format
----------------------------

This section explains the structure of a h5features file as written by the
library, and the difference between the implemented versions.

.. note::

   This is usual to use ``.h5f`` as extension for *h5features* files, but this
   is not required by the library.


.. warning::

   Do not be confused between **library version** and **file format version**.
   The details of library changes and versions are available in the *Changelog*
   section.


The ``h5features`` library is built on the `HDF5 library and file format
<https://www.hdfgroup.org/solutions/hdf5>`_. In few words, the HDF5 format is
structured as a filesystem and is made of *groups* (similar to folders),
*datasets* (similar to files) and *attributes* (metadata attached to groups and
datasets). It allows efficient input/output operations on large datasets. In top
of HDF5, we use the `HighFive C++ library
<https://github.com/BlueBrain/HighFive>`_ which provides a high level and friendly
interface to HDF5.

Several versions of the *h5features* file format have been implemented:

* **file format 0.1**

  Composed of the following datasets: ``features``, ``times``, ``files``,
  ``file_index``. All features from differents items are stacked in the same
  dataset and indexed. There is no ``version`` attribute nor properties support.
  Timestamps must be 1D.

* **file format 1.0**

  Same as 0.1 with a ``version`` attribute added.

* **file format 1.1**

  The structure evolved from *group/[files, times, features, file_index]* to
  *group/[items, labels, features, index]*. Support for 2d timestamps. Support
  for ``properties``, stored as a string attribute (implemented with Python
  pickle module).

* **file format 1.2**

  Same as 1.1 with a new and incompatible implementation of properties, stored
  as a group.

* **file format 2.0**

  Complete rewrite of the file structure. Each item is stored in his own group
  and includes the following datasets and attributes: ``features``, ``times``,
  ``name`` and ``properties``. This implementation is a little bit slower than
  the 1.x version (especially for uncompressed data) but the structure is by far
  more explicit (no more stacked data nor index).

* The compatibility grid below details for each *library* version which *file*
  version is supported for read and write operations:

  ==================== =================== ====================
  *h5features* version file version (read) file version (write)
  ==================== =================== ====================
  0.1                  0.1                 0.1
  1.0                  0.1, 1.0            0.1, 1.0
  1.1                  0.1, 1.0            1.0
  1.2.x                0.1, 1.0            1.0
  1.3.x                0.1, 1.0, 1.1       1.0, 1.1
  2.0.x                1.0, 1.1*, 1.2, 2.0 1.1*, 1.2, 2.0
  ==================== =================== ====================

Basic usage
-----------

The following example show the main usage of h5features:

.. include:: example.py
   :code: python