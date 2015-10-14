"""Provides the Index class to the h5features module.

TODO

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

from h5features2.chunk import nb_lines

class Index(object):
    """TODO"""
    def __init__(self, chunk_size):
        self.chunk_size = chunk_size

    def create(self, group):
        """Initializes the file index subgroup."""
        nb_lines_by_chunk = max(10, nb_lines(
            np.dtype(np.int64).itemsize, 1, self.chunk_size * 1000))

        group.create_dataset('file_index', (0,), dtype=np.int64,
                             chunks=(nb_lines_by_chunk,), maxshape=(None,))


    def write(self, group, continue_last_file):
        """Write the files index to the group"""
        nitems, = group['file_index'].shape
        if continue_last_file:
            nitems -= 1
        group['file_index'].resize((nitems + self.index.shape[0],))
        group['file_index'][nitems:] = self.index
