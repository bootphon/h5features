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
"""Provides the Entry class to the h5features package."""

import numpy as np


def nb_per_chunk(item_size, item_dim, chunk_size):
    """Return the number of items that can be stored in one chunk.

    :param int item_size: Size of an item's scalar componant in
        Bytes (e.g. for np.float64 this is 8)

    :param int item_dim: Items dimension (length of the second axis)

    :param float chunk_size: The size of a chunk given in MBytes.

    """
    # from Mbytes to bytes
    size = chunk_size * 10.**6
    ratio = int(round(size / (item_size*item_dim)))
    return max(10, ratio)


class Entry(object):
    """The Entry class is the base class of h5features.Data entries.

    It provides a shared interface to the classes ``Items``,
    ``Times`` and ``Features`` which all together compose a ``Data``.

    """
    def __init__(self, name, data, dim, dtype, check=True):
        if check:
            if not isinstance(data, list):
                raise ValueError('data must be a list')
            if dim < 1:
                raise ValueError('dimension must be strictly positive')

        self.name = name
        self.data = data
        self.dim = dim
        self.dtype = dtype

    def __eq__(self, other):
        if self is other:
            return True
        try:
            return (self.is_appendable(other) and
                    self.data == other.data)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def clear(self):
        """Erase stored data"""
        self.data = []

    def is_appendable(self, entry):
        """Return True if entry can be appended to self"""
        try:
            if (
                    self.name == entry.name and
                    self.dtype == entry.dtype and
                    self.dim == entry.dim
            ):
                return True
        except AttributeError:
            return False
        return False

    def append(self, entry):
        """Append an entry to self"""
        if not self.is_appendable(entry):
            raise ValueError('entry not appendable')
        self.data += entry.data

    def _create_dataset(
            self, group, chunk_size, compression, compression_opts):
        """Create an empty dataset in a group."""
        if chunk_size == 'auto':
            chunks = True
        else:
            # if dtype is a variable str, guess representative size is 20 bytes
            per_chunk = (
                nb_per_chunk(20, self.dim, chunk_size)
                if self.dtype == np.dtype('O') else
                nb_per_chunk(np.dtype(self.dtype).itemsize,
                             self.dim, chunk_size))
            chunks = (per_chunk, self.dim)

        shape = (0, self.dim)
        maxshape = (None, self.dim)

        # raise if per_chunk >= 4 Gb, this is requested by h5py
        group.create_dataset(
            self.name, shape, dtype=self.dtype,
            chunks=chunks, maxshape=maxshape, compression=compression,
            compression_opts=compression_opts)
