"""Test of the h5features.reader module.

.. note::

    This test assumes the h5features.writer pass it's tests.

"""

import h5py
import pytest
import tempfile

import generate
from utils import remove
from h5features.writer import Writer
from h5features.reader import Reader

class TestReader:
    def setup(self):
        self.filename = 'test.h5'
        self.groupname = 'group'
        self.nitems = 10
        self.data = generate.full_dict(self.nitems)

        Writer(self.filename).write(self.data, self.groupname)

    def teardown(self):
        remove(self.filename)

    def test_init_not_file(self):
        with pytest.raises(IOError) as err:
            Reader(self.filename + 'spam', self.groupname)
        assert 'not a HDF5 file' in str(err.value)

    def test_init_not_hdf(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(b'This is not a HDF5 file')
        with pytest.raises(IOError) as err:
            Reader(temp.name, self.groupname)
        assert 'not a HDF5 file' in str(err.value)
        remove(temp.name)

    def test_init_not_group(self):
        with pytest.raises(IOError) as err:
            Reader(self.filename, self.groupname + 'spam')
        assert 'not a valid group' in str(err.value)

    def test_read_basic(self):
        Reader(self.filename, self.groupname).read()

    # def test_load_index(self):
    #     group = h5py.File(self.filename, 'r')[self.groupname]
    #     print(list(group.keys()))

    # def test_init_basic(self):
    #     reader = Reader(self.filename, self.groupe)
    #     assert reader.version == '1.1'
    #     assert reader.dformat == 'dense'
    #     assert len(reader.items) == self.nitems
