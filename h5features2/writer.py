"""Provides the Writer class to the h5features module.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import h5py
import os

from h5features2.utils import is_supported_version
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

        - data : dict --- TODO document this!

        - groupname : str, optional --- The name of the group in which
             to write the data.

        - append : bool, optional --- This parameter has no effect if
             the *groupname* is not an existing group in the file. If
             set to True (default), try to append new data in the
             group. If False erase all data in the group before
             writing.

        """
        # shortcut from parameters
        items = data['items']
        times = data['times']
        featu = data['features']

        # Open the HDF5 file for writing/appending in the group.
        with h5py.File(self.filename, mode='a') as h5file:
            # Initialize an empty index
            index = Index()

            # The group already exists
            if groupname in h5file:
                group = h5file[groupname]

                # want to append data, raise if we cannot
                if append and not self.is_appendable_to(group, data):
                    raise IOError('data is not appendable to the group {} in {}'
                                  .format(groupname, self.filename))

                # want to overwrite, delete the existing group
                # TODO test that
                if not append:
                    del group
            else:
                # The group does not exist, create it...
                group = h5file.create_group(groupname)
                group.attrs['version'] = self.version

                # ... and initialize it with empty datasets
                featu.create_dataset(group, self.chunk_size)
                items.create_dataset(group, self.chunk_size)
                index.create_dataset(group, self.chunk_size)
                # chunking the times depends on features chunks
                times.create_dataset(group, featu.nb_per_chunk)

            # writing data TODO assert no side effects here,
            # e.g. writting features concat them in place...
            index.write(group, data['items'], data['features'])
            for dataset in ['items', 'times', 'features']:
                data[dataset].write(group)

    def is_appendable_to(self, group, data):
        """Return True if the data is appendable to the group."""
        return (self.is_same_version(group) and
                self.is_same_datasets(group, data) and
                all([data[k].is_appendable_to(group)
                     for k in ('features', 'items', 'times')]))

    def is_same_version(self, group):
        """Return True if self and group versions are the same."""
        try:
            return group.attrs['version'] == self.version
        except IndexError: # version '0.1' doesn't have a version attribute
            return False

    # TODO bad design: self or data ? And the index ?
    def is_same_datasets(self, group, data):
        datasets = [data['items'].name,
                    data['times'].name,
                    data['features'].name]
        if data['features'].dformat == 'sparse':
            datasets += ['frames', 'coordinates']
        return all([d in group for d in datasets])
