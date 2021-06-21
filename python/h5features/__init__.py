"""h5features library"""

from h5features.item import Item
from h5features.reader import Reader
from h5features.writer import Writer


try:
    # a hack to read the library version from setup.py when h5features has been
    # installed
    import sys
    if sys.version_info >= (3, 8):
        from importlib import metadata
    else:
        import importlib_metadata as metadata

    __version__ = metadata.version('h5features')

except metadata.PackageNotFoundError:
    # h5features has not been installed, retrieve the version from the VERSION
    # file directly
    import pathlib
    version_file = pathlib.Path(__file__).parent.parent.parent / 'VERSION'
    try:
        __version__ = open(version_file).read().strip()
    except FileNotFoundError:
        import warnings
        warnings.warn('unable to retrieve h5features version')
        __version__ = 'VERSION_NOT_FOUND'


# exported when doing 'from h5features import *'
__all__ = [Item, Reader, Writer]
