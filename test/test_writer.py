"""Test of the h5features.writer module."""

import h5py
import os
import pytest

from aux import generate
from aux.utils import remove, assert_raise
from h5features.h5features import write
from h5features.writer import Writer
from h5features.features import Features
from h5features.labels import Labels
from h5features.items import Items
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
            Writer(self.filename, arg)

    def test_chunk_bad(self):
        args = [0.008-1e-2, .0001, 0, -1e30]
        msg = 'chunk size is below 8 Ko'
        for arg in args:
            with pytest.raises(IOError) as err:
                Writer(self.filename, arg)
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

    # def test_group(self):
    #     with pytest.raises(IOError):
    #         w = h5f.writer.Writer(self.filename)
    #         w.is_appendable(self.g, None)

    # def test_bad_dim(self):
    #     with pytest.raises(IOError) as ioerror:
    #         h5f._need_to_append(
    #             self.f, self.group, self.datasets, self.h5format,
    #             self.h5dim+1, self.h5type, self.version, self.times)
    #     assert 'mismatch' in str(ioerror.value)

class TestWrite:
    """test the Writer.write method"""
    def setup(self):
        self.data = generate.full_data(10)
        self.filename = 'test.h5'
        remove(self.filename)
        self.group = 'group'
        self.writer = Writer(self.filename)

    def teardown(self):
        remove(self.filename)

    def test_no_append(self):
        self.writer.write(self.data, self.group, append=False)
        with h5py.File(self.filename, 'r') as f:
            g = f[self.group]
            assert len(g['items'][...]) == 10
            assert not all([(l == 0).all() for l in g['features'][...]])
