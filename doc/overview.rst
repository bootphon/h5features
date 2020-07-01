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


File structure
--------------

The HDF5 file format is structured as a filesystem and is made of *groups*
(similar to folders), *datasets* (similar to files) and *attributes* (metadata
attached to groups and datasets).

Data stored in the ``h5features`` format is a *group* within a HDF5 file.

.. figure:: static/file_format.png
   :scale: 75%

   The h5features format internal organization.
