"""Test of the h5features.features module."""

import h5py
import numpy as np
import pytest

from .aux import generate
from .aux.utils import remove, assert_raise
from h5features.features import (
    Features, SparseFeatures,
    contains_empty, parse_dformat, parse_dtype, parse_dim)


def test_contains_empty_good():
    assert not contains_empty(generate.features(10))


def test_contains_empty_none():
    for arg in [None, False, 0]:
        assert contains_empty(arg)


def test_contains_empty_bad():
    bad = generate.features(10) + [np.array([])]
    assert contains_empty(bad)

    bad += generate.features(2, 3)
    assert contains_empty(bad)


def test_parse_dformat_good():
    for arg in ['dense', 'sparse']:
        assert arg == parse_dformat(arg, True)


def test_parse_dformat_bad():
    msg = 'is a bad features format, please choose'
    for arg in ['danse', 'spark', 1, 'spam']:
        with pytest.raises(IOError) as error:
            parse_dformat(arg, True)
        assert msg in str(error.value)


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
            assert_raise(parse_dtype, arg, '', TypeError)


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
        bad_feat[5] = bad_feat[5][:, :-1]
        assert_raise(parse_dim, bad_feat, 'same feature dimension')

        # TODO test with [np.array([1,2,3]),np.array([1,2])]
        # and [np.array([1,2,3]),np.array([1,2])]


class TestEq:
    def setup(self):
        self.feat = Features(generate.features(2, 10, 30))

    def teardown(self):
        pass

    def test_good(self):
        assert self.feat == self.feat

        feat = Features(self.feat.data)
        feat.dformat = 'spam'
        assert not feat.dformat == self.feat.dformat
        assert not feat == self.feat

        feat = Features(self.feat.data)
        feat.dtype = np.int64
        assert not feat == self.feat

        feat = Features(self.feat.data)
        feat.data = [1, 2, 3, [1, 2]]
        assert not feat.data == self.feat.data
        assert not feat == self.feat

    def test_bad(self):
        assert not self.feat == self.feat.data
        assert not self.feat == ''
        assert self.feat is not None

    def test_polymorph(self):
        feat = Features(self.feat.data)
        assert feat == self.feat
        assert not feat.__ne__(self.feat)
        assert feat.__eq__(self.feat)
        assert not feat != self.feat

    def test_s2d(self):
        feat = Features(self.feat.data, sparsetodense=True)
        assert not feat == self.feat


class TestFeatures:
    def setup(self):
        self.filename = 'test.h5'
        remove(self.filename)
        self.group = h5py.File(self.filename, 'w').create_group('group')
        self.data = generate.features(10, 5, 100)
        self.feat = Features(self.data)

    def teardown(self):
        remove(self.filename)

    def test_side_effect(self):
        feat2 = Features(self.feat.data)
        self.feat.create_dataset(self.group, 0.1)
        self.feat.write_to(self.group)
        assert self.feat == feat2

    def test_write(self):
        self.feat.create_dataset(self.group, 0.1)
        self.feat.write_to(self.group, append=True)

        assert 'features' in self.group
        f = self.group['features'][...]
        assert len(f) == sum([d.shape[0] for d in self.data])
