.. _whatsnew:

============
What's new ?
============

These document the changes between versions of h5features. A **TODO**
list for future releases is also provided.


What's new in h5features 1.1
============================

The main goal of the 1.1 release is to provide a better, safer and
clearer code than previous release whithout changing the front-end
API.

* **Object oriented refactoring**

    An object oriented architecture have been coded. The main entry
    classes are the Reader and the Writer, which behind the scene
    relies on instances of the Dataset and Index classes.

* **Change in the HDF5 file structure**

    With *group* as the h5features root in a HDF5 file, the structure
    evolved from *group/[files, times, features, file_index]* to
    *group/[items, times, features, index]*. These changes are done
    for clarity and consistency with the code.

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

.. include:: ../../TODO.rst

.. _pytest: http://www.pytest.org
