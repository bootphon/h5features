"""Provides the Times class to the h5features module.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import numpy as np

from h5features.dataset.dataset import Dataset

def parse_times(times):
    """Return the times vectors dimension from raw times arrays.

    Parameters
    ----------

    times : a list of numpy arrays

        Each element of the list contains the timestamps of an
        h5features item. For all t in times, we must have t.ndim to be
        either 1 or 2.

        - 1D arrays contain the center timestamps of each frame of
          the related item.

        - 2D arrays contain the begin and end timestamps of each
          items's frame, thus having t.ndim == 2 and t.shape[1] == 2

    Raise
    -----

    IOError if the time format is not 1 or 2, or if times arrays have
    different dimensions.

    Return
    ------

    dim : int

        The parsed times dimension is either 1 or 2 for 1D or 2D times
        arrays respectively.

    """

    if not times:
        raise IOError('empty times data!')

    # TODO check that the times are increasing for each item
    dim = times[0].ndim

    if dim > 2:
        raise IOError('times must be a list of 1D or 2D numpy arrays.')

    if not all([t.ndim == dim for t in times]):
        raise IOError('all times arrays must have the same dimension.')

    if dim == 2 and not all(t.shape[1] == 2 for t in times):
        raise IOError('2D times arrays must have 2 elements on 2nd dimension')

    return dim


class Times(Dataset):
    """This class manages times related operations for h5features files."""

    def __init__(self, data, name='times'):
        dim = parse_times(data)
        super(Times, self).__init__(data, name, dim, np.float64)

    def is_appendable_to(self, group):
        """Return True if times data can be appended to the given group."""
        return group[self.name][...].ndim == self.dim

    def create_dataset(self, group, per_chunk):
        """Creates an empty times dataset in the given group."""
        shape = (0,) if self.dim == 1 else (0, self.dim)
        maxshape = (None,) if self.dim == 1 else (None, self.dim)
        chunks = (per_chunk,) if self.dim == 1 else (per_chunk, self.dim)

        group.create_dataset(self.name, shape, dtype=self.dtype,
                             chunks=chunks, maxshape=maxshape)

    def write(self, group):
        """Write times data to the group."""
        nb_data = sum([d.shape[0] for d in self.data])
        nb_group = group[self.name].shape[0]
        new_size = nb_group + nb_data

        if self.dim == 1:
            group[self.name].resize((new_size,))
            group[self.name][nb_group:] = np.concatenate(self.data)
        else: # self.dim == 2
            group[self.name].resize((new_size, 2))
            group[self.name][nb_group:] = np.concatenate(self.data, axis=0)
