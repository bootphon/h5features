"""Provides a write function for h5features files."""

import h5py
import os
import numpy as np
import scipy.sparse as sp

from h5features2.Items import Items
from h5features2.Features import Features

def write(filename, group_name, items_data, times_data, features_data,
          features_format='dense', chunk_size=0.1, sparsity=0.1):
    """Write in a h5features file.

    Parameters
    ----------

    filename : str -- HDF5 file to be writted, potentially serving as
        a container for many small files. If the file does not exist,
        it is created. If the file is already a valid HDF5 file, try
        to append the data in it.

    group_name : str -- h5 group to write the data in, or to append
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

    features_format : str, optional -- Which format to store the
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
    # File format version
    # TODO Get it from setup.py ?
    version = '1.0'

    items = Items(items_data)
    features = Features(features_data)

    # Prepare parameters, look for errors and raise if any.
    _check_file(filename)
    _check_chunk_size(chunk_size)
    time_format = _check_times(times)

    # Open target file for writing.
    with h5py.File(filename, mode='a') as h5file:
        # If group does not exists, create it
        if not group_name in h5file:
            # TODO if something fails here, the file will be polluted,
            # should we catch and del new datasets?

            group = h5file.create_group(group_name)
            group.attrs['version'] = version

            nb_in_chucks = init_features(group, features_format, features_type,
                                         features_dim, chunk_size, sparsity)
            init_times(group, nb_in_chucks, time_format)
            init_file_index(group, chunk_size)

            # typical filename is 20 characters i.e. around 20 bytes
            nb_lines_by_chunk = max(10, nb_lines(20, 1, chunk_size * 1000))
            items.create(group, nb_lines_by_chunk)

        else: # The group exists
            group = h5file[group_name]

            # raise if we cannot append data to it.
            _appendable(group, features_format, features_dim,
                        features_type, version, time_format)

        # in case we append to the end of a file (this eventually
        # modifies 'files').
        continue_last_item = items.continue_last_item(group)

        # build the files index before reshaping features
        file_index = _files_index(group, features, items.group_name)

        # writing data
        items.write(group)
        _write_features(group, features, features_format)
        _write_times(group, times, time_format)
        _write_files_index(group, file_index, continue_last_item)


def simple_write(filename, group, times, features, fileid='features'):
    """Simplified version of write when there is only one file
    """
    write(filename, group, [fileid], [times], [features])


def _check_file(filename):
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


def _check_chunk_size(chunk_size):
    """Raise IOError if the size of a chunk (in Mo) is below 8 Ko."""
    if chunk_size < 0.008:
        raise IOError('chunk size below 8 Ko are not allowed as they'
                      ' result in poor performances.')


def _check_times(times):
    """Retrieve time format and raise on errors.

    Raise IOError if the time format is not 1 or 2, or if times arrays
    have different dimensions.

    """
    # TODO check that the times are increasing for each file
    time_format = times[0].ndim

    if time_format > 2:
        raise IOError('times must be a list of 1D or 2D numpy arrays.')

    if not all([t.ndim == time_format for t in times]):
        raise IOError('all times arrays must have the same dimension.')

    return time_format


def _appendable(group, h5format, h5dim, h5type,
                version, time_format):
    """Raise IOError if the data is not appendable in the group."""
    if not is_same_version(group, version):
        raise IOError('Files have incompatible version of h5features')

    if not is_same_features_format(group, h5format):
        raise IOError('Files must have the same features format.')

    if not is_same_times_format(group, time_format):
        raise IOError('Files must have the same time format')

    if not is_same_datasets(group, h5format):
        raise IOError('group {} is not a valid h5features file:'
                      ' missing dataset'.format(group.name[1:]))

    if not is_same_features_type(group, h5type):
        raise IOError('Files must have the same data type')

    if not is_same_features_dim(group, h5dim, h5format):
        raise IOError('mismatch between provided features dimension and already'
                      ' stored feature dimension.')


def is_same_version(group, version):
    """Return True if local version and group version are the same."""
    return group.attrs['version'] == version


def is_same_times_format(group, times_format):
    return group['times'][...].ndim == times_format


def is_same_datasets(group, features_format):
    # The datasets that will be writted on the HDF5 file
    datasets = ['items', 'times', 'features', 'file_index']
    if features_format == 'sparse':
        datasets += ['frames', 'coordinates']

    return all([d in group for d in datasets])


def init_file_index(group, chunk_size):
    """Initializes the file index subgroup."""
    nb_lines_by_chunk = max(10, nb_lines(
        np.dtype(np.int64).itemsize, 1, chunk_size * 1000))
    group.create_dataset('file_index', (0,), dtype=np.int64,
                         chunks=(nb_lines_by_chunk,), maxshape=(None,))


def init_times(group, nb_in_chucks, times_format):
    """Initilizes the times subgroup."""
    # TODO smarter
    if times_format == 1:
        group.create_dataset('times', (0,), dtype=np.float64,
                             chunks=(nb_in_chucks,), maxshape=(None,))
    else:  # times_format == 2
        group.create_dataset('times', (0,2), dtype=np.float64,
                             chunks=(nb_in_chuks,2), maxshape=(None,2))


def nb_lines(item_size, n_columns, size_in_mem):
    """Item_size given in bytes, size_in_mem given in kilobytes."""
    return int(round(size_in_mem * 1000. / (item_size * n_columns)))


def _files_index(group, features, items_group_name):
    """"""
    group_nb_files = group[items_group_name].shape[0]
    if group_nb_files > 0:
        last_file_index = group['file_index'][-1]
    else:
        # indexing from 0
        last_file_index = -1

    files_index = np.cumsum([x.shape[0] for x in features])
    return last_file_index + files_index


def _write_features(group, features, features_format):
    """Write features data to the group.

    Raise NotImplementedError if features_format == 'sparse'

    """
    if features_format == 'sparse':
        raise NotImplementedError('writing sparse features not implemented')
        # 1- concatenation
        # put them in right format if they aren't already
        # FIXME: implement this
        # are_sparse = [x.isspmatrix_coo() for x in features]
        # if not(all(are_sparse)):
        #    for x in features:
        #        if not(x.isspmatrix_coo()):
        #            x = sp.coo_matrix(x)
        # need to get the coo by line ...

        # 2- writing
        #nb, = g['features'].shape
        # g['feature'].resize((nb+features.shape[0],))
        #g['features'][nb:] = features
        # g['coordinates'].resize((nb+features.shape[0],2))
        #g['coordinates'][nb:,:] = coordinates
        #nb, = g['frames'].shape
        # g['frames'].resize((nb+frames.shape[0],))
        #g['frames'][nb:] = frames
    else:
        features = [x.todense() if sp.issparse(x) else x for x in features]
        features = np.concatenate(features, axis=0)

        nb, d = group['features'].shape
        group['features'].resize((nb + features.shape[0], d))
        group['features'][nb:, :] = features

def _write_times(group, times, times_format):
    """Write times data to the group"""
    if times_format == 1:
        times = np.concatenate(times)
        nb, = group['times'].shape
        group['times'].resize((nb + times.shape[0],))
        group['times'][nb:] = times
    else:
        assert times_format == 2
        nb, _ = group['times'].shape
        group['times'].resize((nb + times.shape[0],2))
        group['times'][nb:] = times


def _write_files_index(group, file_index, continue_last_file):
    """Write the files index to the group"""
    nb, = group['file_index'].shape
    if continue_last_file:
        nb = nb - 1
    group['file_index'].resize((nb + file_index.shape[0],))
    group['file_index'][nb:] = file_index
