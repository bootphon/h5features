These document the scheduled and/or requested changes to the h5features package.

For 1.1 release
---------------

* docs/usage.rst
* write the h5f.Data class as front end for sending/receiving data
  to/from the package.
* improve the reader interface (do not check on reading)
* implement read(index)

For a future release
--------------------

* Have a h5features.File class inspired by h5py.File
* Implement sparse functionalities
* Handle h5py MPI driver for concurent reading
* Enable autochunking from h5py (with chunk=None)
