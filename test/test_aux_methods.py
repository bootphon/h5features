"""Test of auxiliary functions of the h5features2 module.

@author: Mathieu Bernard
"""

import h5py
import os
import numpy as np
import pytest

from utils import remove, assert_raise
import generate
import h5features2.write as h5f


class TestCheckFile:
    """Test _check_file method."""

    def setup(self):
        self.filename = 'test.h5'

    def teardown(self):
        remove(self.filename)

    def test_no_file(self):
        assert_raise(h5f._check_file,
                     '/path/to/non/existant/file',
                     'No such file')

    def test_no_hdf5_file(self):
        with open(self.filename, 'w') as temp:
            temp.write('This is not a HDF5 file')

        assert_raise(h5f._check_file,
                     self.filename,
                     'not a HDF5 file')

    def test_good_file(self):
        h5f._check_file(self.filename)




class TestChunkSize:
    """Test of the _check_chunk_size method."""
    def test_good(self):
        args = [0.008, 0.01, 12, 1e30]
        for arg in args:
            h5f._check_chunk_size(arg)

    def test_bad(self):
        args = [0.008-1e-2, .0001, 0, -1e30]
        msg = 'chunk size below 8 Ko are not allowed'
        for arg in args:
            assert_raise(h5f._check_chunk_size, arg, msg)


class TestCheckFeaturesFormat:
    """Test the _check_features_format method."""
    def test_good(self):
        for arg in ['dense', 'sparse']:
            h5f._check_features_format(arg)

    def test_bad(self):
        msg = 'is a bad features format, please choose'
        for arg in ['danse', 'spark', 1, 'spam']:
            assert_raise(h5f._check_features_format, arg, msg)


class TestCheckFeatures:
    """Test the _check_features method."""
    def setup(self):
        _, _, self.feat = generate.features(10)

    def test_empty(self):
        """Assert raise on empty feature"""
        h5f._check_features(self.feat)

        empty1 = self.feat
        empty1.append(np.array([]))
        empty2 = [np.array([])]*3
        for arg in [empty1, empty2]:
            assert_raise(h5f._check_features, arg,
                         'all features must be non-empty')

    def test_dim_good(self):
        for dim in [1, 2, 5, 20]:
            _, _, feat = generate.features(10, dim)
            d, _ = h5f._check_features(feat)
            assert d == dim

    def test_dim_bad(self):
        bad_feat = self.feat
        bad_feat[5] = bad_feat[5][:,:-1]

        assert_raise(h5f._check_features, bad_feat, 'same feature dimension')

        # TODO test with [np.array([1,2,3]),np.array([1,2])]
        # and [np.array([1,2,3]),np.array([1,2])]


class TestWriteNeedToAppend:
    """Test of the _need_to_append() method."""

    def setup(self):
        # init default parameters
        self.filename = 'test.h5'
        self.group = 'features'
        self.datasets = ['files', 'times', 'features', 'file_index']
        self.h5format = 'dense'
        self.h5dim = 20
        self.h5type = 'float64'
        self.version = '1.0'
        self.time_format = 1

        # create a simple feature file
        self.files, self.times, self.features = generate.features(
            10, n_feat=self.h5dim)
        h5f.write(self.filename, self.group,
                  self.files, self.times, self.features)

        # read it with h5py
        self.f = h5py.File(self.filename, 'r')
        self.g = self.f.get(self.group)

    def teardown(self):
        self.f.close()
        remove(self.filename)

    def test_basic_works(self):
        h5f._appendable(self.g, self.h5format, self.h5dim,
                        self.h5type, self.version, self.time_format)

    # TODO Not here
    def test_version(self):
        assert self.g.attrs['version'] == self.version

    def test_group(self):
        with pytest.raises(IOError):
            h5f._appendable(self.g, None, None, None, None, None)

    # def test_bad_dim(self):
    #     with pytest.raises(IOError) as ioerror:
    #         h5f._need_to_append(
    #             self.f, self.group, self.datasets, self.h5format,
    #             self.h5dim+1, self.h5type, self.version, self.times)
    #     assert 'mismatch' in str(ioerror.value)
