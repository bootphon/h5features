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
from .times import Times
from .features import Features
from .index import create_index
#from .version import is_same_version

class Data(object):
    """This class communicates data to/from Reader and Writer."""

    def __init__(self, items, times, features, check=True):
        self.entries = {}
        self.entries['items'] = Items(items, check)
        self.entries['times'] = Times(times, check)
        self.entries['features'] = Features(features, check)

    def _dict_entry(self, entry):
        return dict(zip(self.entries['items'].data, entry.data))

    def dict_features(self):
        return self._dict_entry(self.entries['features'])

    def dict_times(self):
        return self._dict_entry(self.entries['times'])

    def size(self):
        """Return the data memory usage in Mo."""
        pass

    def create_group(self, group, chunk_size):
        create_index(group, chunk_size)
        self.entries['features'].create_dataset(group, chunk_size)
        self.entries['items'].create_dataset(group, chunk_size)
        # chunking the times depends on features chunks
        self.entries['times'].create_dataset(
            group, self.entries['features'].nb_per_chunk)

    def is_appendable_to(self, group):
        for k in self.entries.keys():
            if not self.entries[k].is_appendable_to(group):
                return False
        return True

class SparseData(Data):
    def __init__(self, items, times, features, sparsity, check=True):
        self.sparsity = sparsity
        super(SparseData, self).__init__(items, times, features, check)
