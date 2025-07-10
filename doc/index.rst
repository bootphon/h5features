========================
h5features documentation
========================

* The ``h5features`` library provides easy to use and efficient storage of
  **large temporal data**

* It has been primarly designed to store **speech features** extracted from huge
  corpora.

* It uses the `HDF5 <https://support.hdfgroup.org/documentation>`_ binary
  file format, it is implemented in **C++** and exposes **Python bindings**
  with `nanobind <https://nanobind.readthedocs.io>`_.

* The source code is available at
  `<http://www.github.com/bootphon/h5features>`_.


**Table of contents**

.. toctree::
   :maxdepth: 2

   overview
   installation
   api_python
   api_cpp
   changelog


License
-------

.. figure:: static/inria.jpg
   :align: left
   :figwidth: 190px
   :alt: Inria
   :target: https://inria.fr/en

This work is founded by the grant *ADT-193* from `Inria <https://inria.fr/en>`_
and developed within the `Cognitive Machine Learning <https://cognitive-ml.fr>`_
research team.

-----------------------

h5features is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your
option) any later version.

h5features is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with h5features. If not, see http://www.gnu.org/licenses/.
