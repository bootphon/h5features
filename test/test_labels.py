"""Test the labels module of h5features package."""

import h5py
from numpy.random import randn
import pytest

import generate
from utils import assert_raise, remove
from h5features.h5features import write, read
from h5features.labels import *


class TestParseLabels:
    """Test of the parse_labels function."""
    def setup(self):
        self.t1 = generate.times(10, tformat=1)
        self.t2 = generate.times(10, tformat=2)

    def teardown(self):
        pass

    def test_good(self):
        assert parse_labels(self.t1, True) == 1
        assert parse_labels(self.t1*2, True) == 1
        assert parse_labels(self.t2, True) == 2

        # 2D with shape[1] != 2
        parse_labels([randn(10, 3)]) == 2
        parse_labels([randn(5, 1)])
        parse_labels([randn(2, 1)])

    def test_bad_format(self):
        # 3D
        assert_raise(parse_labels, [randn(2, 2, 2)], '1D or 2D numpy arrays')

    def test_bad_dims(self):
        for arg in [self.t1+self.t2,
                    self.t2+self.t1,
                    self.t2+[np.array([1, 2, 3])]]:
            assert_raise(parse_labels, arg, 'the same dimension')


class TestLabels1D:
    """Test the Labels class for 1D labels vectors."""
    def setup(self):
        items, self.data, feats = generate.full(10,tformat=1)
        self.filename = 'test.h5'
        self.teardown()
        write(self.filename, 'group', items, self.data, feats)
        self.group = h5py.File(self.filename, 'a')['group']

    def teardown(self):
        remove(self.filename)

    def test_appendable(self):
        t = Labels(generate.times(5, tformat=1))
        assert t.is_appendable_to(self.group)

        t = Labels(generate.times(5, 12, tformat=1))
        assert t.is_appendable_to(self.group)

        t = Labels(generate.times(10, 1, tformat=2))
        assert not t.is_appendable_to(self.group)

        t = Labels(generate.times(5, 1, tformat=2))
        assert not t.is_appendable_to(self.group)

        t = Labels(generate.times(10, 1, tformat=2))
        assert not t.is_appendable_to(self.group)

    def test_create(self):
        t1 = Labels(self.data)
        # we can't create an existing group
        with pytest.raises(RuntimeError) as err:
            t1.create_dataset(self.group, 10)
        assert 'create' in str(err.value)

    def test_side_effect(self):
        t = Labels(self.data)
        t2 = Labels(self.data)
        t.write_to(self.group)
        assert t == t2

class TestLabels2D:
    """Test of the Labels class for 2D labels vectors."""
    def setup(self):
        self.filename = 'test.h5'
        self.group = h5py.File(self.filename).create_group('group')
        self.data = generate.times(10,20,2)

    def teardown(self):
        remove(self.filename)

    def test_init(self):
        assert Labels(self.data).dim == 2

    def test_side_effect(self):
        t = Labels(self.data)
        t2 = Labels(self.data)
        t.create_dataset(self.group, per_chunk=100)
        t.write_to(self.group)
        assert t == t2


class TestReadWriteLevel:
    """Test top level consistency of read/write labels"""
    def setup(self):
        self.filename = 'test.h5'
        self.group = 'group'
        self.nbitems = 100

    def teardown(self):
        remove(self.filename)

    def test_wr_1D(self):
        self._test_wr(1)

    def test_wr_2D(self):
        self._test_wr(2)

    # This function is prefixed by an underscore so that it is not
    # detected by pytest as a test function.
    def _test_wr(self, labeldim):
        """Test retrieving labels and files after a write/read operation."""
        items, t_gold, feat = generate.full(self.nbitems, tformat=labeldim)
        write(self.filename, self.group, items, t_gold, feat)
        t, _ = read(self.filename, self.group)

        assert len(t) == self.nbitems
        if not labeldim == 1:
            assert all([tt.shape[1] == labeldim for tt in t.values()])

        # build a dict from gold to compare with t
        d = dict(zip(items, t_gold))
        # d = {}
        # for k, v in zip(items, t_gold): d[k] = v
        # compare the two dicts
        for dd, tt in zip(d, t): assert tt == dd
