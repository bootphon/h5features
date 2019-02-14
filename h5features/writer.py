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

"""Provides the Writer class to the h5features module."""

import h5py
import numbers
import os

from .version import is_supported_version, is_same_version


class Writer(object):
    """This class provides an interface for writing to h5features files.

    :param str filename: The name of the HDF5 file to write on. For
        clarity you should use a '.h5' or '.h5f' extension but this is
        not required by the package.

    :param float_or_str chunk_size: Optional. The size in Mo of a
        chunk in the file, or 'auto' to let HDF5 guess a chunk size
        automatically. Default is 'auto'. A chunk size below 8 Ko is
        not allowed as it results in poor performances.

    :param str version: Optional. The file format version to write,
        default is to write the latest version.

    :param char mode: Optional. The mode for overwriting an existing
        file, 'a' to append data to the file, 'w' to overwrite it

    :param str_or_int_or_none compression: Optional. Whether to
        compress the data or not. If None, do not compress. If a
        string, must be 'gzip' or 'lzf'. If an integer, uses 'gzip'
        and indicates the compression level, must be from 0 to 9 (if
        'gzip' specified, the compression level is is 4). 'gzip' has
        good compression, moderate speed, 'lzf' has low to moderate
        compression, very fast speed. If appending data to an existing
        uncompressed group, data will not be compressed.

    :raise IOError: if the file exists but is not HDF5, if the file
        can be opened, if the mode is not 'a' or 'w', if the chunk
        size is below 8 Ko, if the requested version is not
        supported or if the specified compression is not valid.

    """
    def __init__(self, filename, chunk_size='auto', version='1.1',
                 mode='a', compression=None):
        # check version
        if not is_supported_version(version):
            raise IOError('version {} is not supported'.format(version))
        self.version = version

        # check filename
        if os.path.isfile(filename) and not h5py.is_hdf5(filename):
            raise IOError('{} is not a HDF5 file.'.format(filename))
        self.filename = filename

        # check chunk size
        if not chunk_size == 'auto':
            if not isinstance(chunk_size, numbers.Number):
                raise IOError(
                    "chunk size must be 'auto' or a number, it is {}"
                    .format(chunk_size))
            if chunk_size < 0.008:
                raise IOError('chunk size is below 8 Ko')
        self.chunk_size = chunk_size

        # check mode
        if mode not in ('w', 'a'):
            raise IOError(
                "mode for writing must be 'a' or 'w', it is '{}'".format(mode))

        # check compression
        if compression is None:
            self.compression = None
            self.compression_opts = None
        elif isinstance(compression, str):
            if compression not in ('gzip', 'lzf'):
                raise IOError(
                    "compression must be 'gzip' or 'lzf', it is '{}'"
                    .format(compression))
            self.compression = compression
            self.compression_opts = None
        elif isinstance(compression, int):
            if not 0 <= compression <= 9:
                raise IOError(
                    'compression level must be in [0, 9], it is {}'
                    .format(compression))
            self.compression = 'gzip'
            self.compression_opts = compression
        else:
            raise IOError("compression must be None, 'gzip', 'lzf' or an int")

        try:
            self.h5file = h5py.File(self.filename, mode=mode)
        except OSError:
            raise IOError('file {} cannot be opened'.format(self.filename))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Close the HDF5 file."""
        self.h5file.close()

    def write(self, data, groupname='h5features', append=False):
        """Write h5features data in a specified group of the file.

        :param dict data: A `h5features.Data` instance to be writed on disk.

        :param str groupname: Optional. The name of the group in which
            to write the data.

        :param bool append: Optional. This parameter has no effect if
           the `groupname` is not an existing group in the file. If
           set to True, try to append new data in the group. If False
           (default) erase all data in the group before writing.

        :raise IOError: if append requested but not possible.

        """
        if append and groupname in self.h5file:
            # append data to the group, raise if we cannot
            group = self.h5file[groupname]
            if not is_same_version(self.version, group):
                raise IOError(
                    'data is not appendable to the group {}: '
                    'versions are different'.format(group.name))

            if not data.is_appendable_to(group):
                raise IOError(
                    'data is not appendable to the group {}'
                    .format(group.name))
        else:  # overwrite any existing data in group
            group = self._prepare(data, groupname)

        data.write_to(group, append)

    def _prepare(self, data, groupname):
        """Clear the group if existing and initialize empty datasets."""
        if groupname in self.h5file:
            del self.h5file[groupname]
        group = self.h5file.create_group(groupname)
        group.attrs['version'] = self.version
        data.init_group(
            group, self.chunk_size, self.compression, self.compression_opts)
        return group
