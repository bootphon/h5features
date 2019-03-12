# Copyright 2014-2019 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
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
    """This class manages labels related operations for h5features files

    :param labels: Each element of the list contains the labels of
        an h5features item. Empty list are not accepted. For all t
        in labels, we must have t.ndim to be either 1 or 2.

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
    def __init__(self, labels, check=True):
        if check:
            self.check(labels)
        dim = self.parse_dim(labels)

        super(Labels, self).__init__('labels', labels, dim, np.float64, check)

    @staticmethod
    def check(labels):
        """Raise IOError if labels are not correct

        `labels` must be a list of sorted numpy arrays of equal
             dimensions (must be 1D or 2D). In the case of 2D labels,
             the second axis must have the same shape for all labels.

        """
        # type checking
        if not isinstance(labels, list):
            raise IOError('labels are not in a list')
        if not len(labels):
            raise IOError('the labels list is empty')
        if not all([isinstance(l, np.ndarray) for l in labels]):
            raise IOError('all labels must be numpy arrays')

        # dimension checking
        ndim = labels[0].ndim
        if ndim not in [1, 2]:
            raise IOError('labels dimension must be 1 or 2')
        if not all([l.ndim == ndim for l in labels]):
            raise IOError('all labels dimensions must be equal')
        if ndim == 2:
            shape1 = labels[0].shape[1]
            if not all([l.shape[1] == shape1 for l in labels]):
                raise IOError('all labels must have same shape on 2nd dim')

        # sort checking
        for label in labels:
            index = (np.argsort(label) if label.ndim == 1
                     else np.lexsort(label.T))
            # print label, index
            # print len(index), label.shape[0]
            assert len(index) == label.shape[0]
            if not all(n == index[n] for n in range(label.shape[0]-1)):
                raise IOError('labels are not sorted in increasing order')

    @staticmethod
    def parse_dim(labels):
        """Return the labels vectors dimension"""
        return 1 if labels[0].ndim == 1 else labels[0].shape[1]

    def __eq__(self, other):
        if self is other:
            return True
        try:
            # check little attributes
            if not (self.name == other.name and
                    self.dim == other.dim and
                    self.dtype == other.dtype and
                    len(self.data) == len(other.data)):
                return False
            # check big data
            for i in range(len(self.data)):
                if not np.array_equal(self.data[i], other.data[i]):
                    return False
            return True
        except AttributeError:
            return False

    def is_appendable_to(self, group):
        shape = group[self.name].shape
        res = self.dim == 1 if len(shape) == 1 else self.data[0].ndim == 2
        return res

    def _dim_tuple(self, value):
        return (value,) if self.dim == 1 else (value, self.dim)

    def create_dataset(
            self, group, per_chunk, compression=None, compression_opts=None):
        shape = self._dim_tuple(0)
        maxshape = self._dim_tuple(None)
        if per_chunk == 'auto':
            chunks = True
        else:
            chunks = self._dim_tuple(per_chunk)

        group.create_dataset(
            self.name, shape, dtype=self.dtype,
            chunks=chunks, maxshape=maxshape,
            compression=compression, compression_opts=compression_opts)

    def write_to(self, group):
        nb_data = sum([d.shape[0] for d in self.data])
        nb_group = group[self.name].shape[0]
        new_size = nb_group + nb_data

        if self.dim == 1:
            group[self.name].resize((new_size,))
            if len(self.data) == 1:
                group[self.name][nb_group:] = self.data[0].T
            else:
                group[self.name][nb_group:] = np.concatenate(self.data)
        else:
            group[self.name].resize((new_size, self.dim))
            group[self.name][nb_group:] = np.concatenate(self.data, axis=0)
