"""Provides the Times class to the h5features module.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import numpy as np

def parse_times(times):
    """Retrieve time format, raise on errors.

    Raise IOError if the time format is not 1 or 2, or if times arrays
    have different dimensions.

    """
    # TODO check that the times are increasing for each file
    tformat = times[0].ndim

    if tformat > 2:
        raise IOError('times must be a list of 1D or 2D numpy arrays.')

    if not all([t.ndim == tformat for t in times]):
        raise IOError('all times arrays must have the same dimension.')

    return tformat


class Times(object):
    """This class manages times related operations for h5features files."""
    def __init__(self, times):
        self.tformat = parse_times(times)
        self.times = times

    def is_compatible(self, group):
        """Return True if times data can be appended to the given group."""
        return group['times'][...].ndim == self.tformat

    def create(self, group, nb_in_chunks):
        """Initilizes the times subgroup."""
        # TODO smarter
        if self.tformat == 1:
            group.create_dataset('times', (0,), dtype=np.float64,
                                 chunks=(nb_in_chunks,), maxshape=(None,))
        else:  # times_format == 2
            group.create_dataset('times', (0,2), dtype=np.float64,
                                 chunks=(nb_in_chunks,2), maxshape=(None,2))

    def write(self, group):
        """Write times data to the group"""
        if self.tformat == 1:
            self.times = np.concatenate(self.times)
            nb, = group['times'].shape
            group['times'].resize((nb + self.times.shape[0],))
            group['times'][nb:] = self.times
        else:
            assert tformat == 2
            nb, _ = group['times'].shape
            group['times'].resize((nb + self.times.shape[0],2))
            group['times'][nb:] = self.times
