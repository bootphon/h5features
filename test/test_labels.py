"""Test the labels module of h5features package."""

import h5py
import pytest
import numpy as np
from numpy.random import randn

from .aux import generate
from .aux.utils import assert_raise, remove
from h5features import write, read
from h5features.labels import Labels


def test_label_one_frame_2D():
    from h5features.labels import Labels
    gold = np.array([[0, 1, 2]])
    label = Labels([gold])
    assert isinstance(label.data, list)
    assert len(label.data) == 1

    test = label.data[0]
    assert isinstance(test, np.ndarray)
    assert test.ndim == gold.ndim
    assert test.shape == gold.shape
    assert (test == gold).all()


def test_check_bad():
    with pytest.raises(IOError) as err:
        Labels({'foo', 'bar'})
    assert 'not in a list' in str(err)

    with pytest.raises(IOError) as err:
        Labels([])
    assert 'list is empty' in str(err)

    with pytest.raises(IOError) as err:
        Labels([{0, 1}])
    assert 'must be numpy arrays' in str(err)

    with pytest.raises(IOError) as err:
        Labels([np.random.random((2, 2)), np.random.random((2, 3))])
    assert 'must have same shape on 2nd dim' in str(err)


def test_equality():
    t1 = generate.labels(10, tformat=2)
    l1 = Labels(t1)
    l2 = Labels(generate.labels(10, tformat=2))
    l3 = Labels(t1)
    l3.name = 'newname'

    assert l1 == l1
    assert l1 != l2
    assert l1 != np.random.random((5, 2))
    assert l1 != l3


class TestParseLabels:
    """Test of the parse_labels function."""
    def setup(self):
        self.t1 = generate.labels(10, tformat=1)
        self.t2 = generate.labels(10, tformat=2)

    def test_good(self):
        assert Labels.parse_dim(self.t1) == 1
        assert Labels.parse_dim(self.t1*2) == 1
        assert Labels.parse_dim(self.t2) == 2

        # 2D with shape[1] != 2
        Labels.parse_dim([randn(10, 3)]) == 2
        Labels.parse_dim([randn(5, 1)])
        Labels.parse_dim([randn(2, 1)])

    def test_bad_format(self):
        # 3D
        assert_raise(Labels.check, [randn(2, 2, 2)], 'must be 1 or 2')

    def test_bad_dims(self):
        for arg in [self.t1+self.t2,
                    self.t2+self.t1,
                    self.t2+[np.array([1, 2, 3])]]:
            assert_raise(Labels.check, arg, 'dimensions must be equal')


class TestLabels1D:
    """Test the Labels class for 1D labels vectors."""
    def setup(self):
        items, self.data, feats = generate.full(10, tformat=1)
        self.filename = 'test.h5'
        self.teardown()
        write(self.filename, 'group', items, self.data, feats)
        self.group = h5py.File(self.filename, 'a')['group']

    def teardown(self):
        remove(self.filename)

    def test_appendable(self):
        t = Labels(generate.labels(5, tformat=1))
        assert t.is_appendable_to(self.group)

        t = Labels(generate.labels(5, 12, tformat=1))
        assert t.is_appendable_to(self.group)

        t = Labels(generate.labels(10, 1, tformat=2))
        assert not t.is_appendable_to(self.group)

        t = Labels(generate.labels(5, 1, tformat=2))
        assert not t.is_appendable_to(self.group)

        t = Labels(generate.labels(10, 1, tformat=2))
        assert not t.is_appendable_to(self.group)

    def test_create(self):
        t1 = Labels(self.data)
        # we can't create an existing group
        # Exception is OSError for h5py<3.0 and ValueError for h5py>=3.0
        with pytest.raises(Exception) as err:
            t1.create_dataset(self.group, 10)
        assert 'create' in str(err.value)

    def test_side_effect(self):
        t = Labels(self.data)
        t2 = Labels(self.data)
        t.write_to(self.group)
        assert t == t2


def test_2D_one_frame():
    label = Labels([np.array([[0, 1, 2]])])
    assert isinstance(label.data, list)
    assert isinstance(label.data[0], np.ndarray)
    assert label.data[0].ndim == 2


class TestLabels2D:
    """Test of the Labels class for 2D labels vectors."""
    def setup(self):
        self.filename = 'test.h5'
        self.group = h5py.File(self.filename, 'w').create_group('group')
        self.data = generate.labels(2, 5, 2)

    def teardown(self):
        remove(self.filename)

    def test_init(self):
        assert Labels(self.data).dim == 2
        assert Labels(self.data).data[0].shape[1] == 2

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
        for dd, tt in zip(d, t):
            assert tt == dd


class TestSortedLabels:
    """Test sorting labels on write/read operations"""
    def setup(self):
        pass

    def test_sort_1D(self):
        list_1d = [np.array([i for i in range(9)])]
        Labels.check(list_1d)

        list_1d[0][[0, 1]] = list_1d[0][[1, 0]]
        assert_raise(Labels.check, list_1d, 'not sorted')

        list_1d.append(np.array([i for i in range(9)]))
        assert_raise(Labels.check, list_1d, 'not sorted')

        list_1d[0][[1, 0]] = list_1d[0][[0, 1]]
        Labels.check(list_1d)

    def test_sorted_2D(self):
        # dont use generate.labels to ensure 2 elements.
        list_2d = [
            np.array([[0., 1.],
                      [0.33333333, 1.33333333],
                      [0.66666667, 1.66666667],
                      [1., 2.]]),
            np.array([[0., 1.],
                      [1., 2.]])]

        # sorted, pass
        Labels.check(list_2d)

        # unsorted, fails
        list_2d[0][[0, 1], :] = list_2d[0][[1, 0], :]
        assert_raise(Labels.check, list_2d, 'not sorted')
