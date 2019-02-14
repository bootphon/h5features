For a future release
--------------------

* Converter: Possibility to specify other names than 'labels',
  'features' for the input files

* Test convertion from h5features old versions

* read/write bigger than RAM -> catch MemoryError when np.concatenate
  on writing.

* labels can be of arbitrary type (optionally sorted)

* Have a h5features.File class inspired by h5py.File

  * Make Data a dict with the following syntax::

      with h5f.Reader(file, group) as reader:
          reader['item'][from_time:to_time]
          reader['item'].features
          reader['item'].labels
          reader.keys()

  * Make an Item class wrapping Labels and Features

* Implement sparse functionalities
* Handle h5py MPI driver for concurent reading


For h5features-1.3
------------------

* Add an optional properties field in the dataset to store a
  dictionary of various entries (basically features parameters)
