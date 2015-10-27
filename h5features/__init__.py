"""This package defines a standard to read/write features from/to HDF5 files.

The h5features file format is briefly documented at
http://abxpy.readthedocs.org/en/latest/FilesFormat.html#features-file

TODO Document more and more this package. Give proper definition of
the format, give examples.

# TODO test read() still compatible with legacy version (need
# transpose at some point ?)
# TODO implement sparse functionalities
# TODO introduce support for empty internal files ?

"""

from .h5features import read
from .h5features import write
from .h5features import simple_write
