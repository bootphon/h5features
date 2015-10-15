"""Provides a write function for h5features files."""


from h5features2.writer import Writer
from h5features2.features import Features, SparseFeatures, parse_dformat
from h5features2.items import Items
from h5features2.times import Times, Times2D, parse_times


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
    items = Items(items_data)

    # Prepare the times according to format, raise on error
    times = (Times2D(times_data)
             if parse_times(times_data) == 2
             else Times(times_data))

    # Prepare the features according to format, raise on error
    features = (SparseFeatures(features_data, sparsity)
                if parse_dformat(dformat) == 'sparse'
                else Features(features_data))

    # Write all that stuff in the HDF5 file's specified group
    data = {'items':items, 'times':times, 'features':features}
    writer.write(data, groupname)


def simple_write(filename, group, times, features, fileid='features'):
    """Simplified version of write when there is only one file
    """
    write(filename, group, [fileid], [times], [features])
