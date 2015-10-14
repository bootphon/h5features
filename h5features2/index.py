"""Provides the Index class to the h5features module.

TODO

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import numpy as np
from h5features2.chunk import nb_lines

class Index(object):
    """TODO"""
    def __init__(self, name='file_index'):
        self.name = name

    def create(self, group, chunk_size):
        """Create an empty index dataset in the given group."""
        nb_lines_by_chunk = max(10, nb_lines(
            np.dtype(np.int64).itemsize, 1, chunk_size * 1000))

        group.create_dataset(self.name, (0,), dtype=np.int64,
                             chunks=(nb_lines_by_chunk,), maxshape=(None,))

    def write(self, group, items, features):
        """Write the index to the given HDF5 group."""
        nitm = group[items.name].shape[0]
        last_index = group[self.name][-1] if nitm > 0 else -1
        self.index = last_index + np.cumsum([x.shape[0] for x in features.data])

        nidx = group[self.name].shape[0]
        # in case we append to the end of an existing item
        if items.continue_last_item(group):
            nidx -= 1

        group[self.name].resize((nidx + self.index.shape[0],))
        group[self.name][nidx:] = self.index
