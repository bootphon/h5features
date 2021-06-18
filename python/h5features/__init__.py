"""h5features library"""

from h5features.item import Item
from h5features.reader import Reader
from h5features.writer import Writer


# a hack to read the library version from setup.py
import sys
if sys.version_info >= (3, 8):
    from importlib import metadata
else:
    import importlib_metadata as metadata

__version__ = metadata.version('h5features')


# exported when doing 'from h5features import *'
__all__ = [Item, Reader, Writer]
