"""Provides the read() function from h5features files."""

import h5py
import os
import numpy as np
import scipy.sparse as sp


def fetch_index(group, element):
    """Look for the given element in the given group (a list)."""
    try:
        return group.index(element)
    except ValueError:
        raise IOError('No entry for item {} in {}'.format(element, group))


def read(filename, groupname=None, from_item=None, to_item=None,
         from_time=None, to_time=None, index=None):
    """Reads in a h5features file.

    Parameters
    ----------

    filename : filename
        hdf5 file potentially serving as a container for many small files

    groupname : str
        h5 group to read the data from

    from_item : str, optional
        Read the data starting from this item. (defaults to the first stored
        item)

    to_item : str, optional
        Read the data until reaching the item. (defaults to from_item
        if it was specified and to the last stored item otherwise)

    from_time : float, optional
        (defaults to the beginning time in from_item)
        the specified times are included in the output

    to_time : float, optional
        (defaults to the ending time in to_item)
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
        index = read_index(filename, groupname)

    if groupname is None:
        groupname = index['group']

    if to_item is None:
        if from_item is None:
            to_item = index['items'][-1]
        else:
            to_item = from_item
    if from_item is None:
        from_item = index['items'][0]

    f1 = fetch_index(index['items'], from_item)
    f2 = fetch_index(index['items'], to_item)
    if not f2 >= f1:
        raise IOError('Item {} is located after item {} in file {}'
                      .format(from_item, to_item, filename))

    # index associated with the begin/end of from/to_item :
    f1_start = 0 if f1 == 0 else index['file_index'][f1 - 1] + 1
    f2_start = 0 if f2 == 0 else index['file_index'][f2 - 1] + 1
    f1_end = index['file_index'][f1]
    f2_end = index['file_index'][f2]

    if from_time is None:
        i1 = f1_start
    else:
        times = index['times'][f1_start:f1_end + 1]  # the end is included...
        try:
            # smallest time larger or equal to from_time
            i1 = f1_start + np.where(times >= from_time)[0][0]
        except IndexError:
            raise IOError('from_time {} is larger than the biggest time in '
                            'from_item {}'.format(from_time, from_internal_file))

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
    with h5py.File(filename, 'r') as h5file:
        group = h5file[groupname]
        if index['format'] == 'dense':
            if index['legacy']:
                features = group['features'][:, i1:i2 + 1].T  # i2 included
            else:
                features = group['features'][i1:i2 + 1, :]  # i2 included
            times = group['times'][i1:i2 + 1]
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
    files = index['items'][f1:f2 + 1]
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
            # Trying to read the first and only group in file
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
            files = list(g['items'][...])
            index = {'items': files, 'file_index': g['file_index'][...],
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
