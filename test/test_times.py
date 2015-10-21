"""Test the times module of h5features2 package.

@author: Mathieu Bernard

"""

import h5py
from numpy.random import randn
import pytest

import generate
from utils import assert_raise, remove
from h5features2.h5features2 import write, read
from h5features2.dataset.times import *


class TestParseTimes:
    """Test of the parse_times function."""
    def setup(self):
        self.t1 = generate.times(10, tformat=1)
        self.t2 = generate.times(10, tformat=2)

    def teardown(self):
        pass

    def test_good(self):
        assert parse_times(self.t1) == 1
        assert parse_times(self.t1*2) == 1
        assert parse_times(self.t2) == 2

    def test_bad_format(self):
        # 3D
        assert_raise(parse_times, [randn(2, 2, 2)], '1D or 2D numpy arrays')
        # 2D with shape[1] != 2
        assert_raise(parse_times, [randn(10, 3)], 'must have 2 elements')
        assert_raise(parse_times, [randn(5, 1)], 'must have 2 elements')
        assert_raise(parse_times, [randn(2, 1)], 'must have 2 elements')

    def test_bad_dims(self):
        for arg in [self.t1+self.t2,
                    self.t2+self.t1,
                    self.t2+[np.array([1, 2, 3])]]:
            assert_raise(parse_times, arg, 'the same dimension')


def test_times_init():
    """Test silly data input"""
    for arg in [[], 1, 'spam', generate.times(5)]:
        t1, t2 = Times(arg), Times2D(arg)
        assert t1.name == t2.name == 'times'
        assert t1.data == t2.data == arg
        assert t1.tformat == 1
        assert t2.tformat == 2


class TestTimes1D:
    """Test the Times class."""
    def setup(self):
        items, self.data, feats = generate.full(10,tformat=1)
        self.filename = 'test.h5'
        self.teardown()
        write(self.filename, 'group', items, self.data, feats)
        self.group = h5py.File(self.filename, 'a')['group']

    def teardown(self):
        remove(self.filename)

    def test_appendable(self):
        t = Times(generate.times(5, tformat=1))
        assert t.is_appendable_to(self.group)

        t = Times(generate.times(5, 12, tformat=1))
        assert t.is_appendable_to(self.group)

        t = Times(generate.times(10, 1, tformat=2))
        assert t.is_appendable_to(self.group)

        t = Times2D(generate.times(5, 1, tformat=1))
        assert not t.is_appendable_to(self.group)

        t = Times2D(generate.times(10, 1, tformat=2))
        assert not t.is_appendable_to(self.group)

    def test_create(self):
        t1 = Times(self.data, name='try1')
        t1.create_dataset(self.group, 10)
        assert t1.name in self.group
        assert len(self.group[t1.name]) == 0

        # we can't create an existing group
        with pytest.raises(RuntimeError) as err:
            t1.create_dataset(self.group, 10)
        assert 'Name already exists' in str(err.value)

        t2 = Times([], name='toto')
        t2.create_dataset(self.group, 10)
        assert t2.name in self.group
        assert len(self.group[t2.name]) == 0


class TestReadWriteLevel:
    """Test top level consistency of read/write times"""
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
    def _test_wr(self, time_format):
        """Test retrieving times and files after a write/read operation."""
        items, t_gold, feat = generate.full(self.nbitems, tformat=time_format)
        write(self.filename, self.group, items, t_gold, feat)
        t, _ = read(self.filename, self.group)

        assert len(t) == self.nbitems
        if time_format == 2:
            assert all([tt.shape[1] == time_format for tt in t.values()])

        # build a dict from gold to compare with t
        d = {}
        for k, v in zip(items, t_gold): d[k] = v
        # compare the two dicts
        for dd, tt in zip(d, t): assert tt == dd
