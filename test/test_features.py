"""Test of the h5features2.features module.

@author: Mathieu Bernard <mmathieubernardd@gmail.com>
"""

import numpy as np
import pytest

import generate
from utils import remove, assert_raise
from h5features2.dataset.features import *


def test_contains_empty_good():
    """Test the contains_empty function."""
    assert not contains_empty(generate.features(10))


def test_contains_empty_none():
    """Test the contains_empty function."""
    for arg in [None, False, 0]:
        assert contains_empty(arg)


def test_contains_empty_bad():
    """Test the contains_empty function."""
    bad = generate.features(10) + [np.array([])]
    assert contains_empty(bad)

    bad += generate.features(2, 3)
    assert contains_empty(bad)


def test_parse_dformat_good():
    """Test the parse_dformat function."""
    for arg in ['dense', 'sparse']:
        assert arg == parse_dformat(arg)


def test_parse_dformat_bad():
    """Test the parse_dformat function."""
    msg = 'is a bad features format, please choose'
    for arg in ['danse', 'spark', 1, 'spam']:
        assert_raise(parse_dformat, arg, msg)


class TestParseDType:
    """Test the parse_dtype function."""
    def setup(self):
        self.data = generate.features(10)

    def teardown(self):
        pass

    def test_good(self):
        assert np.float64 == parse_dtype(self.data)

    def test_bad(self):
        arg = self.data
        arg[0] = arg[0].astype(int)
        assert_raise(parse_dtype, arg, 'homogeneous')

    def test_not_iterable(self):
        args = [self.data.append(np.array([])), 1]
        for arg in args:
            assert_raise(parse_dtype, arg, 'not iterable', TypeError)


class TestParseDim:
    """Test of the parse_dim function."""
    def setup(self):
        self.data = {}
        for dim in [1, 2, 3, 5, 10]:
            self.data[dim] = generate.features(10, dim)

    def teardown(self):
        pass

    def test_good(self):
        for dim, feat in self.data.items():
            assert dim == parse_dim(feat)

    def test_bad(self):
        bad = self.data[2] + self.data[3]
        assert_raise(parse_dim, bad, 'must have the same')


class TestFeaturesDFormat:
    """Test the dformat parameter."""
    def setup(self):
        self.data = generate.features(10)

    def teardown(self):
        pass

    def test_raise_on_sparse(self):
        with pytest.raises(NotImplementedError) as err:
            SparseFeatures(self.data, 0)
        assert 'sparse' in str(err.value)

    def test_ok_on_dense(self):
        feat = Features(self.data)
        assert feat.dformat == 'dense'


class TestFeaturesParse:
    """Test method."""
    def setup(self):
        self.feat = generate.features(10)

    def test_raise_on_empty(self):
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
