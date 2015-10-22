"""Provides the Times class to the h5features module.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import numpy as np

from h5features2.dataset.dataset import Dataset

def parse_times(times):
    """Return the time format from raw times arrays, raise on errors.

    Parameters
    ----------

    times : a list of numpy arrays

        Each element of the list contains the timestamps of an
        h5features item. For all t in times, we must have f.ndim to be
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

    tformat : int

        The parsed time format is either 1 or 2 for 1D or 2D times
        arrays respectively.

    """
    # TODO check that the times are increasing for each item
    tformat = times[0].ndim

    if tformat > 2:
        raise IOError('times must be a list of 1D or 2D numpy arrays.')

    if not all([t.ndim == tformat for t in times]):
        raise IOError('all times arrays must have the same dimension.')

    if tformat == 2 and not all(t.shape[1] == 2 for t in times):
        raise IOError('2D times arrays must have 2 elements on 2nd dimension')

    return tformat


class Times(Dataset):
    """This class manages times related operations for h5features files."""

    def __init__(self, data, name='times'):
        super().__init__(data, name)
        self.tformat = 1

    def __eq__(self, other):
        try:
            return super().__eq__(other) and self.tformat == other.tformat
        except AttributeError:
            return False

    def is_appendable_to(self, group):
        """Return True if times data can be appended to the given group."""
        return group[self.name][...].ndim == self.tformat

    def create_dataset(self, group, per_chunk):
        """Creates an empty times dataset in the given group."""
        dim = self.tformat
        shape = (0,) if dim == 1 else (0, dim)
        maxshape = (None,) if dim == 1 else (None, dim)
        dtype = np.float64
        chunks = (per_chunk,) if dim == 1 else (per_chunk, dim)
        group.create_dataset(self.name, shape, dtype=dtype,
                             chunks=chunks, maxshape=maxshape)

    def write(self, group):
        """Write times data to the group."""
        nb_data = sum([d.shape[0] for d in self.data])
        nb_group = group[self.name].shape[0]
        new_size = nb_group + nb_data

        group[self.name].resize((new_size,))
        group[self.name][nb_group:] = np.concatenate(self.data)

# TODO No need to specialize, make Times more generic
class Times2D(Times):
    """Specialized class for 2D times arrays."""

    def __init__(self, data, name='times'):
        if not all([d.ndim == 2 for d in data]):
            raise IOError('data must be 2D.')

        super().__init__(data, name)
        # must be after super() because overloaded from Times
        self.tformat = 2

    def write(self, group):
        """Write times data to the group"""
        nb_data = sum([d.shape[0] for d in self.data])
        nb_group = group[self.name].shape[0]
        new_size = nb_group + nb_data

        group[self.name].resize((new_size, 2))
        group[self.name][nb_group:] = np.concatenate(self.data, axis=0)
