"""Test of auxiliary functions of the h5features2 module.

@author: Mathieu Bernard
"""

import h5py
import pytest

from utils import remove, assert_raise
import generate
import h5features2.write as h5f
from h5features2.features import Features
from h5features2.times import Times


class TestCheckFile:
    """Test _check_file method."""

    def setup(self):
        self.filename = 'test.h5'

    def teardown(self):
        remove(self.filename)

    def test_no_file(self):
        assert_raise(h5f.check_file,
                     '/path/to/non/existant/file',
                     'No such file')

    def test_no_hdf5_file(self):
        with open(self.filename, 'w') as temp:
            temp.write('This is not a HDF5 file')

        assert_raise(h5f.check_file,
                     self.filename,
                     'not a HDF5 file')

    def test_good_file(self):
        h5f.check_file(self.filename)




class TestChunkSize:
    """Test of the _check_chunk_size method."""
    def test_good(self):
        args = [0.008, 0.01, 12, 1e30]
        for arg in args:
            h5f.check_chunk_size(arg)

    def test_bad(self):
        args = [0.008-1e-2, .0001, 0, -1e30]
        msg = 'chunk size below 8 Ko are not allowed'
        for arg in args:
            assert_raise(h5f.check_chunk_size, arg, msg)



class TestWriteAppendable:
    """Test of the _appendable() method."""

    def setup(self):
        # init default parameters
        self.filename = 'test.h5'
        self.group = 'features'
        self.datasets = ['files', 'times', 'features', 'file_index']
        self.dim = 20
        self.version = '1.0'
        self.tformat = 1

        # create a simple feature file
        items, times, feat = generate.full(10, dim=self.dim)
        self.features = Features(feat)
        self.times = Times(times)
        h5f.write(self.filename, self.group, items, times, feat)

        # read it with h5py
        self.f = h5py.File(self.filename, 'r')
        self.g = self.f.get(self.group)

    def teardown(self):
        self.f.close()
        remove(self.filename)

    def test_basic_works(self):
        h5f.appendable(self.g, self.features, self.times, self.version)

    # TODO Not here
    def test_version(self):
        assert self.g.attrs['version'] == self.version

    def test_group(self):
        with pytest.raises(IOError):
            h5f.appendable(self.g, None, None, None)

    # def test_bad_dim(self):
    #     with pytest.raises(IOError) as ioerror:
    #         h5f._need_to_append(
    #             self.f, self.group, self.datasets, self.h5format,
    #             self.h5dim+1, self.h5type, self.version, self.times)
    #     assert 'mismatch' in str(ioerror.value)
