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
"""The legacy version of h5features.

For compatibility tests only."""

import h5py
import os
import numpy as np
import scipy.sparse as sp


def read_index(filename, group=None):
    with h5py.File(filename, 'r') as f:
        if group is None:
            groups = [g for g in f]
            assert len(groups) <= 1, ("There are several groups in file %s, "
                                      "you should specify which one should be "
                                      "read" % filename)
            assert len(groups) > 0, ("There are no group in file %s, "
                                     "impossible to read" % filename)
            group = groups[0]
        g = f[group]
        legacy = False
        try:
            version = g.attrs['version']
        except KeyError:
            legacy = True
        if legacy:
            index = legacy_read_index(filename, group)
        else:
            assert version == "1.0", "unsupported version %s" % version
            files = list(g['files'][...])
            index = {'files': files, 'file_index': g['file_index'][...],
                     'times': g['times'][...], 'format': g.attrs['format']}
            # file_index contains the index of the end of each file
            if index['format'] == 'sparse':
                index['dim'] = g.attrs['dim']
                index['frames'] = g['frames'][...]
        index['group'] = group
        index['legacy'] = legacy
        return index


def read(filename, group=None, from_internal_file=None, to_internal_file=None,
         from_time=None, to_time=None, index=None):
    """function read

    Reads in a h5features file.

    Parameters
    ----------
    filename : filename
        hdf5 file potentially serving as a container for many small files
    group : str
        h5 group to read the data from
    from_internal_file : str, optional
        Read the data strating from this file. (defaults to the first stored
        file)
    to_internal_file : str, optional
        Read the data until reaching the file. (defaults to from_internal_file
        if it was specified and to the last stored file otherwise)
    from_time : float, optional
        (defaults to the beginning time in from_internal_file)
        the specified times are included in the output
    to_time : float, optional
        (defaults to the ending time in to_internal_file)
        the specified times are included in the output
    index : int, optional
        (for faster access)

    Returns
    -------
    times : dict
        a dictionary of 1D arrays
    features : dict
        a dictionary of 2D arrays with the 'feature' dimension along the
        columns and the 'time' dimension along the lines

    .. note:: Note that all the files that are present on disk between file1
        and file2 will be loaded and returned. It's the responsibility
        of the user to make sure that it will fit into RAM memory.

    .. note:: Also note that the functions are not concurrent nor thread-safe
        (because the HDF5 library is not concurrent and not always
        thread-safe), moreover, they aren't even atomic for independent
        process (because there are several independent calls to the file
        system), so that thread-safety and atomicity of operations should be
        enforced externally when necessary.
    """
    # Step 1: parse arguments and find read coordinates from metadata
    if index is None:
        index = read_index(filename, group)
    if group is None:
        group = index['group']
    if to_internal_file is None:
        if from_internal_file is None:
            to_internal_file = index['files'][-1]
        else:
            to_internal_file = from_internal_file
    if from_internal_file is None:
        from_internal_file = index['files'][0]
    try:
        # the second 'index' in this expression refers to the 'index' method of
        # class list
        f1 = index['files'].index(from_internal_file)
    except ValueError:
        raise Exception('No entry for file %s in %s\\%s' %
                        (from_internal_file, filename, group))
    try:
        f2 = index['files'].index(to_internal_file)
    except ValueError:
        raise Exception('No entry for file %s in %s\\%s' %
                        (to_internal_file, filename, group))
    assert f2 >= f1, ("Internal file %s is located after internal file %s in "
                      "the h5features file %s" %
                      (from_internal_file, to_internal_file, filename))
    # index associated with the beginning of from_internal_file :
    f1_start = 0 if f1 == 0 else index['file_index'][f1 - 1] + 1
    f1_end = index['file_index'][f1]
    f2_start = 0 if f2 == 0 else index['file_index'][f2 - 1] + 1
    # index associated with the end of to_internal_file :
    f2_end = index['file_index'][f2]
    if from_time is None:
        i1 = f1_start
    else:
        times = index['times'][f1_start:f1_end + 1]  # the end is included...
        try:
            # smallest time larger or equal to from_time
            i1 = f1_start + np.where(times >= from_time)[0][0]
        except IndexError:
            raise Exception('from_time %f is larger than the biggest time in '
                            'from_internal_file %s' %
                            (from_time, from_internal_file))
    if to_time is None:
        i2 = f2_end
    else:
        times = index['times'][f2_start:f2_end + 1]  # the end is included...
        try:
            # largest time smaller or equal to to_time
            i2 = f2_start + np.where(times <= to_time)[0][-1]
        except IndexError:
            raise Exception('to_time %f is smaller than the smallest time in '
                            'to_internal_file %s' %
                            (to_time, to_internal_file))
    # Step 2: access actual data
    with h5py.File(filename, 'r') as f:
        g = f[group]
        if index['format'] == 'dense':
            if index['legacy']:
                features = g['features'][:, i1:i2 + 1].T  # i2 included
            else:
                features = g['features'][i1:i2 + 1, :]  # i2 included
            times = g['times'][i1:i2 + 1]
        else:
            # FIXME implement this
            raise IOError('reading sparse features not yet implemented')
            # will be different for version 1.0 and legacy code ...
    if f2 > f1:
        file_ends = index['file_index'][f1:f2] - f1_start
        # FIXME change axis from 1 to 0, but need to check that this doesn't
        # break compatibility with matlab generated files
        features = np.split(features, file_ends + 1, axis=0)
        times = np.split(times, file_ends + 1)
    else:
        features = [features]
        times = [times]
    files = index['files'][f1:f2 + 1]
    features = dict(zip(files, features))
    times = dict(zip(files, times))
    return times, features


# FIXME could check that the times are increasing for each file
def write(filename, group, files, times, features, features_format='dense',
          chunk_size=0.1, sparsity=0.1):
    """function write

    Write in a h5features file.

    Parameters
    ----------
    filename : filename
        hdf5 file potentially serving as a container for many small files
    group : str
        h5 group to write the data in
    files : list of str
        List of files from which the features where extracted
    times : list of 1D numpy array like
        Time value for the features array (e.g. the center of the time window)
    features : list of 2D numpy array like
        features should have time along the lines and features along the
        columns (accomodating row-major storage in hdf5 files)
    features_format : str, optional
        Which format to store the features into (sparse or dense)
    chunk_size : float, optional
        In Mo, tuning parameter corresponding to the size of a chunk in
        the h5file, ignored if the file already exists
    sparsity : float, optional
        tuning parameter corresponding to the expected proportion of
        non-zeros elements on average in a single frame
    """
    version = "1.0"  # version number for the file format
    # Step 1: check arguments
    assert features_format in ['dense', 'sparse']
    assert chunk_size >= 0.008, ('chunk_size below 8Ko are not allowed as they'
                                 ' would result in poor performances')
    nb_frames = [x.shape[0] for x in features]
    assert all([n > 0 for n in nb_frames]), "all files must be non-empty"
    dims = [x.shape[1] for x in features]
    dim = dims[0]
    assert dim > 0, "features dimension must be strictly positive"
    assert all([d == dim for d in dims]), ("all files must have the same "
                                           "feature dimension")
    types = [x.dtype for x in features]
    features_type = types[0]
    assert all([t == features_type for t in types]), ("all files must have the"
                                                      " same feature type")
    assert len(set(files)) == len(files), "all files must have different names"
    datasets = ['files', 'times', 'features', 'file_index']
    if features_format == 'sparse':
        datasets.append('frames')
        datasets.append('coordinates')
    # Step 2: preparing target file
    append = False
    if os.path.isfile(filename):
        with h5py.File(filename, 'w') as fh:
            if group in fh:
                append = True
    with h5py.File(filename, 'w') as fh:
        if append:  # check existing h5 file
            g = fh[group]  # raise KeyError if group not in file
            assert g.attrs['version'] == version, (
                "File was written with incompatible version of h5features")
            assert g.attrs['format'] == features_format
            for dataset in datasets:
                assert dataset in g, (
                    "group %s of file %s is not a valid h5features file: "
                    "missing dataset %s" % (group, filename, dataset))
            assert g['features'].dtype == features_type
            if features_format == 'sparse':
                f_dim = g.attrs['dim']
            else:
                f_dim = g['features'].shape[1]
            assert f_dim == dim, (
                "mismatch between provided features dimension and already "
                "stored feature dimension")
        else:  # create h5 file
            # FIXME if something fails here, the file will be polluted, should
            # we catch and del new datasets?
            g = fh.create_group(group)
            g.attrs['version'] = version
            if features_format == 'sparse':
                nb_lines_by_chunk = max(
                    10, nb_lines(features_type.itemsize, 1, chunk_size * 1000))
                g.create_dataset(
                    'coordinates', (0, 2), dtype=np.float64,
                    chunks=(nb_lines_by_chunk, 2), maxshape=(None, 2))
                g.create_dataset(
                    'features', (0,), dtype=features_type, chunks=(
                    nb_lines_by_chunk,), maxshape=(None,))
                # guessed from value of sparsity, used to determine time
                # chunking
                nb_frames_by_chunk = max(10, nb_lines(
                    features_type.itemsize, int(round(sparsity * dim)),
                    chunk_size * 1000))
                nb_lines_by_chunk = max(
                    10, nb_lines(np.dtype(np.int64).itemsize, 1,
                                 chunk_size * 1000))
                g.create_dataset(
                    'frames', (0,), dtype=np.int64, chuns=(nb_lines_by_chunk,),
                    maxshape=(None,))
                g.attrs['dim'] = dim
            else:
                nb_frames_by_chunk = max(
                    10, nb_lines(features_type.itemsize, dim,
                                 chunk_size * 1000))
                g.create_dataset(
                    'features', (0, dim), dtype=features_type, chunks=(
                        nb_frames_by_chunk, dim), maxshape=(None, dim))
            g.create_dataset('times', (0,), dtype=np.float64, chunks=(
                nb_frames_by_chunk,), maxshape=(None,))
            str_dtype = h5py.special_dtype(vlen=str)
            # typical filename is 20 characters i.e. around 20 bytes
            nb_lines_by_chunk = max(10, nb_lines(20, 1, chunk_size * 1000))
            g.create_dataset(
                'files', (0,), dtype=str_dtype, chunks=(nb_lines_by_chunk,),
                maxshape=(None,))
            nb_lines_by_chunk = max(
                10, nb_lines(np.dtype(np.int64).itemsize, 1,
                             chunk_size * 1000))
            g.create_dataset('file_index', (0,), dtype=np.int64, chunks=(
                nb_lines_by_chunk,), maxshape=(None,))
            g.attrs['format'] = features_format
        # Step 3: preparing data for writing
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
            # FIXME implement this
            # are_sparse = [x.isspmatrix_coo() for x in features]
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
            # nb, = g['features'].shape
            # g['feature'].resize((nb+features.shape[0],))
            # g['features'][nb:] = features
            # g['coordinates'].resize((nb+features.shape[0],2))
            # g['coordinates'][nb:,:] = coordinates
            # nb, = g['frames'].shape
            # g['frames'].resize((nb+frames.shape[0],))
            # g['frames'][nb:] = frames
        else:
            nb, d = g['features'].shape
            g['features'].resize((nb + features.shape[0], d))
            g['features'][nb:, :] = features
        nb, = g['times'].shape
        g['times'].resize((nb + times.shape[0],))
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


def simple_write(filename, group, times, features):
    """simplified version of write when there is only one file
    """
    # use a default name for the file
    write(filename, group, ['features'], [times], [features])


def nb_lines(item_size, n_columns, size_in_mem):
    """
    Auxiliary function
    """
    # item_size given in bytes, size_in_mem given in kilobytes
    return int(round(size_in_mem * 1000. / (item_size * n_columns)))


def legacy_read_index(filename, group=None):
    """
    legacy code for supporting reading feature written from matlab bindings
    """
    with h5py.File(filename, 'r') as f:
        if group is None:
            groups = [g for g in f]
            assert len(
                groups) <= 1, (
                    "There are several groups in file %s, you should specify "
                    "which one should be read" % filename)
            assert len(
                groups) > 0, (
                    "There are no group in file %s, impossible to read"
                    % filename)
            group = groups[0]
        g = f[group]
        files = ''.join([unichr(int(c)) for c in g['files'][...]]).replace(
            '/-', '/').split('/\\')  # parse unicode to strings
        # file_index contains the index of the end of each file:
        index = {'files': files, 'file_index': np.int64(g['file_index'][...]),
                 'times': g['times'][...], 'format': g.attrs['format']}
        if index['format'] == 'sparse':
            index['dim'] = g.attrs['dim']  # FIXME type ?
            index['frames'] = g['lines'][...]  # FIXME type ?
    return index
