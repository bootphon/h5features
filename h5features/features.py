# Copyright 2014-2019 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
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

"""Provides Features class to the h5features module."""

import numpy as np
import scipy.sparse as sp

from .entry import Entry
from .entry import nb_per_chunk


def contains_empty(features):
    """Check features data are not empty

    :param features: The features data to check.
    :type features: list of numpy arrays.

    :return: True if one of the array is empty, False else.

    """
    if not features:
        return True
    for feature in features:
        if feature.shape[0] == 0:
            return True
    return False


def parse_dformat(dformat, check=True):
    """Return `dformat` or raise if it is not 'dense' or 'sparse'"""
    if check and dformat not in ['dense', 'sparse']:
        raise IOError(
            "{} is a bad features format, please choose 'dense' or 'sparse'"
            .format(dformat))
    return dformat


def parse_dtype(features, check=True):
    """Return the features scalar type, raise if error

    Raise IOError if all features have not the same data type.
    Return dtype, the features scalar type.

    """
    dtype = features[0].dtype
    if check:
        types = [x.dtype for x in features]
        if not all([t == dtype for t in types]):
            raise IOError('features must be homogeneous')
    return dtype


def parse_dim(features, check=True):
    """Return the features dimension, raise if error

    Raise IOError if features have not all the same positive
    dimension.  Return dim (int), the features dimension.

    """
    # try:
    dim = features[0].shape[1]
    # except IndexError:
    #     dim = 1

    if check and not dim > 0:
        raise IOError('features dimension must be strictly positive')
    if check and not all([d == dim for d in [x.shape[1] for x in features]]):
        raise IOError('all files must have the same feature dimension')
    return dim


class Features(Entry):
    """This class manages features in h5features files

    :param data: Features must have time along the lines and
        features along the columns (accomodating row-major storage
        in hdf5 files).
    :type data: list of 2D numpy arrays

    :param bool sparsetodense: If True convert sparse matrices to
        dense when writing. Used for compatibility with 1.0.

    :raise IOError: if features are badly formatted.

    """
    def __init__(self, data, check=True, sparsetodense=False):
        if check:
            if contains_empty(data):
                raise IOError('all features must be non-empty')

        # raise on error
        dtype = parse_dtype(data, check)
        dim = parse_dim(data, check)
        super(Features, self).__init__('features', data, dim, dtype)

        self.dformat = 'dense'
        self.sparsetodense = sparsetodense

    def __eq__(self, other):
        if self is other:
            return True
        try:
            ndata = len(self.data)
            # check the little attributes
            if not (self.dformat == other.dformat and
                    self.sparsetodense == other.sparsetodense and
                    self.name == other.name and
                    self.dim == other.dim and
                    self.dtype == other.dtype and
                    ndata == len(other.data)):
                return False
            # check big data
            for i in range(ndata):
                if not (self.data[i] == other.data[i]).all():
                    return False
            return True
        except AttributeError:
            return False

    def is_sparse(self):
        """Return True if features are sparse matrices"""
        return self.dformat == 'sparse'

    def is_appendable_to(self, group):
        """Return True if features are appendable to a HDF5 group"""
        return (group.attrs['format'] == self.dformat and
                group[self.name].dtype == self.dtype and
                # We use a method because dim differs in dense and sparse.
                self._group_dim(group) == self.dim)

    def _group_dim(self, group):
        """Return the dimension of features stored in a HDF5 group"""
        try:
            return group[self.name].shape[1]
        except IndexError:
            return 1

    def create_dataset(
            self, group, chunk_size, compression=None, compression_opts=None):
        """Initialize the features subgoup"""
        group.attrs['format'] = self.dformat
        super(Features, self)._create_dataset(
            group, chunk_size, compression, compression_opts)

        # TODO attribute declared outside __init__ is not safe. Used
        # because Labels.create_dataset need it.
        if chunk_size != 'auto':
            self.nb_per_chunk = nb_per_chunk(
                self.dtype.itemsize, self.dim, chunk_size)
        else:
            self.nb_per_chunk = 'auto'

    def write_to(self, group, append=False):
        """Write stored features to a given group"""
        if self.sparsetodense:
            self.data = [x.todense() if sp.issparse(x) else x
                         for x in self.data]

        nframes = sum([d.shape[0] for d in self.data])
        dim = self._group_dim(group)
        feats = np.concatenate(self.data, axis=0)

        if append:
            nframes_group = group[self.name].shape[0]
            group[self.name].resize(nframes_group + nframes, axis=0)
            if dim == 1:
                group[self.name][nframes_group:] = feats
            else:
                group[self.name][nframes_group:, :] = feats
        else:
            group[self.name].resize(nframes, axis=0)
            group[self.name][...] = feats if dim == 1 else feats


class SparseFeatures(Features):
    """This class is specialized for managing sparse matrices as features"""

    def __init__(self, data, sparsity, check=True):
        self.dformat = 'sparse'

        if sparsity < 0 or sparsity > 1:
            raise ValueError('sparsity must be in [0, 1]')
        self.sparsity = sparsity

        super(SparseFeatures, self).__init__(data, check)
        raise NotImplementedError(
            'writing sparse features is not implemented')

    def __eq__(self, other):
        try:
            return (self.sparsity == other.sparsity and
                    super(SparseFeatures, self).__eq__(other))
        except AttributeError:
            return False

    def _group_dim(self, group):
        """Return the dimension of features stored in a HDF5 group"""
        return group.attrs['dim']

    def create_dataset(self, group, chunk_size):
        """Initializes sparse specific datasets"""
        group.attrs['format'] = self.dformat
        group.attrs['dim'] = self.dim

        if chunk_size == 'auto':
            group.create_dataset(
                'coordinates', (0, 2), dtype=np.float64,
                chunks=True, maxshape=(None, 2))

            group.create_dataset(
                self.name, (0,), dtype=self.dtype,
                chunks=True, maxshape=(None,))

        else:
            # for storing sparse data we don't use the self.nb_per_chunk,
            # which is only used by the Writer to determine times chunking.
            per_chunk = nb_per_chunk(self.dtype.itemsize, 1, chunk_size)

            group.create_dataset(
                'coordinates', (0, 2), dtype=np.float64,
                chunks=(per_chunk, 2), maxshape=(None, 2))

            group.create_dataset(
                self.name, (0,), dtype=self.dtype,
                chunks=(per_chunk,), maxshape=(None,))

        dtype = np.int64
        if chunk_size == 'auto':
            chunks = True
            self.nb_per_chunk = 'auto'
        else:
            chunks = (nb_per_chunk(np.dtype(dtype).itemsize, 1, chunk_size),)
            # Needed by Times.create_dataset
            self.nb_per_chunk = nb_per_chunk(
                self.dtype.itemsize,
                int(round(self.sparsity*self.dim)),
                chunk_size)

        group.create_dataset(
            'frames', (0,), dtype=dtype,
            chunks=chunks, maxshape=(None,))

    def write_to(self, group, append=False):
        raise NotImplementedError
        # TODO implement this
        # 1- concatenation. put them in right format if they aren't already
        # are_sparse = [x.isspmatrix_coo() for x in features]
        # if not(all(are_sparse)):
        #    for x in features:
        #        if not(x.isspmatrix_coo()):
        #            x = sp.coo_matrix(x)
        # need to get the coo by line ...

        # 2- writing
        # nb, = g['features'].shape
        # g['feature'].resize((nb+features.shape[0],))
        # g['features'][nb:] = features
        # g['coordinates'].resize((nb+features.shape[0],2))
        # g['coordinates'][nb:,:] = coordinates
        # nb, = g['frames'].shape
        # g['frames'].resize((nb+frames.shape[0],))
        # g['frames'][nb:] = frames
