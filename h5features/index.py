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
"""Provides indexing facilities to the h5features package.

This index typically allows a faster read access in large datasets and
is transparent to the user.

Because the h5features package is designed to handle large datasets,
features and times data is internally stored in a compact *indexed*
representation.

"""

import numpy as np
from .entry import nb_per_chunk


def cumindex(features):
    """Return the index computed from features."""
    return np.cumsum([x.shape[0] for x in features.data])


def create_index(group, chunk_size, compression=None, compression_opts=None):
    """Create an empty index dataset in the given group."""
    dtype = np.int64
    if chunk_size == 'auto':
        chunks = True
    else:
        chunks = (nb_per_chunk(np.dtype(dtype).itemsize, 1, chunk_size),)

    group.create_dataset(
        'index', (0,), dtype=dtype,
        chunks=chunks, maxshape=(None,),
        compression=compression, compression_opts=compression_opts)


def write_index(data, group, append):
    """Write the data index to the given group.

    :param h5features.Data data: The that is being indexed.
    :param h5py.Group group: The group where to write the index.
    :param bool append: If True, append the created index to the
        existing one in the `group`. Delete any existing data in index
        if False.

    """
    # build the index from data
    nitems = group['items'].shape[0] if 'items' in group else 0
    last_index = group['index'][-1] if nitems > 0 else -1
    index = last_index + cumindex(data._entries['features'])

    if append:
        nidx = group['index'].shape[0]
        # # in case we append to the end of an existing item
        # if data._entries['items']._continue_last_item(group):
        #     nidx -= 1

        group['index'].resize((nidx + index.shape[0],))
        group['index'][nidx:] = index
    else:
        group['index'].resize((index.shape[0],))
        group['index'][...] = index


def read_index(group, version='1.1'):
    """Return the index stored in a h5features group.

    :param h5py.Group group: The group to read the index from.
    :param str version: The h5features version of the `group`.
    :return: a 1D numpy array of features indices.
    """
    if version == '0.1':
        return np.int64(group['index'][...])
    elif version == '1.0':
        return group['file_index'][...]
    else:
        return group['index'][...]
