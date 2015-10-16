"""Test of the h5features2.writer module.

@author: Mathieu Bernard
"""

import pytest
from utils import remove, assert_raise
from h5features2.writer import Writer


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
