"""Test of read/write facilities of the h5features module."""

import numpy as np
import h5py
import pytest

import h5features.h5features as h5f
from .aux import generate
from .aux.utils import remove


def test_raise_on_write_sparse():
    a, b, c = generate.full(1)
    with pytest.raises(NotImplementedError) as ioerror:
        h5f.write('test.h5', 'group', a, b, c, dformat='sparse')
    assert 'sparse' in str(ioerror.value)


def test_raise_with_index():
    with pytest.raises(NotImplementedError):
        h5f.read('test.h5', index=0)


class TestH5FeaturesWrite:
    """Test write methods."""
    def setup(self):
        self.filename = 'test.h5'

    def teardown(self):
        remove(self.filename)

    def test_bad_data(self):
        with pytest.raises(IOError) as ioerror:
            h5f.write('/silly/path/to/no/where.h5', 'group', [], [], [])
        assert 'data is empty' == str(ioerror.value)

    def test_bad_file(self):
        a, b, c = generate.full(2)
        with pytest.raises(IOError) as ioerror:
            h5f.write('/silly/path/to/no/where.h5', 'group', a, b, c)
        assert all([s in str(ioerror.value)]
                   for s in ['/silly/path', 'No such file'])

    def test_bad_file2(self):
        with open(self.filename, 'w') as f:
            f.write('This is not a HDF5 file')

        data = generate.full(1)
        with pytest.raises(IOError) as ioerror:
            h5f.write(self.filename, 'group', data[0], data[1], data[2])
        msg = str(ioerror.value)
        assert self.filename in msg
        assert 'not a HDF5 file' in msg

    def test_simple_write(self):
        self.features_0 = np.random.randn(30, 20)
        self.times_0 = np.linspace(0, 2, 30)

        h5f.simple_write(
            self.filename, 'f', self.times_0, self.features_0)

        with h5py.File(self.filename, 'r') as f:
            assert ['f'] == list(f.keys())

            g = f.get('f')
            assert list(g.keys()) == (
                ['features', 'index', 'items', 'labels'])

            assert g['features'].shape == (30, 20)
            assert g['items'].shape == (1,)
            assert g['labels'].shape == (30,)
            assert g['index'].shape == (1,)

    def test_write(self):
        files, times, features = generate.full(10, 2, 5)
        h5f.write(self.filename, 'f', files, times, features)

        with h5py.File(self.filename, 'r') as f:
            assert ['f'] == list(f.keys())
            g = f.get('f')
            assert list(g.keys()) == ['features', 'index', 'items', 'labels']
            assert g.get('features').shape[1] == 2
            assert g.get('index').shape == (10,)
            assert g.get('items').shape == (10,)
            assert g.get('features').shape[0] == g.get('labels').shape[0]


class TestH5FeaturesReadWrite:
    """Test more advanced read/write facilities.

    This is a legacy test from h5features-1.0. It ensures the
    top-down compatibility of the module from current version to 1.0.

    """
    def setup(self):
        self.filename = 'test.h5'
        self.dim = 20  # Dimensions of the features

    def teardown(self):
        remove(self.filename)

    @pytest.mark.parametrize('properties', [False, True])
    def test_write_simple(self, properties):
        """write/read a file with a single item of 30 frames"""
        nframes = 30
        f = np.random.randn(nframes, self.dim)
        t = np.linspace(0, 2, nframes)
        if properties:
            props = {'a': 0, 'b': 'b'}
        else:
            props = None

        h5f.simple_write(
            self.filename, 'group1', t, f,
            properties=props, item='item', mode='w')

        if properties:
            tr, fr, pr = h5f.read(self.filename, 'group1')
            assert list(pr.keys()) == ['item']
            assert pr['item'] == props
        else:
            tr, fr = h5f.read(self.filename, 'group1')

        assert list(tr.keys()) == ['item']
        assert list(fr.keys()) == ['item']
        assert len(tr['item']) == 30
        assert len(fr['item']) == 30
        # assert tr['item'] == t
        assert (fr['item'] == f).all()

    def test_append(self):
        """Append a new item to an existing dataset."""
        i, t, f = generate.full(30, self.dim, 40, items_root='File')
        h5f.write(self.filename, 'group', i, t, f)

        # append new item to existing dataset
        features_added = np.zeros(shape=(1, self.dim))
        times_added = np.linspace(0, 2, 1)
        h5f.write(self.filename, 'group', ['File_31'],
                  [times_added], [features_added])

        with pytest.raises(IOError) as err:
            h5f.write(self.filename, 'group', ['File_3'],
                      [times_added], [features_added])
        assert 'data is not appendable to the group' in str(err.value)

        # read it
        times_r, features_r = h5f.read(self.filename, 'group')
        assert set(times_r.keys()) == set(i+['File_31'])
        assert set(features_r.keys()) == set(i+['File_31'])
        assert all(times_r['File_31'] == times_added)
        assert (features_r['File_31'] == features_added).all()

    def test_concat(self):
        """Concatenate new data to an existing item in an existing file."""

        # write a single item named 'item_0'
        data1 = generate.full(1, self.dim, 10, items_root='item')
        h5f.write(self.filename, 'group1', data1[0], data1[1], data1[2])
        h5f.write(self.filename, 'group3', data1[0], data1[1], data1[2])

        # concatenate new data to 'item_0'
        data2 = generate.full(1, self.dim, 20, items_root='item')
        h5f.write(self.filename, 'group2', data2[0], data2[1], data2[2])
        with pytest.raises(IOError):
            h5f.write(self.filename, 'group3', data2[0], data2[1], data2[2])
