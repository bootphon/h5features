"""Provides the write() function to h5features files."""

import h5py
import os
import numpy as np
import scipy.sparse as sp


def write(filename, group, files, times, features,
          features_format='dense', chunk_size=0.1, sparsity=0.1):
    """Write in a h5features file.

    Parameters
    ----------

    filename : str -- HDF5 file to be writted, potentially serving as
        a container for many small files. If the file does not exist,
        it is created. If the file is already a valid HDF5 file, try
        to append the data in it.

    group : str -- h5 group to write the data in, or to append the
        data to if the group already exists in the file.

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

    """

    # Step 1:
    # preparing parameters, check for and raise if error.

    # file format version number TODO Get it from setup.py
    version = '1.0'

    features_dim, features_type, time_format = _write_check_arguments(
        filename, group, features_format, chunk_size, features, files, times)

    # The datasets that will be writted on the HDF5 file
    datasets = ['files', 'times', 'features', 'file_index']
    if features_format == 'sparse':
        datasets += ['frames', 'coordinates']

    # Step 2:
    # preparing target file.  Choose if data will be appended
    # to an existing group or stored in a new one

    h5file = h5py.File(filename)

    if _write_need_to_append(
            h5file, group, datasets,
            features_format, features_dim, features_type,
            version, time_format):

        g = h5file.get(group)

    else:
        g = _write_init_datasets(
            h5file, group, datasets,
            features_format, features_dim, features_type,
            chunk_size, version)

    # Step 3:
    # preparing data for writing

    nb_existing_files = g['files'].shape[0]
    continue_last_file = False
    if nb_existing_files > 0:
        existing_files = g['files'][...]
        inter = list(set(existing_files).intersection(files))
        if inter:
            assert (
                inter == [files[0]] and files[0] == existing_files[-1]), (
                    "Data can be added only at the end of the last written"
                    " file")
            continue_last_file = True
            files = files[1:]

    file_index = [x.shape[0] for x in features]
    file_index = np.cumsum(file_index)

    if nb_existing_files > 0:
        last_file_index = g['file_index'][-1]
    else:
        last_file_index = -1  # indexing from 0
    file_index = last_file_index + file_index

    if features_format == 'sparse':
        raise IOError('writing sparse features not yet implemented')
        # put them in right format if they aren't already
        # FIXME: implement this
        #are_sparse = [x.isspmatrix_coo() for x in features]
        # if not(all(are_sparse)):
        #    for x in features:
        #        if not(x.isspmatrix_coo()):
        #            x = sp.coo_matrix(x)
        # need to get the coo by line ...
    else:
        features = [x.todense() if sp.issparse(x) else x for x in features]
        features = np.concatenate(features, axis=0)
    times = np.concatenate(times)

    # Step 4: writing data
    if features_format == 'sparse':
        raise IOError('writing sparse features not yet implemented')
        #nb, = g['features'].shape
        # g['feature'].resize((nb+features.shape[0],))
        #g['features'][nb:] = features
        # g['coordinates'].resize((nb+features.shape[0],2))
        #g['coordinates'][nb:,:] = coordinates
        #nb, = g['frames'].shape
        # g['frames'].resize((nb+frames.shape[0],))
        #g['frames'][nb:] = frames
    else:
        nb, d = g['features'].shape
        g['features'].resize((nb + features.shape[0], d))
        g['features'][nb:, :] = features

    # write times dataset
    if time_format == 1:
        nb, = g['times'].shape
        g['times'].resize((nb + times.shape[0],))
        g['times'][nb:] = times
    else:
        assert time_format == 2
        nb,_ = g['times'].shape
        g['times'].resize((nb + times.shape[0],2))
        g['times'][nb:] = times

    if files:
        nb, = g['files'].shape
        g['files'].resize((nb + len(files),))
        g['files'][nb:] = files

    nb, = g['file_index'].shape
    if continue_last_file:
        nb = nb - 1
    g['file_index'].resize((nb + file_index.shape[0],))
    g['file_index'][nb:] = file_index

    h5file.close()


def simple_write(filename, group, times, features):
    """simplified version of write when there is only one file
    """
    # use a default name for the file
    write(filename, group, ['features'], [times], [features])

def _write_check_arguments(
        filename, group, features_format, chunk_size, features, files, times):
    """Consistency checks of write() arguments.

    This method is called by write(). It checks that filename can be
    openned for writting. Also checks for consistency errors in the input
    arguments, as documented in write.__doc__.

    Raise:

        IOError if the file os not valid for writting HDF5 data.
        IOError if badly formatted arguments.

    Return:

        dim: int -- Dimension of the feature vectors.
        features_type -- Type of the feature scalars.

    """

    # Raise if the file don't exists and is not writable.
    # TODO simplify, no need to create/delete the file.
    if not os.path.isfile(filename):
        try:
            f = open(filename, 'w')
            f.close()
            os.remove(filename)
        except OSError, error:
            raise IOError(error)

    # Raise IOError if file exists and is not HDF5
    if os.path.isfile(filename) and not h5py.is_hdf5(filename):
        raise IOError('{} is not an HDF5 file.'.format(filename))

    if not features_format in  ['dense', 'sparse']:
        raise IOError(
            "{} is a bad features_format, please choose 'dense' or 'sparse'"
            .format(features_format))

    if not chunk_size >= 0.008:
        raise IOError('chunk_size below 8Ko are not allowed as they'
                      ' would result in poor performances')

    nb_frames = [x.shape[0] for x in features]
    if not all([n > 0 for n in nb_frames]):
        raise IOError('all files must be non-empty')

    # retrieve features dimension
    dims = [x.shape[1] for x in features]
    features_dim = dims[0]

    if not features_dim > 0:
        raise IOError("features dimension must be strictly positive")

    if not all([d == features_dim for d in dims]):
        raise IOError("all files must have the same feature dimension")

    # retrieve features type
    types = [x.dtype for x in features]
    features_type = types[0]

    if not all([t == features_type for t in types]):
        raise IOError("all files must have the same feature type")

    if not len(set(files)) == len(files):
        raise IOError("all files must have different names")

    # retrieve time format
    # TODO check that the times are increasing for each file
    time_format = times[0].ndim

    if time_format > 2:
        raise IOError('times must be a list of 1D or 2D numpy arrays')

    if not all([t.ndim == time_format for t in times]):
        raise IOError('all times arrays must have the same dimension')

    return features_dim, features_type, time_format


def _write_need_to_append(h5file, group, datasets, h5format, h5dim,
                          h5type, version, time_format):
    """Return True if the data can be appended in the given group of the file.

    This internal method is called by write().

    Raise:

    Raise IOError if the data is not appendable in the file because of
    some format error.

    Return:

    True if the data can be appended in the given group of the HDF5
    file, False else.

    """

    if not group in h5file:
        return False

    g = h5file.get(group)

    if not g.attrs['version'] == version:
        raise IOError('Files have incompatible version of h5features')

    if not g.attrs['format'] == h5format:
        raise IOError('Files must have the same features format.')

    for dataset in datasets:
        if not dataset in g:
            raise IOError('group {} of file {} is not a valid h5features file:'
                          ' missing dataset {}'
                          .format(group, h5file.filename, dataset))

    if not g['features'].dtype == h5type:
        raise IOError('Files must have the same data type')

    f_dim = g.attrs['dim'] if h5format == 'sparse' else g['features'].shape[1]
    if not f_dim == h5dim:
        raise IOError('mismatch between provided features dimension and already'
                      ' stored feature dimension.')

    print time_format
    print
    print g['times'][...].ndim

    if not time_format == g['times'][...].ndim:
        raise IOError('Files must have the same time format')

    return True

# FIXME if something fails here, the file will be polluted, should
# we catch and del new datasets?
def _write_init_datasets(h5file, group, datasets,
                         features_format, features_dim, features_type,
                         chunk_size, version):
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
    str_dtype = h5py.special_dtype(vlen=unicode)

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


def _write_init_sparse_datasets(
        g, features_type, features_dim, sparsity, chunk_size):
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
