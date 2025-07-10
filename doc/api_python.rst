Python API
==========

.. note::

   The whole library is accessible by importing the ``h5features`` module.

   .. code-block:: python

      import h5features

Item
----

.. autoclass:: h5features.Item

   .. automethod:: features
   .. automethod:: times
   .. autoproperty:: name() -> str
   .. autoproperty:: dim() -> int
   .. autoproperty:: size() -> int
   .. autoproperty:: properties() -> dict


Writer
------

.. autoclass:: h5features.Writer

   .. automethod:: write
   .. autoproperty:: filename() -> str
   .. autoproperty:: groupname() -> str
   .. autoproperty:: version() -> h5features.Version


Reader
------

.. autoclass:: h5features.Reader

   .. automethod:: read
   .. automethod:: read_all
   .. automethod:: read_partial
   .. automethod:: items
   .. automethod:: list_groups
   .. autoproperty:: filename() -> str
   .. autoproperty:: groupname() -> str
   .. autoproperty:: version() -> h5features.Version


Version
-------

.. autoenum:: h5features.Version
