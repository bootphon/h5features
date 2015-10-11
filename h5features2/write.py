"""Provides a write function for h5features files."""

import h5py
import os
import numpy as np
import scipy.sparse as sp


def write(filename, group_name, files, times, features,
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

    files : list of str -- List of files from which the features where
        extracted.

    times : list of 1D or 2D numpy array like -- Time value for the
        features array. Elements of a 1D array are considered as the
        center of the time window associated with the features. A 2D
        array must have 2 columns corresponding to the begin and end
        timestamps of the features time window.

    features : list of 2D numpy array like -- Features should have
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

    IOError if filename is not valid or if parameters are not consistents.

    NotImplementedError if features_format == 'sparse'

    """
    # File format version
    # TODO Get it from setup.py ?
    version = '1.0'

    if features_format == 'sparse':
        raise NotImplementedError('Writing sparse features is not implemented.')

    # Prepare parameters, look for errors and raise if any.
    _check_file(filename)
    _check_chunk_size(chunk_size)
    _check_features_format(features_format)
    _check_files(files)
    time_format = _check_times(times)
    features_dim, features_type = _check_features(features)

    # Open target file for writing.
    with h5py.File(filename, mode='a') as h5file:
        group = init_subgroups(h5file, group_name, features_format,
                               features_dim, features_type,
                               time_format, chunk_size, version,
                               sparsity)

        # in case we append to the end of a file (this eventually
        # modifies 'files').
        files, continue_last_file = _files_continue_last_file(group, files)

        # build the files index before reshaping features
        file_index = _files_index(group, features)

        # writing data
        _write_features(group, features, features_format)
        _write_times(group, times, time_format)
        _write_files(group, files)
        _write_files_index(group, file_index, continue_last_file)


def simple_write(filename, group, times, features, fileid='features'):
    """Simplified version of write when there is only one file
    """
    write(filename, group, [fileid], [times], [features])


def _check_features(features):
    """Raise IOError if features are not in a correct state.

    Raise:

    Raise IOError if one of the feature is empty, if features have not
    all the same positive dimension, or if all features have not the
    same data type.

    Return:

    features_dim : int -- Dimension of the features
    features_type : type -- Data type of features scalars

    """
    nb_frames = [x.shape[0] for x in features]
    if not all([n > 0 for n in nb_frames]):
        raise IOError('all features must be non-empty')

    # retrieve features dimension
    dims = [x.shape[1] for x in features]
    features_dim = dims[0]

    if not features_dim > 0:
        raise IOError('features dimension must be strictly positive.')

    if not all([d == features_dim for d in dims]):
        raise IOError('all files must have the same feature dimension.')

    # retrieve features type
    types = [x.dtype for x in features]
    features_type = types[0]

    if not all([t == features_type for t in types]):
        raise IOError('all files must have the same feature type.')

    return features_dim, features_type


def _check_files(files):
    """Raise if file names are not unique."""
    if not len(set(files)) == len(files):
        raise IOError('all files must have different names.')


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


def _check_features_format(features_format):
    """Raise IOError if the features format is not 'dense' or 'sparse'"""
    if not features_format in  ['dense', 'sparse']:
        raise IOError(
            "{} is a bad features format, please choose 'dense' or 'sparse'"
            .format(features_format))


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


def init_subgroups(h5file, group_name, features_format, features_dim,
                   features_type, time_format, chunk_size, version, sparsity):
    """"""
    # The datasets that will be writted on the HDF5 file
    datasets = ['files', 'times', 'features', 'file_index']

    if features_format == 'sparse':
        datasets += ['frames', 'coordinates']

    # Choose if data will be appended to an existing group or stored
    # in a new one
    is_append = _need_to_append(h5file, group_name, datasets,
                                features_format, features_dim,
                                features_type, version,
                                time_format)
    if is_append:
        return h5file.get(group_name)
    else:
        return _write_init_datasets(h5file, group_name,
                                    features_format, features_dim,
                                    features_type, chunk_size,
                                    version, sparsity)


def _need_to_append(h5file, group_name, datasets, h5format, h5dim, h5type,
                    version, time_format):
    """Return True if the data can be appended in the given group of the file.

    This internal method is called by write().

    Raise:

    Raise IOError if the data is not appendable in the file because of
    some format error.

    Return:

    True if the data can be appended in the given group of the HDF5
    file, False else.

    """
    if not group_name in h5file:
        return False

    group = h5file.get(group_name)

    if not group.attrs['version'] == version:
        raise IOError('Files have incompatible version of h5features')

    if not group.attrs['format'] == h5format:
        raise IOError('Files must have the same features format.')

    for dataset in datasets:
        if not dataset in group:
            raise IOError('group {} of file {} is not a valid h5features file:'
                          ' missing dataset {}'
                          .format(group_name, h5file.filename, dataset))

    if not group['features'].dtype == h5type:
        raise IOError('Files must have the same data type')

    f_dim = (group.attrs['dim'] if h5format == 'sparse'
             else group['features'].shape[1])

    if not f_dim == h5dim:
        raise IOError('mismatch between provided features dimension and already'
                      ' stored feature dimension.')

    if not time_format == group['times'][...].ndim:
        raise IOError('Files must have the same time format')

    return True


# FIXME if something fails here, the file will be polluted, should
# we catch and del new datasets?
# TODO Why don't use datasets variable ?
def _write_init_datasets(h5file, group, features_format, features_dim,
                         features_type, chunk_size, version, sparsity):
    """Initializes HDF5 file datasets according to parameters."""

    g = h5file.create_group(group)
    g.attrs['version'] = version
    g.attrs['format'] = features_format

    # init specific datasets for 'dense' and 'sparse' cases.
    if features_format == 'sparse':
        nb_frames_by_chunk = _write_init_sparse_datasets(
            g, features_type, features_dim, sparsity, chunk_size)

    else:
        nb_frames_by_chunk = _write_init_dense_datasets(
            g, features_type, features_dim, chunk_size)

    g.create_dataset('times',
                     (0,),
                     dtype=np.float64,
                     chunks=(nb_frames_by_chunk,),
                     maxshape=(None,))

    # typical filename is 20 characters i.e. around 20 bytes
    nb_lines_by_chunk = max(10, nb_lines(20, 1, chunk_size * 1000))
    str_dtype = h5py.special_dtype(vlen=str)

    g.create_dataset('files',
                     (0,),
                     dtype=str_dtype,
                     chunks=(nb_lines_by_chunk,),
                     maxshape=(None,))

    nb_lines_by_chunk = max(10, nb_lines(
        np.dtype(np.int64).itemsize, 1, chunk_size * 1000))

    g.create_dataset('file_index',
                     (0,),
                     dtype=np.int64,
                     chunks=(nb_lines_by_chunk,),
                     maxshape=(None,))

    return g


def _write_init_sparse_datasets(g, features_type, features_dim, sparsity, chunk_size):
    """Initializes sparse specific datasets."""

    nb_lines_by_chunk = max(
        10, nb_lines(features_type.itemsize, 1, chunk_size * 1000))

    g.create_dataset('coordinates',
                     (0, 2),
                     dtype=np.float64,
                     chunks=(nb_lines_by_chunk, 2),
                     maxshape=(None, 2))

    g.create_dataset('features',
                     (0,),
                     dtype=features_type,
                     chunks=(nb_lines_by_chunk,),
                     maxshape=(None,))

    # guessed from sparsity, used to determine time chunking
    nb_frames_by_chunk = max(10, nb_lines(
        features_type.itemsize, int(round(sparsity * features_dim)),
        chunk_size * 1000))

    nb_lines_by_chunk = max(
        10, nb_lines(np.dtype(np.int64).itemsize, 1,
                     chunk_size * 1000))

    g.create_dataset('frames',
                     (0,),
                     dtype=np.int64,
                     chuns=(nb_lines_by_chunk,),
                     maxshape=(None,))

    g.attrs['dim'] = features_dim

    return nb_frames_by_chunk


def _write_init_dense_datasets(
        g, features_type, features_dim, chunk_size):
    """Initializes dense specific datasets."""

    nb_frames_by_chunk = max(
        10, nb_lines(features_type.itemsize, features_dim,
                     chunk_size * 1000))

    g.create_dataset('features',
                     (0, features_dim),
                     dtype=features_type,
                     chunks=(nb_frames_by_chunk, features_dim),
                     maxshape=(None, features_dim))

    return nb_frames_by_chunk

def nb_lines(item_size, n_columns, size_in_mem):
    """
    Auxiliary function
    """
    # item_size given in bytes, size_in_mem given in kilobytes
    return int(round(size_in_mem * 1000. / (item_size * n_columns)))


def _files_continue_last_file(group, files):
    """"""
    continue_last_file = False

    group_nb_files = group['files'].shape[0]
    if group_nb_files > 0:
        group_files = group['files'][...]
        inter = list(set(group_files).intersection(files))
        if inter:
            if not (inter == [files[0]] and files[0] == group_files[-1]):
                raise IOError('Data can be added only at the end'
                              'of the last written file')

            continue_last_file = True
            files = files[1:]

    return files, continue_last_file


def _files_index(group, features):
    """"""
    group_nb_files = group['files'].shape[0]
    if group_nb_files > 0:
        last_file_index = group['file_index'][-1]
    else:
        # indexing from 0
        last_file_index = -1

    files_index = np.cumsum([x.shape[0] for x in features])
    return last_file_index + files_index

def _write_features(group, features, features_format):
    """Write features to an HDF5 group.

    Raise:

    NotImplementedError if features_format == 'sparse'
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

def _write_times(g, times, times_format):
    """"""
    if times_format == 1:
        times = np.concatenate(times)
        nb, = g['times'].shape
        g['times'].resize((nb + times.shape[0],))
        g['times'][nb:] = times
    else:
        assert times_format == 2
        nb, _ = g['times'].shape
        g['times'].resize((nb + times.shape[0],2))
        g['times'][nb:] = times
def _write_files(g, files):
    """"""

    if files:
        nb, = g['files'].shape
        g['files'].resize((nb + len(files),))
        g['files'][nb:] = files

def _write_files_index(g, file_index, continue_last_file):
    """"""
    nb, = g['file_index'].shape
    if continue_last_file:
        nb = nb - 1
    g['file_index'].resize((nb + file_index.shape[0],))
    g['file_index'][nb:] = file_index
