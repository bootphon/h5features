"""Provides the Features class to the h5features module.

TODO Describe the structure of features.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import scipy.sparse as sp

from h5features2.chunk import nb_lines

def parse_dformat(dformat):
    """Raise if dformat is not valid and return it else."""
    if not dformat in ['dense', 'sparse']:
        raise IOError(
            "{} is a bad features format, please choose 'dense' or 'sparse'"
            .format(dformat))
    return dformat


def parse_dtype(features):
    """Check and return the features scalar type.

    Raise IOError if all features have not the same data type.

    """
    types = [x.dtype for x in features]
    dtype = types[0]
    if not all([t == dtype for t in types]):
        raise IOError('all files must have the same feature type.')
    return dtype


def parse_dim(features):
    """Check and return the features dimension.

    Raise IOError if features have not all the same positive
    dimension.

    """
    dims = [x.shape[1] for x in features]
    dim = dims[0]

    if not dim > 0:
        raise IOError('features dimension must be strictly positive.')
    if not all([d == dim for d in dims]):
        raise IOError('all files must have the same feature dimension.')

    return dim


def contains_empty(features):
    """Return True if one of the feature is empty, False else."""
    if not features:
        return True

    sizes = [x.shape[0] for x in features]
    for s in sizes:
        if s == 0:
            return True
    return False


class Features(object):
    """This class manages features in h5features files."""

    def __init__(self, features, dformat='dense'):
        """Initializes Features with a list of features.

        Parameters:

        features : list of 2D numpy array like -- Features should have
            time along the lines and features along the columns
            (accomodating row-major storage in hdf5 files).

        dformat : str, optional -- Which format to store the
            features into (sparse or dense). Default is
            dense. Actually sparse functionalitoes are not
            implemented.

        Raise:

        NotImplementedError if features_format == 'sparse'.

        IOError if features are badly formatted.

        """
        if dformat == 'sparse':
            raise NotImplementedError(
                'Writing sparse features is not yet implemented.')

        if contains_empty(features):
            raise IOError('all features must be non-empty')

        self.dformat = parse_dformat(dformat)
        self.dtype = parse_dtype(features)
        self.dim = parse_dim(features)
        self.features = features

    def is_compatible(self, group):
        """Return True if features are appendable to a HDF5 dataset."""
        # TODO for sparse we have dim = group.attrs['dim']
        return (group.attrs['format'] == self.dformat and
                group['features'].dtype == self.dtype and
                group['features'].shape[1] == self.dim)

    def create(self, group, chunk_size, sparsity):
        """Initialize the features subgoup."""
        group.attrs['format'] = self.dformat

        # init specific datasets for 'dense' and 'sparse' cases.
        nb_frames_by_chunk = (self._create_sparse(group, chunk_size, sparsity)
                              if self.dformat == 'sparse'
                              else self._create_dense(group, chunk_size))

        return nb_frames_by_chunk

    def _create_dense(self, group, chunk_size):
        """Initializes dense specific datasets."""
        nb_frames_by_chunk = max(
            10, nb_lines(self.dtype.itemsize, self.dim, chunk_size*1000))

        group.create_dataset('features',
                         (0, self.dim),
                         dtype=self.dtype,
                         chunks=(nb_frames_by_chunk, self.dim),
                         maxshape=(None, self.dim))

        return nb_frames_by_chunk

    def _create_sparse(self, group, chunk_size, sparsity):
        """Initializes sparse specific datasets."""
        nb_lines_by_chunk = max(
            10, nb_lines(self.dtype.itemsize, 1, chunk_size * 1000))

        group.create_dataset('coordinates',
                             (0, 2),
                             dtype=np.float64,
                             chunks=(nb_lines_by_chunk, 2),
                             maxshape=(None, 2))

        group.create_dataset('features',
                             (0,),
                             dtype=self.dtype,
                             chunks=(nb_lines_by_chunk,),
                             maxshape=(None,))

        # guessed from sparsity, used to determine time chunking
        nb_frames_by_chunk = max(10, nb_lines(self.dtype.itemsize,
                                              int(round(sparsity*self.dim)),
                                              chunk_size*1000))

        nb_lines_by_chunk = max(10, nb_lines(np.dtype(np.int64).itemsize,
                                             1,
                                             chunk_size*1000))

        group.create_dataset('frames',
                             (0,),
                             dtype=np.int64,
                             chuns=(nb_lines_by_chunk,),
                             maxshape=(None,))

        group.attrs['dim'] = self.dim

        return nb_frames_by_chunk

    def write(self, group):
        """Write stored features to a given group."""
        if self.dformat == 'sparse':
            raise NotImplementedError('writing sparse features not implemented')
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
        else:
            features = [x.todense() if sp.issparse(x)
                        else x for x in self.features]
            features = np.concatenate(features, axis=0)

        nb, d = group['features'].shape
        group['features'].resize((nb + features.shape[0], d))
        group['features'][nb:, :] = features
