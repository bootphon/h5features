"""Provides the Writer class to the h5features module.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import h5py
import numpy as np
import os

from h5features2.utils import is_supported_version, nb_lines
from h5features2.index import Index

class Writer(object):
    """This class provides an interface for writing h5features to HDF5 files."""

    def __init__(self, filename, chunk_size=0.1, version='1.1'):
        """Initialize an HDF5 file for writing h5features.

        Parameters
        ----------

        filename : str --- The name of the HDF5 file to write on. For
            clarity you should use a *.h5 extension but this is not
            required.

        chunk_size : float, optional --- The size in Mo of a chunk in
            the file. Default is 0.1 Mo. A chunk size below 8 Ko is
            not allowed as it results in poor performances.

        Raise
        -----

        IOError if the file exists but is not HDF5.
        IOError if the chunk size is below 8 Ko.

        """
        if not is_supported_version(version):
            raise IOError('version {} is not supported'.format(version))
        self.version = version

        # Raise if the file exists but is not HDF5
        if os.path.isfile(filename) and not h5py.is_hdf5(filename):
            raise IOError('{} is not a HDF5 file.'.format(filename))
        self.filename = filename

        if chunk_size < 0.008:
            raise IOError('chunk size is below 8 Ko')
        self.chunk_size = chunk_size


    def write(self, data, groupname='features', append=True):
        """Write h5features data in a specified group.

        Parameters
        ----------

        data : dict --- TODO document this!

        groupname : str, optional --- The name of the group in which
            to write the data.

        """
        # TODO Raise if
        # Open the HDF5 file for writing/appending.
        with h5py.File(self.filename, mode='a') as h5file:
            index = Index()
            # If the group already exists, try to append data.
            if groupname in h5file:
                group = h5file[groupname]
                # raise if we want but cannot append
                if append and not self.is_compatible(group, data):
                    raise IOError('data is not appendable to the group {} in {}'
                                  .format(groupname, self.filename))
                if not append:
                    del group
            else:
                # The group does not exist, create it
                group = h5file.create_group(groupname)
                group.attrs['version'] = self.version
                # TODO uniformize chunk stuffs...

                nb_in_chunks = data['features'].create(group, self.chunk_size)
                data['times'].create(group, nb_in_chunks)

                # typical filename is 20 characters i.e. around 20 bytes
                nb_lines_by_chunk = max(10, nb_lines(20, 1, self.chunk_size*1000))

                data['items'].create(group, nb_lines_by_chunk)
                index.create(group, self.chunk_size)

            # writing data
            # TODO assert no side effects here... In that
            # order it's order but what happens if it is changed?
            # e.g. writting features concat them in place...
            index.write(group, data['items'], data['features'])
            for dataset in data.values():
                dataset.write(group)

    # TODO raise error message ?
    def is_compatible(self, group, data):
        """Raise IOError if the data is not compatible with the group."""
        return (self.is_same_version(group) and
                self.is_same_datasets(group, data) and
                all([data[k].is_compatible(group)
                     for k in ('features', 'items', 'times')]))

    def is_same_version(self, group):
        """Return True if self and group versions are the same."""
        try:
            return group.attrs['version'] == self.version
        except IndexError:
            return False

    # TODO bad design: self or data ? And the index ?
    def is_same_datasets(self, group, data):
        datasets = [data['items'].name,
                    data['times'].name,
                    data['features'].name]
        if data['features'].dformat == 'sparse':
            datasets += ['frames', 'coordinates']
        return all([d in group for d in datasets])
