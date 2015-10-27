"""This package defines a standard to read/write features from/to HDF5 files.

The h5features file format is briefly documented at
http://abxpy.readthedocs.org/en/latest/FilesFormat.html#features-file

"""

from .h5features import read
from .h5features import write
from .h5features import simple_write
