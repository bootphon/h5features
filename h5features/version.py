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
"""Provides functions related to h5features versions."""

SUPPORTED_VERSIONS = ['0.1', '1.0', '1.1']
"""The different versions supported by the h5features module """


def is_supported_version(version):
    """Return True if the version is supported by h5features."""
    return version in SUPPORTED_VERSIONS


def is_same_version(version, group):
    """Return True if *version* and *group* versions are equals."""
    return version == read_version(group)


def read_version(group):
    """Return the h5features version of a given HDF5 *group*.

    This method raise IOError if version is not supported.

    """
    version = ('0.1' if not 'version' in group.attrs
               else group.attrs['version'])

    # decode from bytes to str if needed
    if type(version) == bytes:
        version = version.decode()

    if not is_supported_version(version):
        raise IOError('version {} is not supported'.format(version))

    return version
