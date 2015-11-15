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
* Implement sparse functionalities
* Handle h5py MPI driver for concurent reading
* Enable autochunking from h5py (with chunk=None)
