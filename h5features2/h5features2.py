"""Provides the read() and write() wrapper functions."""

from h5features2.reader import Reader
from h5features2.writer import Writer
from h5features2 import dataset


def read(filename, groupname, from_item=None, to_item=None,
         from_time=None, to_time=None, index=None):
    """Reads in a h5features file.

    Parameters
    ----------

    filename : filename
        hdf5 file potentially serving as a container for many small files

    groupname : str
        h5 group to read the data from.

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

    times : dict --- A dictionary of 1D arrays values (keys are items)

    features : dict --- A dictionary of 2D arrays values (keys are items)
        with the 'feature' dimension along the columns and the 'time'
        dimension along the lines

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

    reader = Reader(filename, groupname, index)
    items, times, features = reader.read(from_item, to_item,
                                         from_time, to_time)
    return (dict(zip(items.data, times.data)),
            dict(zip(items.data, features.data)))


def write(filename, groupname, items_data, times_data, features_data,
          dformat='dense', chunk_size=0.1, sparsity=0.1):
    """Write h5features data in a HDF5 file.

    This function is a wrapper to the Writer class. It has three purposes:

    - Check parameters for errors (see details below),
    - Create Items, Times and Features objects
    - Send them to the Writer.

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

    IOError if the filename is not valid or parameters are inconsistent.
    NotImplementedError if features_format == 'sparse'

    """
    # Prepare the writer, raise on error
    writer = Writer(filename, chunk_size)

    # Prepare the items, raise on error
    items = dataset.items.Items(items_data)

    # Prepare the times according to format, raise on error
    times = (dataset.times.Times2D(times_data)
             if dataset.times.parse_times(times_data) == 2
             else dataset.times.Times(times_data))

    # Prepare the features according to format, raise on error
    features = (dataset.features.SparseFeatures(features_data, sparsity)
                if dataset.features.parse_dformat(dformat) == 'sparse'
                else dataset.features.Features(features_data))

    # Write all that stuff in the HDF5 file's specified group
    data = {'items':items, 'times':times, 'features':features}
    writer.write(data, groupname)


def simple_write(filename, group, times, features, item='item'):
    """Simplified version of write when there is only one item."""
    write(filename, group, [item], [times], [features])
