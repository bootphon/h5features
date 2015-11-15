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

"""Provides the Labels class to the h5features module."""

import numpy as np
from .entry import Entry


class Labels(Entry):
    """This class manages labels related operations for h5features files."""

    def __init__(self, data, check=True):
        dim = self.parse_labels(data, check)
        super(Labels, self).__init__('labels', data, dim, np.float64, check)

    @staticmethod
    def parse_labels(labels, check=True):
        """Return the labels vectors dimension.

        :param labels: Each element of the list contains the labels of
            an h5features item. For all t in labels, we must have
            t.ndim to be either 1 or 2.

            * 1D arrays contain the center labelstamps of each frame of the
              related item.

            * 2D arrays contain the begin and end labelstamps of each
              items's frame, thus having t.ndim == 2 and t.shape[1] == 2.

        :type labels: list of numpy arrays

        :param bool check: If True, raise on errors

        :raise IOError: if the time format is not 1 or 2, or if labels
            arrays have different dimensions.

        :return: The parsed labels dimension is either 1 or 2 for 1D
            or 2D labels arrays respectively.

        """
        # TODO change that method to parse arbitrary type of labels
        try:
            dim = labels[0].ndim
        except:
            dim = 1

        if check:
            if dim > 2:
                raise IOError('labels must be a list of 1D or 2D numpy arrays.')
            if not all([t.ndim == dim for t in labels]):
                raise IOError('all labels arrays must have the same dimension.')
        return dim

    def __eq__(self, other):
        if self is other:
            return True
        try:
            # check the little attributes
            if not (self.name == other.name and
                    self.dim == other.dim and
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
        return group[self.name][...].ndim == self.dim

    def create_dataset(self, group, per_chunk):
        shape = (0,) if self.dim == 1 else (0, self.dim)
        maxshape = (None,) if self.dim == 1 else (None, self.dim)
        chunks = (per_chunk,) if self.dim == 1 else (per_chunk, self.dim)

        group.create_dataset(self.name, shape, dtype=self.dtype,
                             chunks=chunks, maxshape=maxshape)

    def write_to(self, group):
        nb_data = sum([d.shape[0] for d in self.data])
        nb_group = group[self.name].shape[0]
        new_size = nb_group + nb_data

        if self.dim == 1:
            group[self.name].resize((new_size,))
            group[self.name][nb_group:] = np.concatenate(self.data)
        else:
            group[self.name].resize((new_size, self.dim))
            group[self.name][nb_group:] = np.concatenate(self.data, axis=0)
