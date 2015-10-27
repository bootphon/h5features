"""Provides the Dataset interface implemented by Features, Times and Items.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import numpy as np

class Dataset(object):
    """The Dataset class is an **abstract base class** of h5features data.

    It provides a shared interface to the classes `Items`, `Times` and
    'Features' which all together constitutes an h5features file.

    """
    def __init__(self, data, name, dim, dtype):
        self.name = name
        self.dim = dim
        self.dtype = dtype
        self.data = data

    def __eq__(self, other):
        try:
            return (self.name == other.name and
                    self.dim == other.dim and
                    self.dtype == other.dtype and
                    self.data == other.data)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def create_dataset(self, group, chunk_size):
        """Create an empty dataset in an HDF5 *group*.

        TODO comment that method"""
        shape = (0,) if self.dim == 1 else (0, self.dim)
        maxshape = (None,) if self.dim == 1 else (None, self.dim)

        if self.dtype == np.dtype('O'):
            # if dtype is a variable str, guess representative size is 20 bytes
            per_chunk = _nb_per_chunk(20, self.dim, chunk_size)
        else:
            per_chunk = _nb_per_chunk(np.dtype(self.dtype).itemsize,
                                      self.dim, chunk_size)

        chunks = (per_chunk,) if self.dim == 1 else (per_chunk, self.dim)

        # raise if per_chunk >= 4 Gb, this is requested by h5py
        group.create_dataset(self.name, shape, dtype=self.dtype,
                             chunks=chunks, maxshape=maxshape)


def _nb_per_chunk(item_size, item_dim, chunk_size):
    """Return the number of items that can be stored in one chunk.

    This function is used internally by the *Dataset.create_dataset*
    method. The result is returned in bytes

    Parameters

    - *item_size* : int --- Size of an item's scalar componant in
       Bytes (e.g. for np.float64 this is 8)

    - *item_dim* : int --- Items dimension (length of the second axis)

    - *chunk_size* : float --- The size of a chunk given in MBytes.

    """
    # from Mbytes to bytes
    size = chunk_size * 10.**6
    ratio = int(round(size / (item_size*item_dim)))
    return max(10, ratio)
