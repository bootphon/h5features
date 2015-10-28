These document the planned and future changes to the h5features package.

For 1.1.0 release
-----------------

  - Refactor the Reader _get_items, _get_times methods. This is not
    clear at all what the point is.
  - test versions and converter
  - finish documenting, write examples as doctest
  - profile and compare with 1.0, stress test on big data

For a future release
--------------------

  - Have a h5features.File class inspired by h5py.File

General TODOs
-------------

  - Examples on how to extend h5features to custom datasets
    (i.e. Dataset inheritance).
  - Examples of equivalence between legacy and new APIs.
