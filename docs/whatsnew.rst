.. highlight:: python
.. _whatsnew:

============
What's new ?
============

What's new in h5features 1.2
============================

* **Breaking change** Labels associated with features data must be
  sorted in increasing order. This is convenient to use with
  timestamps and improve reading huge datasets with long labels.

* **Breaking change** Appending new data to an exisiting item is no
  more allowed.

  Suppose a h5f file with 3 items ``['a', 'b', 'c']``, in 1.1 it was
  possible to append 3 items ``['c', 'd', 'e']``, giving a file with
  the 5 items ``['a', 'b', 'c', 'd', 'e']``, where the item ``'c'``
  being the concatenation of original and appended data. That facility
  was messy and is removed in 1.2.

* Bugfix when writing unidimensional features

* Bugfix when reading from time/to time in Reader

* Safely overwrite existing groups in h5features files with mode='w'

* Now more than 100 test cases


What's new in h5features 1.1
============================

The main goal of the 1.1 release is to provide a better, safer and
clearer code than previous release whithout changing the front-end
API.

* **Object oriented refactoring**

    An object oriented architecture have been coded. The main entry
    classes are Data, Reader and Writer.

* **Distinct overwrite/append mode**

    Appending to an existing file is now optional. This allow minor
    optimzations but that make sense when data is big.

* **Change in the HDF5 file structure**

    With *group* as the h5features root in a HDF5 file, the structure
    evolved from *group/[files, times, features, file_index]* to
    *group/[items, labels, features, index]*. These changes are done
    for clarity and consistency with code and usage.

* **Change in times/labels**

    You can now write 2D labels to h5features.

* **Test suite**

    The project is now endowed with a `pytest`_ suite of more than 50 unit
    tests.

* **Improved documentation**

    This is what you are reading now!


What's new in h5features 1.0
============================

Over the previous development release (0.1), the 1.0 release changes
the underlying HDF5 file structure, add a *version* attribute and
improve the index facilities.


**TODO** list
=============

.. include:: ../TODO.rst

.. _pytest: http://www.pytest.org
