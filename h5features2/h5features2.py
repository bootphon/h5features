"""Provides functions to read/write in h5features files.

The h5features file format is briefly documented at
http://abxpy.readthedocs.org/en/latest/FilesFormat.html#features-file

"""

from h5features2.read import read
from h5features2.write import write
from h5features2.write import simple_write

# TODO test read() still compatible with legacy version (need
# transpose at some point ?)
# TODO implement sparse functionalities
# TODO introduce support for empty internal files ?
