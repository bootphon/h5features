"""Test of the h5features2.features module.

@author: Mathieu Bernard <mmathieubernardd@gmail.com>
"""

import numpy as np
import pytest

import generate
from utils import remove, assert_raise
from h5features2.features import Features, parse_dformat, parse_dim


class TestFeaturesDFormat:
    """Test the dformat parameter."""
    def setup(self):
        self.filename = 'test.h5'
        self.dim = 3
        self.size = 20
        self.data = generate.features(self.size, self.dim)

    def teardown(self):
        remove(self.filename)

    def test_raise_on_sparse(self):
        with pytest.raises(NotImplementedError) as err:
            Features(self.data, 'sparse')
        assert 'sparse' in str(err.value)

    def test_ok_on_dense(self):
        feat = Features(self.data, 'dense')
        assert feat.dformat == 'dense'

        feat = Features(self.data)
        assert feat.dformat == 'dense'

    def test_bad(self):
        msg = 'is a bad features format, please choose'
        feat = Features(self.data)
        for arg in ['danse', 'spark', 1, 'spam']:
            assert_raise(parse_dformat, arg, msg)


class TestFeaturesParse:
    """Test method."""
    def setup(self):
        self.feat = generate.features(10)

    def test_empty(self):
        """Assert raise on empty feature"""
        Features(self.feat)

        empty1 = self.feat
        empty1.append(np.array([]))
        empty2 = [np.array([])]*3
        for arg in [empty1, empty2]:
            assert_raise(Features, arg, 'all features must be non-empty')

    def test_dim_good(self):
        for dim in [1, 2, 5, 20]:
            feat = generate.features(10, dim)
            d = parse_dim(feat)
            assert d == dim

    def test_dim_bad(self):
        bad_feat = self.feat
        bad_feat[5] = bad_feat[5][:,:-1]

        assert_raise(parse_dim, bad_feat, 'same feature dimension')

        # TODO test with [np.array([1,2,3]),np.array([1,2])]
        # and [np.array([1,2,3]),np.array([1,2])]
