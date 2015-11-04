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
"""Provides the Dataset interface implemented by Features, Times and Items."""

import numpy as np

from .version import is_same_version


def is_same_dataset(data, group):
    """Check that dataset names are consistent between `data` and a `group`.

    This function is used internally by the `Writer`. Only the names
    of the datasets are accessed, not their content.

    :param dict data: A dictionary as specified in `Writer.write()`
    :param group: The group to compare the dataset with
    :type group: HDF5 group

    :return: True if each dataset in `data` is present in the
      `group`. False else.

    """
    names = [data['items'].name,
             data['times'].name,
             data['features'].name]

    if data['features'].is_sparse():
        names += ['frames', 'coordinates']

    return all([name in group for name in names])


def is_appendable_to(data, group, version='1.1'):
    """Check if `data` can be appended in a h5features `group`.

    A dataset is apendable in a group if both names and shapes are
    consistent.

    :param dict data: A dictionary of h5features datasets. See
        `Writer.write()`

    :param group: A group in an opened HDF5 file.

    :type group: HDF5 group

    :param str version: The h5features version of the `group`.

    :return: True if `data` is appendable to the `group`.

    """
    return (is_same_version(version, group) and
            is_same_dataset(data, group) and
            all([data[k].is_appendable_to(group)
                 for k in ('features', 'items', 'times')]))


def nb_per_chunk(item_size, item_dim, chunk_size):
    """Return the number of items that can be stored in one chunk.

    This function is used internally by the *Dataset.create_dataset*
    method.

    :param int item_size: Size of an item's scalar componant in
        Bytes (e.g. for np.float64 this is 8)

    :param int item_dim: Items dimension (length of the second axis)

    :param float chunk_size: The size of a chunk given in MBytes.

    """
    # from Mbytes to bytes
    size = chunk_size * 10.**6
    ratio = int(round(size / (item_size*item_dim)))
    return max(10, ratio)


class Dataset(object):
    """The Dataset class is an **abstract base class** of h5features data.

    It provides a shared interface to the classes `Index`, `Items`,
    `Times` and 'Features' which all together constitutes an
    h5features file.

    """
    def __init__(self, data, name, dim, dtype):
        self.name = name
        self.dim = dim
        self.dtype = dtype
        self.data = data

    def __eq__(self, other):
        if self is other:
            return True

        try:
            return (self.name == other.name and
                    self.dim == other.dim and
                    self.dtype == other.dtype and
                    self.data == other.data)
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def create_dataset(self, group, chunk_size):
        """Create an empty dataset in an HDF5 group.

        :param h5py.Group group: The group where to create a dataset.

        :param float chunk_size: In MB, the desired size of a data
            chunk in the file.

        """
        shape = (0,) if self.dim == 1 else (0, self.dim)
        maxshape = (None,) if self.dim == 1 else (None, self.dim)

        if self.dtype == np.dtype('O'):
            # if dtype is a variable str, guess representative size is 20 bytes
            per_chunk = nb_per_chunk(20, self.dim, chunk_size)
        else:
            per_chunk = nb_per_chunk(np.dtype(self.dtype).itemsize,
                                     self.dim, chunk_size)

        chunks = (per_chunk,) if self.dim == 1 else (per_chunk, self.dim)

        # raise if per_chunk >= 4 Gb, this is requested by h5py
        group.create_dataset(self.name, shape, dtype=self.dtype,
                             chunks=chunks, maxshape=maxshape)
