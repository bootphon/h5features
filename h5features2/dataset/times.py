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
        self.tformat = 1
        self.name = name
        self.data = data

    def is_compatible(self, group):
        """Return True if times data can be appended to the given group."""
        return group[self.name][...].ndim == self.tformat

    def create(self, group, nb_in_chunks):
        """Creates an empty times dataset in the given group."""
        group.create_dataset(self.name, (0,), dtype=np.float64,
                             chunks=(nb_in_chunks,), maxshape=(None,))

    def write(self, group):
        """Write times data to the group."""
        self.data = np.concatenate(self.data)
        nb = group[self.name].shape[0]

        group[self.name].resize((nb + self.data.shape[0],))
        group[self.name][nb:] = self.data


class Times2D(Times):
    """Specialized class for 2D times arrays."""
    def __init__(self, data, name='times'):
        Times.__init__(self, data, name)
        self.tformat = 2

    def create(self, group, nb_in_chunks):
        """Creates an empty times dataset in the given group."""
        group.create_dataset(self.name, (0,2), dtype=np.float64,
                             chunks=(nb_in_chunks,2), maxshape=(None,2))

    def write(self, group):
        """Write times data to the group"""
        self.data = np.concatenate(self.data, axis=1)
        nb = group[self.name].shape[0]

        group[self.name].resize((nb + self.data.shape[0], 2))
        group[self.name][nb:] = self.data
