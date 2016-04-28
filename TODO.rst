These document the scheduled and/or requested changes to the h5features package.

For 1.1 release
---------------

* Test convertion from h5features old versions
* read/write bigger than RAM -> catch MemoryError when np.concatenate
  on writing.
* Data.__repr__

For a future release
--------------------

* labels can be of arbitrary type
* Have a h5features.File class inspired by h5py.File

  * Make Data a dict with the following syntax::

      reader = h5f.Reader(file, group)
      reader['item'][from_time:to_time]
      reader['item'].features
      reader['item'].labels
      reader.keys()

  * Make an Item class wrapping Labels and Features

* Implement sparse functionalities
* Handle h5py MPI driver for concurent reading
* Enable autochunking from h5py (with chunk=None)
