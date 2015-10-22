"""Provides Features class to the h5features module.

TODO Describe the structure of features.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import numpy as np
import scipy.sparse as sp

from h5features2.dataset.dataset import Dataset, _nb_per_chunk

def contains_empty(features):
    """Return True if one of the features is empty, False else."""
    # Is features empty ?
    if not features:
        return True

    # Are features sub-arrays empty ?
    sizes = [x.shape[0] for x in features]
    for s in sizes:
        if s == 0:
            return True

    # Nothing empty
    return False


def parse_dformat(dformat):
    """Return `dformat` or raise if it is not 'dense' or 'sparse'"""
    if not dformat in ['dense', 'sparse']:
        raise IOError(
            "{} is a bad features format, please choose 'dense' or 'sparse'"
            .format(dformat))
    return dformat


def parse_dtype(features):
    """Return the features scalar type, raise if error.

    Raise IOError if all features have not the same data type.
    Return dtype, the features scalar type.

    """
    types = [x.dtype for x in features]
    dtype = types[0]
    if not all([t == dtype for t in types]):
        raise IOError('features must be homogeneous.')
    return dtype


def parse_dim(features):
    """Return the features dimension, raise if error

    Raise IOError if features have not all the same positive
    dimension.  Return dim (int), the features dimension.

    """
    dims = [x.shape[1] for x in features]
    dim = dims[0]

    if not dim > 0:
        raise IOError('features dimension must be strictly positive.')
    if not all([d == dim for d in dims]):
        raise IOError('all files must have the same feature dimension.')

    return dim



class Features(Dataset):
    """This class manages features in h5features files."""

    def __init__(self, data, name='features'):
        """Initializes Features with data.

        Parameters:

        data : list of 2D numpy array like -- Features should have
            time along the lines and features along the columns
            (accomodating row-major storage in hdf5 files).

        Raise:

        IOError if features are badly formatted.

        """
        if contains_empty(data):
            raise IOError('all features must be non-empty')

        self.dformat = 'dense'
        self.dtype = parse_dtype(data)
        self.dim = parse_dim(data)
        super().__init__(data, name)

    def __eq__(self, other):
        try:
            return (other.dformat == self.dformat and
                    other.dtype == self.dtype and
                    other.dim == self.dim and
                    super().__eq__(other))
        except AttributeError:
            return False

    def is_appendable_to(self, group):
        """Return True if features are appendable to a HDF5 group."""
        return (group.attrs['format'] == self.dformat and
                group[self.name].dtype == self.dtype and
                # We use a method because dim differs in dense and sparse.
                self._dim(group) == self.dim)

    def _dim(self, group):
        """Return the dimension of features stored in a HDF5 group."""
        return group[self.name].shape[1]

    # TODO Document create_dataset order : Features before Times
    def create_dataset(self, group, chunk_size):
        """Initialize the features subgoup."""
        group.attrs['format'] = self.dformat
        super().create_dataset(group, self.dtype, self.dim, chunk_size)

        # attribute declared outside init is not safe. Used because
        # Times.create_dataset need it
        self.nb_per_chunk = _nb_per_chunk(self.dtype.itemsize,
                                          self.dim, chunk_size)

    def write(self, group):
        """Write stored features to a given group."""
        data = [x.todense() if sp.issparse(x)
                     else x for x in self.data]
        data = np.concatenate(data, axis=0)

        nb_group, dim = group[self.name].shape
        nb_data = data.shape[0]
        new_size = nb_group + nb_data

        group[self.name].resize((new_size, dim))
        group[self.name][nb_group:, :] = data


class SparseFeatures(Features):
    """This class is specialized for managing sparse matrices as features."""

    def __init__(self, data, sparsity, name='features'):
        super().__init__(data, name)
        self.dformat = 'sparse'
        self.sparsity = sparsity

        raise NotImplementedError('Writing sparse features is not implemented.')

    def __eq__(self, other):
        try:
            return self.sparsity == other.sparsity and super().__eq__(other)
        except AttributeError:
            return False

    def _dim(self, group):
        """Return the dimension of features stored in a HDF5 group."""
        return group.attrs['dim']

    def create_dataset(self, group, chunk_size):
        """Initializes sparse specific datasets."""
        group.attrs['format'] = self.dformat
        group.attrs['dim'] = self.dim

        # for storing sparse data we don't use the self.nb_per_chunk,
        # which is only used by the Writer to determine times chunking.
        per_chunk = _nb_per_chunk(self.dtype.itemsize, 1, chunk_size)

        group.create_dataset('coordinates', (0, 2), dtype=np.float64,
                             chunks=(per_chunk, 2), maxshape=(None, 2))

        group.create_dataset(self.name, (0,), dtype=self.dtype,
                             chunks=(per_chunk,), maxshape=(None,))

        dtype = np.int64
        chunks = (_nb_per_chunk(np.dtype(dtype).itemsize, 1, chunk_size),)
        group.create_dataset('frames', (0,), dtype=dtype,
                             chunks=chunks, maxshape=(None,))

        # Needed by Times.create_dataset
        self.nb_per_chunk = _nb_per_chunk(self.dtype.itemsize,
                                          int(round(self.sparsity*self.dim)),
                                          chunk_size)

    def write(self, group):
        pass
        # TODO implement this
        # 1- concatenation. put them in right format if they aren't already
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
