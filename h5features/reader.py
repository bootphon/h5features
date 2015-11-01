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

"""Provides the Reader class to the h5features package."""

import h5py
import os
import numpy as np

from .features import Features
from .items import Items, read_items
from .times import Times
from .index import read_index
from .version import read_version

class Reader(object):
    """This class provides an interface for reading from h5features files.

    A `Reader` object wrap a h5features file. When created it loads
    items, times and index from file. The read() method allows
    fast access to features data.

    :param str filename: Path to the HDF5 file to read from.

    :param str groupname: Name of the group to read from in the file.

    :raise IOError: if `filename` is not an existing HDF5 file or
        if `groupname` is not a valid group in `filename`.

    """
    def __init__(self, filename, groupname):
        # open the file for reading
        if not os.path.exists(filename) or not h5py.is_hdf5(filename):
            raise IOError('{} is not a HDF5 file'.format(filename))
        self.h5file = h5py.File(filename, 'r')

        # open the requested group in the file
        if not groupname in self.h5file:
            raise IOError('{} is not a valid group in {}'
                          .format(groupname, filename))
        self.group = self.h5file[groupname]

        # load h5features attributes and datasets
        self.version = read_version(self.group)
        self.index = read_index(self.group, self.version)
        self.items = read_items(self.group, self.version)

        self.dformat = self.group.attrs['format']
        if self.dformat == 'sparse':
            self.dim = self.group.attrs['dim']
            self.frames = (self.group['lines'] if self.version == '0.1'
                           else self.group['frames'])[...]

    # def __del__(self):
    #     self.h5file.close()

    def index_read(self, index):
        """Read data from its indexed coordinate"""
        raise NotImplementedError

    def read(self, from_item=None, to_item=None,
             from_time=None, to_time=None):
        """Retrieve requested data coordinates from the h5features index.

        :param str from_item: Optional. Read the data starting from
            this item. (defaults to the first stored item)

        :param str to_item: Optional. Read the data until reaching the
            item. (defaults to from_item if it was specified and to
            the last stored item otherwise).

        :param float from_time: Optional. (defaults to the beginning
            time in from_item) The specified times are included in the
            output.

        :param float to_time: Optional. (defaults to the ending time
            in to_item) the specified times are included in the
            output.

        :return: A dictionary where keys are 'items', 'times, and
            'features' and the values are instances of Items, Times, and
            Features repectively.

        """
        # handling default arguments
        if to_item is None:
            to_item = self.items.data[-1] if from_item is None else from_item
        if from_item is None:
            from_item = self.items.data[0]

        # index coordinates of from/to_item. TODO optimize because we
        # have 4 accesses to list.index() where 2 are enougth.
        if not self.items.is_valid_interval(from_item, to_item):
            raise IOError('cannot read items: not a valid items interval')
        from_idx = self.items.data.index(from_item)
        to_idx = self.items.data.index(to_item)

        from_pos = self._get_item_position(from_idx)
        to_pos = self._get_item_position(to_idx)

        lower = self._get_from_time(from_time, from_pos)
        upper = self._get_to_time(to_time, to_pos)

        # Step 2: access actual data
        if self.dformat == 'sparse':
            # TODO implement this. will be different for v1.0 and legacy
            raise NotImplementedError('Reading sparse features not implemented')
        else:
            # i2 included
            features = (self.group['features'][:, lower:upper + 1].T
                        if self.version == '0.1'
                        else self.group['features'][lower:upper + 1, :])
            times = self.group['times'][lower:upper + 1]

        # If we read a single item
        if to_idx == from_idx:
            features = [features]
            times = [times]
        else: # Several items case
            item_ends = self.index[from_idx:to_idx] - from_pos[0] + 1
            features = np.split(features, item_ends, axis=0)
            times = np.split(times, item_ends, axis=0)

        items = self.items.data[from_idx:to_idx + 1]
        return (Items(items),
                Times(times),
                Features(features))

    def _get_item_position(self, idx):
        """Return a tuple of (start, end) indices of an item given its index."""
        start = 0 if idx == 0 else self.index[idx - 1] + 1
        end = self.index[idx]
        return start, end

    def _get_from_time(self, time, pos):
        group = self.group['times']
        if time is None:
            i1 = pos[0]
        else:
            # the end is included...
            times = group[pos[0]:pos[1] + 1]
            try:
                # smallest time larger or equal to from_time
                i1 = pos[0] + np.where(times >= time)[0][0]
            except IndexError:
                raise IOError('time {} is too large'.format(time))
        return i1

    def _get_to_time(self, time, pos):
        group = self.group['times']
        if time is None:
            i2 = pos[1]
        else:
            # the end is included...
            times = group[pos[0]:pos[1] + 1]
            try:
                # smallest time larger or equal to from_time
                i2 = pos[0] + np.where(times <= time)[0][-1]
            except IndexError:
                raise IOError('time {} is too small'.format(time))
        return i2
