# Copyright 2014-2015 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
#
# This file is part of h5features.
#
# h5features is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# h5features is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with h5features.  If not, see <http://www.gnu.org/licenses/>.
"""Provides the Times class to the h5features module."""

import numpy as np
from .dataentry import DataEntry

def parse_times(times, check):
    """Return the times vectors dimension from raw times arrays.

    :param times: Each element of the list contains the timestamps of
        an h5features item. For all t in times, we must have t.ndim to
        be either 1 or 2.

        * 1D arrays contain the center timestamps of each frame of the
          related item.

        * 2D arrays contain the begin and end timestamps of each
          items's frame, thus having t.ndim == 2 and t.shape[1] == 2.

    :type times: list of numpy arrays

    :param bool check: If True, raise on errors

    :raise IOError: if the time format is not 1 or 2, or if times
        arrays have different dimensions.

    :return: The parsed times dimension is either 1 or 2 for 1D or 2D
        times arrays respectively.

    """
    dim = times[0].ndim

    if check:
        if dim > 2:
            raise IOError('times must be a list of 1D or 2D numpy arrays.')

        if not all([t.ndim == dim for t in times]):
            raise IOError('all times arrays must have the same dimension.')

        if dim == 2 and not all(t.shape[1] == 2 for t in times):
            raise IOError('2D times arrays must have 2 elements on 2nd dimension')
    return dim


class Times(DataEntry):
    """This class manages times related operations for h5features files."""

    def __init__(self, data, check=True):
        dim = parse_times(data, check)
        super(Times, self).__init__(data, dim, np.float64, check)

    def __eq__(self, other):
        if self is other:
            return True
        try:
            # check the little attributes
            if not (self.dim == other.dim and
                    self.dtype == other.dtype and
                    len(self.data) == len(other.data)):
                return False
            # check big data
            for i in range(len(self.data)):
                if not (self.data[i] == other.data[i]).all():
                    return False
            return True
        except AttributeError:
            return False

    def is_appendable_to(self, group):
        return group['times'][...].ndim == self.dim

    def create_dataset(self, group, per_chunk):
        shape = (0,) if self.dim == 1 else (0, self.dim)
        maxshape = (None,) if self.dim == 1 else (None, self.dim)
        chunks = (per_chunk,) if self.dim == 1 else (per_chunk, self.dim)

        group.create_dataset('times', shape, dtype=self.dtype,
                             chunks=chunks, maxshape=maxshape)

    def write(self, group):
        name = 'items'
        nb_data = sum([d.shape[0] for d in self.data])
        nb_group = group[name].shape[0]
        new_size = nb_group + nb_data

        if self.dim == 1:
            group[name].resize((new_size,))
            group[name][nb_group:] = np.concatenate(self.data)
        else: # self.dim == 2
            group[name].resize((new_size, 2))
            group[name][nb_group:] = np.concatenate(self.data, axis=0)
