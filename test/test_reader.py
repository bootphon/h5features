"""Test of the h5features.reader module.

.. note::

    This test assumes the h5features.writer pass it's tests.

"""

import h5py
import pytest
import tempfile

from aux import generate
from aux.utils import remove
import h5features as h5f


class TestReader:
    def setup(self):
        self.filename = 'test.h5'
        self.groupname = 'group'
        self.nitems = 10
        d = generate.full(self.nitems)
        self.data = h5f.Data(d[0], d[1], d[2])

        h5f.Writer(self.filename).write(self.data, self.groupname)

    def teardown(self):
        remove(self.filename)

    def test_init_not_file(self):
        with pytest.raises(IOError) as err:
            h5f.Reader(self.filename + 'spam', self.groupname)
        assert 'not a HDF5 file' in str(err.value)

    def test_init_not_hdf(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(b'This is not a HDF5 file')
        with pytest.raises(IOError) as err:
            h5f.Reader(temp.name, self.groupname)
        assert 'not a HDF5 file' in str(err.value)
        remove(temp.name)

    def test_init_not_group(self):
        with pytest.raises(IOError) as err:
            h5f.Reader(self.filename, self.groupname + 'spam')
        assert 'not a valid group' in str(err.value)

    def test_read_basic(self):
        data = h5f.Reader(self.filename, self.groupname).read()
        assert self.data == data

    def test_groupname_is_none(self):
        data = h5f.Reader(self.filename, None).read()
        assert self.data == data

    # def test_load_index(self):
    #     group = h5py.File(self.filename, 'r')[self.groupname]
    #     print(list(group.keys()))

    def test_init_basic(self):
        reader = h5f.Reader(self.filename, self.groupname)
        assert reader.version == '1.1'
        assert reader.dformat == 'dense'
        assert len(reader.items.data) == self.nitems

    def test_read_time(self):
        reader = h5f.Reader(self.filename, self.groupname)
        assert reader.read(from_time=0, to_time=1) == reader.read()
