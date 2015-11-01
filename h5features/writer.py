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

"""Provides the Writer class to the h5features module."""

import h5py
import os

from .dataset import is_appendable_to
from .index import create_index, write_index
from .version import is_supported_version


class Writer(object):
    """This class provides an interface for writing to h5features files.

    :param str filename: The name of the HDF5 file to write on. For
        clarity you should use a '\*.h5' extension but this is not
        required.

    :param float chunk_size: Optional. The size in Mo of a chunk in
        the file. Default is 0.1 Mo. A chunk size below 8 Ko is not
        allowed as it results in poor performances.

    :param str version: Optional. The file format version to write.

    :raise IOError: if the file exists but is not HDF5.
    :raise IOError: if the chunk size is below 8 Ko.
    :raise IOError: if the requested version is not supported.

    """
    def __init__(self, filename, chunk_size=0.1, version='1.1'):
        if not is_supported_version(version):
            raise IOError('version {} is not supported'.format(version))
        self.version = version

        if os.path.isfile(filename) and not h5py.is_hdf5(filename):
            raise IOError('{} is not a HDF5 file.'.format(filename))
        self.filename = filename

        if chunk_size < 0.008:
            raise IOError('chunk size is below 8 Ko')
        self.chunk_size = chunk_size


    def write(self, data, groupname='h5features', append=True):
        """Write h5features data in a specified group of the file.

        :param dict data: A dictionary of h5features datasets. It must
          contains 'items', 'times' and 'features' keys pointing to
          Items, Times and Features instances respectively.

        :param str groupname: Optional. The name of the group in which
          to write the data.

        :param bool append: Optional. This parameter has no effect if
           the `groupname` is not an existing group in the file. If
           set to True (default), try to append new data in the
           group. If False erase all data in the group before writing.

        :raise IOError: if append requested but not possible.

        """
        # Open the HDF5 file for writing/appending in the group.
        with h5py.File(self.filename, mode='a') as h5file:
            if append and groupname in h5file:
                group = h5file[groupname]

                # want to append data, raise if we cannot
                if not is_appendable_to(data, group):
                    raise IOError('data is not appendable to the group '
                                  '{} in {}'.format(groupname, self.filename))

            else:
                # erase the group if it exists
                if groupname in h5file:
                    del h5file[groupname]

                group = self.create_group(h5file, groupname, data)

            # Finally write index and data
            write_index(group, data['items'], data['features'], append)
            for dset in ['items', 'times', 'features']:
                data[dset].write(group)

    def create_group(self, h5file, groupname, data):
        """Initialize a HDF5 group for writing h5features.

        :param h5py.File h5file: An opened HDF5 file

        :param str groupname: The name of the group to initialize in
          the file

        :param dict data: A dictionary of h5features datasets. See
          `Writer.write()`

        :return: The created group.
        """
        group = h5file.create_group(groupname)
        group.attrs['version'] = self.version

        # create empty datasets
        create_index(group, self.chunk_size)
        data['features'].create_dataset(group, self.chunk_size)
        data['items'].create_dataset(group, self.chunk_size)
        # chunking the times depends on features chunks
        data['times'].create_dataset(group, data['features'].nb_per_chunk)

        return group
