"""Test of the h5features2.writer module.

@author: Mathieu Bernard
"""

import h5py
import pytest

import generate
from utils import remove, assert_raise
from h5features2.h5features2 import write
from h5features2.writer import Writer
from h5features2.dataset.features import Features
from h5features2.dataset.times import Times
from h5features2.dataset.items import Items

class TestInit:
    """Test of Writer.__init__"""
    def setup(self):
        self.filename = 'test.h5'

    def teardown(self):
        remove(self.filename)

    def test_nto_hdf5_file(self):
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

        # create a simple feature file
        items, times, feat = generate.full(10)
        self.features = Features(feat)
        self.times = Times(times)
        self.items = Items(items)
        self.items2 = Items([i+'2' for i in items])
        write(self.filename, self.group, items, times, feat)

        # read it with h5py
        self.f = h5py.File(self.filename, 'r')
        self.g = self.f.get(self.group)

    def teardown(self):
        self.f.close()
        remove(self.filename)

    def test_basic_works(self):
        w = Writer(self.filename)
        w.is_appendable_to(self.g, {'features':self.features,
                                 'items':self.items2,
                                 'times':self.times})

    def test_version(self):
        assert self.g.attrs['version'] == Writer(self.filename).version

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
