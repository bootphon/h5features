These document the scheduled and/or requested changes to the h5features package.

For 1.1.0 release
-----------------

* test versions and converter
* optimize writer and reader -> stress test on big data
* docs

  * usage.rst
  * fix sphinx.interdocs for h5py
  * fix building on readthedocs
  * Examples on how to extend h5features to custom datasets
    (i.e. Dataset inheritance).



For a future release
--------------------

* Have a h5features.File class inspired by h5py.File
* Implement sparse functionalities
* Handle h5py MPI driver for concurent reading
* Name attribute in datasets is no longuer needed, remove it
