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
"""Provides versioning facilities to the h5features package.

This module manages the h5features **file format versions**, specified
as strings in the format 'major.minor'. File format versions are
independant of the h5feature package version (but actually follow the
same numerotation scheme).

The module provides functions to list supported versions, read a
version from a h5features file or check a specific version is
supported.

"""


def supported_versions():
    """Return the list of file format versions supported by h5features."""
    return ['0.1', '1.0', '1.1']


def is_supported_version(version):
    """Return True if the `version` is supported by h5features."""
    return version in supported_versions()


def is_same_version(version, group):
    """Return True if `version` and `read_version(group)` are equals."""
    return version == read_version(group)


def read_version(group):
    """Return the h5features version of a given HDF5 `group`.

    Look for a 'version' attribute in the `group` and return its
    value. Return '0.1' if the version is not found. Raises an IOError
    if it is not supported.

    """
    version = ('0.1' if 'version' not in group.attrs
               else group.attrs['version'])

    # decode from bytes to str if needed
    if isinstance(version, bytes):
        version = version.decode()

    if not is_supported_version(version):
        raise IOError('version {} is not supported'.format(version))

    return version
