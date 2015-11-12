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

"""Provides the Data class to the h5features package."""

from .items import Items
from .labels import Labels
from .features import Features, SparseFeatures
from .index import create_index, write_index


class Data(object):
    """This class manages h5features data."""
    def __init__(self, items, labels, features, sparsity=None, check=True):
        if check and not (len(items) == len(labels) == len(features)):
            raise ValueError('all entries must have the same length ({} {} {})'
                             .format(len(items), len(labels), len(features)))

        self._entries = {}
        self._entries['items'] = Items(items, check)
        self._entries['labels'] = Labels(labels, check)
        self._entries['features'] = (
            Features(features, check) if sparsity is None else
            SparseFeatures(features, sparsity, check))

    def __eq__(self, other):
        return self._entries == other._entries

    def _data(self, key):
        return self._entries[key].data

    def _dict_entry(self, key):
        return dict(zip(self.items(), self._data(key)))

    def is_empty(self):
        return len(self.items()) == 0

    def clear(self):
        """Erase stored data"""
        for e in self._entries.values():
            e.clear()

    def append(self, data):
        """Append a Data instance to self"""
        for k in self._entries.keys():
            self._entries[k].append(data._entries[k])

    def items(self):
        """Returns the stored items as a list of str."""
        return self._data('items')

    def labels(self):
        """Returns the stored labels as a list."""
        return self._data('labels')

    def features(self):
        """Returns the stored features as a list of numpy arrays."""
        return self._data('features')

    def dict_features(self):
        """Returns a items/features dictionary."""
        return self._dict_entry('features')

    def dict_labels(self):
        """Returns a items/labels dictionary."""
        return self._dict_entry('labels')

    def init_group(self, group, chunk_size):
        """Initializes a HDF5 group compliant with the stored data.

        This method creates the datasets 'items', 'labels', 'features'
        and 'index' and leaves them empty.

        :param h5py.Group group: The group to initializes.
        :param float chunk_size: The size of a chunk in the file (in MB).

        """
        create_index(group, chunk_size)
        self._entries['items'].create_dataset(group, chunk_size)
        self._entries['features'].create_dataset(group, chunk_size)
        # chunking the labels depends on features chunks
        self._entries['labels'].create_dataset(
            group, self._entries['features'].nb_per_chunk)

    def is_appendable_to(self, group):
        """Returns True if the data can be appended in a given group."""
        # First check only the names
        if not all([k in group for k in self._entries.keys()]):
            return False
        # If names are matching, check the contents
        for k in self._entries.keys():
            if not self._entries[k].is_appendable_to(group):
                return False
        return True

    def write_to(self, group, append=False):
        """Write the data to the given group.

        :param h5py.Group group: The group to write the data on. It is
            assumed that the group is already existing or initialized
            to store h5features data (i.e. the method
            ``Data.init_group`` have been called.

        :param bool append: If False, any existing data in the group
            is overwrited. If True, the data is appended to the end of
            the group and we assume ``Data.is_appendable_to`` is True
            for this group.

        """
        write_index(self, group, append)
        self._entries['items'].write_to(group)
        self._entries['features'].write_to(group, append)
        self._entries['labels'].write_to(group)
