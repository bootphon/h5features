"""Provides the Writer class to the h5features module.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import h5py
import numpy as np
import os

from h5features2 import chunk
from h5features2.index import Index


def parse_filename(filename):
    """Check if the file is a writable HDF5 file.

    Raise an IOError if the file does not exists, is not writable, or
    is not a HDF5 file.

    """
    # Raise if the file exists but is not HDF5
    if os.path.isfile(filename):
        if not h5py.is_hdf5(filename):
            raise IOError('{} is not a HDF5 file.'.format(filename))

    # # Raise if the file is not writable
    # # TODO no need to create/delete the file.
    # else:
    #     try:
    #         temp = open(filename, 'w')
    #         temp.close()
    #         os.remove(filename)
    #     except OSError as error:
    #         raise IOError(error)

    return filename


class Writer(object):
    def __init__(self, filename, chunk_size):
        # File format version TODO Get it from setup.py
        self.version = '1.0'

        self.filename = parse_filename(filename)
        self.chunk_size = chunk.check_size(chunk_size)

    def write(self, groupname, data):
        features = data['features']
        items = data['items']
        times = data['times']

        # Open the HDF5 file for writing/appending.
        with h5py.File(self.filename, mode='a') as h5file:
            # Init an empty index
            index = Index()

            # If group does not exists in file, create it
            if not groupname in h5file:
                group = h5file.create_group(groupname)
                group.attrs['version'] = self.version

                nb_in_chunks = features.create(group, self.chunk_size)
                times.create(group, nb_in_chunks)

                # typical filename is 20 characters i.e. around 20 bytes
                nb_lines_by_chunk = max(10, chunk.nb_lines(
                    20, 1, self.chunk_size * 1000))

                items.create(group, nb_lines_by_chunk)
                index.create(group, self.chunk_size)

            else: # The group exists
                group = h5file[groupname]

                # raise if we cannot append data to it.
                self.is_appendable(group, features, times)

            # writing data
            # TODO assert no side effects here !
            index.write(group, items, features)
            items.write(group)
            features.write(group)
            times.write(group)

    def append(self, groupname, data):
        pass

    def is_appendable(self, group, features, times):
        """Raise IOError if the data is not appendable in the group."""
        if not self.is_same_version(group):
            raise IOError('Files have incompatible version of h5features')

        if not times.is_compatible(group):
            raise IOError('Files must have the same time format')

        if not self.is_same_datasets(group, features.dformat):
            raise IOError('group {} is not a valid h5features file:'
                          ' missing dataset'.format(group.name[1:]))

        if not features.is_compatible(group):
            raise IOError('Features datasets are not compatible.')

    def is_same_version(self, group):
        """Return True if local version and group version are the same."""
        return group.attrs['version'] == self.version

    def is_same_datasets(self, group, dformat):
        # TODO build datasets as attribute -> deal with custom names
        # The datasets that will be writted on the HDF5 file
        datasets = ['items', 'times', 'features', 'file_index']
        if dformat == 'sparse':
            datasets += ['frames', 'coordinates']

        return all([d in group for d in datasets])
