"""Provides the read() function from h5features files."""

import h5py
import os
import numpy as np
import scipy.sparse as sp


def read(filename, group=None,
         from_internal_file=None, to_internal_file=None,
         from_time=None, to_time=None,
         index=None):
    """Reads in a h5features file.

    Parameters
    ----------

    filename : filename
        hdf5 file potentially serving as a container for many small files

    group : str
        h5 group to read the data from

    from_internal_file : str, optional
        Read the data starting from this file. (defaults to the first stored
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

    .. note:: Note that all the files that are present on disk between
        file1 and file2 will be loaded and returned. It's the
        responsibility of the user to make sure that it will fit into
        RAM memory.

    .. note:: Also note that the functions are not concurrent nor
        thread-safe (because the HDF5 library is not concurrent and
        not always thread-safe), moreover, they aren't even atomic for
        independent process (because there are several independent
        calls to the file system), so that thread-safety and atomicity
        of operations should be enforced externally when necessary.

    """
    # Step 1: parse arguments and find read coordinates from metadata

    # If no index provided, build it
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
        # the second 'index' here refers to the list.index() method
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


def read_index(filename, group=None):
    """

    Parameters:

    filename : str
        HDF5 file to read index from

    group : str, optional
        h5 group in the HDF5 file to read the index from

    """
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
            index['dim'] = g.attrs['dim']  # FIXME: type ?
            index['frames'] = g['lines'][...]  # FIXME: type ?
    return index
