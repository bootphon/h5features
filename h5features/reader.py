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

from .data import Data
from .items import read_items
from .index import read_index
from .version import read_version

class Reader(object):
    """This class provides an interface for reading from h5features files.

    A `Reader` object wrap a h5features file. When created it loads
    items and index from file. The read() method then allows fast
    access to features and times data.

    :param str filename: Path to the HDF5 file to read from.

    :param str groupname: Name of the group to read from in the
        file. If None, guess there is one and only one group in
        `filename`.

    :raise IOError: if `filename` is not an existing HDF5 file or
        if `groupname` is not a valid group in `filename`.

    """
    def __init__(self, filename, groupname=None):
        # open the file for reading
        if not os.path.exists(filename) or not h5py.is_hdf5(filename):
            raise IOError('{} is not a HDF5 file'.format(filename))
        self.h5file = h5py.File(filename, 'r')

        # open the requested group in the file
        if groupname is None:
            # expect only one group in the file
            groups = list(self.h5file.keys())
            if not len(groups) == 1:
                raise IOError('groupname is None and cannot be guessed in {}.'
                              .format(filename))
            groupname = groups[0]
        elif not groupname in self.h5file:
            raise IOError('{} is not a valid group in {}'
                          .format(groupname, filename))
        self.group = self.h5file[groupname]

        # load h5features attributes and datasets
        self.version = read_version(self.group)
        self.items = read_items(self.group, self.version)
        self._index = read_index(self.group, self.version)

        self.dformat = self.group.attrs['format']
        if self.dformat == 'sparse':
            self.dim = self.group.attrs['dim']
            self.frames = (self.group['lines'] if self.version == '0.1'
                           else self.group['frames'])[...]

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.h5file.close()

    def index_read(self, index):
        """Read data from its indexed coordinate"""
        # TODO
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
            raise IOError('cannot read items: not a valid interval')
        from_idx = self.items.data.index(from_item)
        to_idx = self.items.data.index(to_item)

        from_pos = self._get_item_position(from_idx)
        to_pos = self._get_item_position(to_idx)

        lower = self._get_from_time(from_time, from_pos)
        # upper included with +1
        upper = 1 + self._get_to_time(to_time, to_pos)

        # Step 2: access actual data
        if self.dformat == 'sparse':
            raise NotImplementedError('Reading sparse features not implemented')
        else:
            features = (self.group['features'][:, lower:upper].T
                        if self.version == '0.1'
                        else self.group['features'][lower:upper, :])
            labels = (self.group['labels'][lower:upper]
                      if self.version >= '1.1' else
                      self.group['times'][lower:upper])

        # If we read a single item
        if to_idx == from_idx:
            features = [features]
            labels = [labels]
        else: # Several items case: unindex data
            item_ends = self._index[from_idx:to_idx] - from_pos[0] + 1
            features = np.split(features, item_ends, axis=0)
            labels = np.split(labels, item_ends, axis=0)

        items = self.items.data[from_idx:to_idx + 1]

        return Data(items, labels, features, check=False)

    def _get_item_position(self, idx):
        """Return a tuple of (start, end) indices of an item given its index."""
        start = 0 if idx == 0 else self._index[idx - 1] + 1
        end = self._index[idx]
        return start, end

    def _get_from_time(self, time, pos):
        if time is None:
            return pos[0]
        else:
            times = self.group['times'][pos[0]:pos[1] + 1]
            try:
                return pos[0] + np.where(times >= time)[0][0]
            except IndexError:
                raise IOError('time {} is too large'.format(time))

    def _get_to_time(self, time, pos):
        if time is None:
            return pos[1]
        else:
            times = self.group['times'][pos[0]:pos[1] + 1]
            try:
                return pos[0] + np.where(times <= time)[0][-1]
            except IndexError:
                raise IOError('time {} is too small'.format(time))
