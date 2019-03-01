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
"""Provides the Properties class to the h5features package."""

import numpy as np
import pickle


def read_properties(group):
    """Returns properties loaded from a group"""
    if 'properties' not in group.attrs.keys():
        raise IOError('no properties in group')

    return pickle.loads(group.attrs['properties'].tostring())


class Properties(object):
    def __init__(self, data, check=True):
        if check is True:
            if not (
                    isinstance(data, list)
                    and all([isinstance(d, dict) for d in data])
            ):
                raise IOError('properties must be a list of dictionnaries')

        self.data = data

    def __eq__(self, other):
        # lists of dictionaries must have the same length
        if len(self.data) != len(other.data):
            return False

        # each pair of dicts must be equal
        for n in range(len(self.data)):
            if not self._eq_dicts(self.data[n], other.data[n]):
                return False

        return True

    @staticmethod
    def _eq_dicts(d1, d2):
        """Returns True if d1 == d2, False otherwise"""
        if not d1.keys() == d2.keys():
            return False

        for k, v1 in d1.items():
            v2 = d2[k]
            if not type(v1) == type(v2):
                return False
            if isinstance(v1, np.ndarray):
                if not np.array_equal(v1, v2):
                    return False
            else:
                if not v1 == v2:
                    return False
        return True

    def is_appendable_to(self, group):
        return 'properties' in group.attrs.keys()

    def write_to(self, group, append=False):
        """Writes the properties to a `group`, or append it"""
        data = self.data
        if append:
            # concatenate original and new properties in a single list
            original = read_properties(group)
            data = original + data

        group.attrs['properties'] = np.void(pickle.dumps(data))
