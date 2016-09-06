# Copyright 2014-2016 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
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

"""Provides the Items class to the h5features package."""

import numpy as np

from h5py import special_dtype
from .entry import Entry, nb_per_chunk


def read_items(group, version='1.1', check=False):
    """Return an Items instance initialized from a h5features group."""
    if version == '0.1':
        # parse unicode to strings
        return ''.join(
            [unichr(int(c)) for c in group['files'][...]]
        ).replace('/-', '/').split('/\\')
    elif version == '1.0':
        return Items(list(group['files'][...]), check)
    else:
        return Items(list(group['items'][...]), check)


class Items(Entry):
    """This class manages items in h5features files.

    :param data: A list of item names (e.g. files from which the
        features where extracted). Each name of the list must be
        unique.
    :type data: list of str

    :raise IOError: if data is empty or if one or more names are not
        unique in the list.

    """
    def __init__(self, data, check=True):
        if check:
            if not data:
                raise IOError('data is empty')
            if not len(set(data)) == len(data):
                raise IOError('all items must have different names.')

        super(Items, self).__init__(
            'items', data, 1, special_dtype(vlen=str), check)

    def create_dataset(self, group, chunk_size):
        self._create_dataset(group, chunk_size)

    def is_appendable_to(self, group):
        return not set(group[self.name][...]).intersection(self.data)

    def write_to(self, group):
        """Write stored items to the given HDF5 group.

        We assume that self.create() has been called.

        """
        # The HDF5 group where to write data
        items_group = group[self.name]

        nitems = items_group.shape[0]
        items_group.resize((nitems + len(self.data),))
        items_group[nitems:] = self.data

    def is_valid_interval(self, lower, upper):
        """Return False if [lower:upper] is not a valid subitems interval. If
        it is, then returns a tuple of (lower index, upper index)"""
        try:
            lower_idx = self.data.index(lower)
            upper_idx = self.data.index(upper)
            return (lower_idx, upper_idx) if lower_idx <= upper_idx else False
        except ValueError:
            return False

    def _create_dataset(self, group, chunk_size):
        """Create an empty dataset in a group."""
        # if dtype is a variable str, guess representative size is 20 bytes
        per_chunk = (
            nb_per_chunk(20, 1, chunk_size) if self.dtype == np.dtype('O')
            else nb_per_chunk(np.dtype(self.dtype).itemsize, 1, chunk_size))

        shape = (0,)
        maxshape = (None,)
        chunks = (per_chunk,)

        # raise if per_chunk >= 4 Gb, this is requested by h5py
        group.create_dataset(
            self.name, shape, dtype=self.dtype,
            chunks=chunks, maxshape=maxshape)
