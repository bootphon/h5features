"""Provides a write function for h5features files."""

import h5py
import numpy as np
import os


from h5features2 import chunk
from h5features2.features import Features, SparseFeatures, parse_dformat
from h5features2.index import Index
from h5features2.items import Items
from h5features2.times import Times, Times2D, parse_times

def write(filename, groupname, items_data, times_data, features_data,
          dformat='dense', chunk_size=0.1, sparsity=0.1):
    """Write in a h5features file.

    Parameters
    ----------

    filename : str -- HDF5 file to be writted, potentially serving as
        a container for many small files. If the file does not exist,
        it is created. If the file is already a valid HDF5 file, try
        to append the data in it.

    groupname : str -- h5 group to write the data in, or to append
        the data to if the group already exists in the file.

    items_data : list of str -- List of files from which the features where
        extracted.

    times_data : list of 1D or 2D numpy array like -- Time value for the
        features array. Elements of a 1D array are considered as the
        center of the time window associated with the features. A 2D
        array must have 2 columns corresponding to the begin and end
        timestamps of the features time window.

    features_data : list of 2D numpy array like -- Features should have
        time along the lines and features along the columns
        (accomodating row-major storage in hdf5 files).

    dformat : str, optional -- Which format to store the
        features into (sparse or dense). Default is dense.

    chunk_size : float, optional -- In Mo, tuning parameter
        corresponding to the size of a chunk in the h5file. Ignored if
        the file already exists.

    sparsity : float, optional -- Tuning parameter corresponding to
        the expected proportion of non-zeros elements on average in a
        single frame.

    Raise
    -----

    IOError if filename is not valid or if parameters are not consistent.

    NotImplementedError if features_format == 'sparse'

    """
    # File format version TODO Get it from setup.py
    version = '1.0'

    # Prepare parameters, look for errors and raise if any.
    check_file(filename)
    chunk.check_size(chunk_size)
    index = Index()
    items = Items(items_data)

    # Instanciate either 1D or 2D Times class
    times = (Times2D(times_data)
             if parse_times(times_data) == 2
             else Times(times_data))

    # Instanciate either dense or sparse Features class
    features = (SparseFeatures(features_data, sparsity)
                if parse_dformat(dformat) == 'sparse'
                else Features(features_data))

    # Open the HDF5 file for writing/appending.
    with h5py.File(filename, mode='a') as h5file:
        # If group does not exists in file, create it
        if not groupname in h5file:
            group = h5file.create_group(groupname)
            group.attrs['version'] = version

            nb_in_chunks = features.create(group, chunk_size)
            times.create(group, nb_in_chunks)

            # typical filename is 20 characters i.e. around 20 bytes
            nb_lines_by_chunk = max(10, chunk.nb_lines(20, 1, chunk_size * 1000))
            items.create(group, nb_lines_by_chunk)

            index.create(group, chunk_size)

        else: # The group exists
            group = h5file[groupname]

            # raise if we cannot append data to it.
            appendable(group, features, times, version)

        # writing data
        # TODO assert no side effects here !
        index.write(group, items, features)
        items.write(group)
        features.write(group)
        times.write(group)


def simple_write(filename, group, times, features, fileid='features'):
    """Simplified version of write when there is only one file
    """
    write(filename, group, [fileid], [times], [features])


def check_file(filename):
    """Check the file is a writable HDF5 file.

    Raise an IOError if the file does not exists, is not writable, or
    is not a HDF5 file.

    """
    # Raise if the file exists but is not HDF5
    if os.path.isfile(filename):
        if not h5py.is_hdf5(filename):
            raise IOError('{} is not a HDF5 file.'.format(filename))

    # Raise if the file is not writable
    # TODO no need to create/delete the file.
    else:
        try:
            temp = open(filename, 'w')
            temp.close()
            os.remove(filename)
        except OSError as error:
            raise IOError(error)


def appendable(group, features, times, version):
    """Raise IOError if the data is not appendable in the group."""
    if not is_same_version(group, version):
        raise IOError('Files have incompatible version of h5features')

    if not times.is_compatible(group):
        raise IOError('Files must have the same time format')

    if not is_same_datasets(group, features.dformat):
        raise IOError('group {} is not a valid h5features file:'
                      ' missing dataset'.format(group.name[1:]))

    if not features.is_compatible(group):
        raise IOError('Features datasets are not compatible.')


def is_same_version(group, version):
    """Return True if local version and group version are the same."""
    return group.attrs['version'] == version


def is_same_datasets(group, dformat):
    # The datasets that will be writted on the HDF5 file
    datasets = ['items', 'times', 'features', 'file_index']
    if dformat == 'sparse':
        datasets += ['frames', 'coordinates']

    return all([d in group for d in datasets])
