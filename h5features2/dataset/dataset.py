"""Provides the Dataset interface implemented by Features, Times and Items.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import numpy as np

class Dataset(object):
    """The Dataset class is an **abstract base class** of h5features data.

    It provides a shared interface to the classes `Items`, `Times` and
    'Features' which all together constitutes an h5features file.

    """
    def __init__(self, data, name):
        self.name = name
        self.data = data

    def __eq__(self, other):
        return self.name == other.name and self.data == other.data

    # def is_appendable_to(self, group):
    #     return

    # def write(self, group):
    #     return

    # def read(self, group):
    #     return

    def create_dataset(self, group, dtype, dim, chunk_size):
        shape = (0,) if dim == 1 else (0, dim)
        maxshape = (None,) if dim == 1 else (None, dim)

        if dtype == np.dtype('O'):
            # if dtype is a variable str, guess representative size is 20 Bytes
            per_chunk = _nb_per_chunk(20, dim, chunk_size)
        else:
            per_chunk = _nb_per_chunk(np.dtype(dtype).itemsize, dim, chunk_size)

        chunks = (per_chunk,) if dim == 1 else (per_chunk, dim)

        # raise if per_chunk >= 4 Gb, this is requested by h5py
        group.create_dataset(self.name, shape, dtype=dtype,
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
    print('ratio: {}'.format(ratio))
    return max(10, ratio)
