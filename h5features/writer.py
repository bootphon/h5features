"""Provides the Writer class to the h5features module.

Copyright 2014-2015, Thomas Schatz, Mathieu Bernard, Roland Thiolliere.
Licensed under GPLv3.

"""

import h5py
import os

from .version import is_supported_version, is_same_version
from .index import Index

# TODO Where is the index ?
def is_same_datasets(group, data):
    """Return True if each dataset in *data* is present in *group*.

    This function is used internally by the Witer.

    Parameters:

    *data* : dict --- A dictionary as specified in Writer.write
    *group* : HDF5 group --- The group to check dataset on.

    """
    datasets = [data['items'].name,
                data['times'].name,
                data['features'].name]
    if data['features'].dformat == 'sparse':
        datasets += ['frames', 'coordinates']
    return all([d in group for d in datasets])


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

        - data : dict(str -> Dataset) --- A dictionary of h5features
          Datasets. The dict must contain 'items', 'times' and
          'features' keys pointing to Items, Times and Features
          instances respectively.

        - groupname : str, optional --- The name of the group in which
             to write the data.

        - append : bool, optional --- This parameter has no effect if
             the *groupname* is not an existing group in the file. If
             set to True (default), try to append new data in the
             group. If False erase all data in the group before
             writing.

        """
        # shortcut for data access
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

            # writing data
            index.write(group, data['items'], data['features'])
            for dataset in ['items', 'times', 'features']:
                data[dataset].write(group)

    def is_appendable_to(self, group, data):
        """Return True if the *data* is appendable to the *group*."""
        return (is_same_version(self.version, group) and
                is_same_datasets(group, data) and
                all([data[k].is_appendable_to(group)
                     for k in ('features', 'items', 'times')]))
