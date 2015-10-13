"""Provides the Features class to the h5features module.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

import h5py

class Features(object):
    """This class manages features in h5features files."""
    def __init__(self, features, format='dense'):
        """Initializes Features with a list of features.

        Parameters:

        features : list of 2D numpy array like -- Features should have
            time along the lines and features along the columns
            (accomodating row-major storage in hdf5 files).

        format : str, optional -- Which format to store the features
            into (sparse or dense). Default is dense. Actually sparse
            functionalitoes are not implemented.

        Raise NotImplementedError if features_format == 'sparse'.

        """
        if format == 'sparse':
            raise NotImplementedError(
                'Writing sparse features is not yet implemented.')

        self.format = format


    def check(self, features):
        """Raise IOError if features are not in a correct state.

        Raise:

        Raise IOError if one of the feature is empty, if features have not
        all the same positive dimension, or if all features have not the
        same data type.

        Raise IOError if the features format is not 'dense' or 'sparse'

        Side effect:

        Create self.dim and self.dtype.
        dim : int -- Dimension of the features
        dtype : type -- Data type of features scalars

        """
        if not self.format in ['dense', 'sparse']:
            raise IOError(
                "{} is a bad features format, please choose 'dense' or 'sparse'"
                .format(self.format))

        nb_frames = [x.shape[0] for x in features]
        if not all([n > 0 for n in nb_frames]):
            raise IOError('all features must be non-empty')

        # retrieve features dimension in self.dim
        dims = [x.shape[1] for x in features]
        self.dim = dims[0]

        if not self.dim > 0:
            raise IOError('features dimension must be strictly positive.')

        if not all([d == self.dim for d in dims]):
            raise IOError('all files must have the same feature dimension.')

        # retrieve features type in self.dtype
        types = [x.dtype for x in features]
        self.dtype = types[0]

        if not all([t == self.dtype for t in types]):
            raise IOError('all files must have the same feature type.')

    def is_compatible(self, group):
        """Return True if stored features are compatible with given group."""
        dim = (group.attrs['dim'] if self.format == 'sparse'
               else group['features'].shape[1])

        return (group.attrs['format'] == self.format and
                group['features'].dtype == self.dtype and
                dim == self.dim)

    def create(self, group, chunk_size, sparsity):
        """Initialize the features subgoup."""
        group.attrs['format'] = features_format

        # init specific datasets for 'dense' and 'sparse' cases.
        nb_frames_by_chunk = (self._create_sparse(group, chunk_size, sparsity)
                              if features_format == 'sparse'
                              else self._create_dense(group, chunk_size))

        return nb_frames_by_chunk

    def _create_dense(self, group, chunk_size):
        """Initializes dense specific datasets."""
        nb_frames_by_chunk = max(
            10, nb_lines(self.dtype.itemsize, self.dim, chunk_size*1000))

        g.create_dataset('features',
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
                             dtype=features_type,
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

        g.attrs['dim'] = self.dim

        return nb_frames_by_chunk


    def write(self):
        pass
