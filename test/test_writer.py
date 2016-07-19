"""Test of the h5features.writer module."""

import h5py
import os
import pytest
import h5features as h5f
import numpy as np

from aux import generate
from aux.utils import remove, assert_raise
from h5features.writer import Writer
from h5features.data import Data


def test_create_a_file():
    name = 'azecqgxqsdqxws.eztcqezxf'
    assert not os.path.exists(name)
    Writer(name)
    assert os.path.exists(name)
    remove(name)


class TestInit:
    """Test of Writer.__init__"""
    def setup(self):
        self.filename = 'test.h5'

    def teardown(self):
        remove(self.filename)

    def test_not_hdf5_file(self):
        with open(self.filename, 'w') as temp:
            temp.write('This is not a HDF5 file')
        assert_raise(Writer, self.filename, 'not a HDF5 file')

    def test_good_file(self):
        for arg in self.filename, 'abc', 'toto.zip':
            Writer(self.filename)

    def test_chunk_good(self):
        args = [0.008, 0.01, 12, 1e30]
        for arg in args:
            Writer(self.filename, chunk_size=arg)

    def test_chunk_bad(self):
        args = [0.008-1e-2, .0001, 0, -1e30]
        msg = 'chunk size is below 8 Ko'
        for arg in args:
            with pytest.raises(IOError) as err:
                Writer(self.filename, chunk_size=arg)
            assert msg in str(err.value)


class TestWriteAppendable:
    """Test of the _appendable() method."""

    def setup(self):
        # init default parameters
        self.filename = 'test.h5'
        self.group = 'features'
        remove(self.filename)

        # create a simple feature file
        items, times, feat = generate.full(10)
        items2 = [i+'2' for i in items]
        self.data = Data(items, times, feat)
        self.data2 = Data(items2, times, feat)

        self.writer = Writer(self.filename)
        self.writer.write(self.data, self.group)

        # read it with h5py
        self.f = h5py.File(self.filename, 'r')
        self.g = self.f.get(self.group)

    def teardown(self):
        self.f.close()
        remove(self.filename)

    def test_basic_works(self):
        self.data2.is_appendable_to(self.g)

    def test_version(self):
        assert self.g.attrs['version'] == Writer('toto').version
        remove('toto')

    def test_group(self):
        with pytest.raises(IOError):
            w = h5f.writer.Writer(self.filename)
            w.is_appendable(self.g, None)


class TestWrite:
    """test the Writer.write method"""
    def setup(self):
        self.filename = 'test.h5'
        remove(self.filename)

        self.group = 'group'

    def teardown(self):
        remove(self.filename)

    def test_no_append(self):
        h5f.Writer(self.filename).write(
            generate.full_data(10), self.group, append=False)

        with h5py.File(self.filename, 'r') as f:
            g = f[self.group]
            assert len(g['items'][...]) == 10
            assert not all([(l == 0).all() for l in g['features'][...]])

    def test_append_distinct_items(self):
        data1 = generate.full_data(10)
        h5f.Writer(self.filename).write(data1, self.group, append=False)

        data2 = generate.full_data(10, items_root='items_bis')
        h5f.Writer(self.filename).write(data2, self.group, append=True)

        with h5py.File(self.filename, 'r') as f:
            g = f[self.group]
            items = g['items'][...]
            assert len(items) == 20
            assert all('bis' not in i for i in items[:10])
            assert all('bis' in i for i in items[10:])
            assert not all([(l == 0).all() for l in g['features'][...]])

    # def test_append_one_shared_item(self):
    #     data1 = generate.full_data(10)
    #     shape1 = data1.features()[-1].shape
    #     shared_item = data1.items()[-1]
    #     h5f.Writer(self.filename).write(data1, self.group, append=False)

    #     # one item in data, same as in data1
    #     data2 = generate.full_data(1, max_frames=10)
    #     shape2 = data2.features()[0].shape
    #     data2.items()[0] = shared_item

    #     expected_result = np.vstack((
    #         data1.dict_features()[shared_item],
    #         data2.dict_features()[shared_item]))

    #     h5f.Writer(self.filename).write(data2, self.group, append=True)

    #     data_read = h5f.Reader(self.filename, self.group).read()
    #     assert len(data_read.items()) == len(data1.items())
    #     assert np.array_equal(
    #         data_read.dict_features()[shared_item],
    #         expected_result)
    #     print shape1, shape2, data_read.dict_features()[shared_item].shape
    #     print data_read.items()
