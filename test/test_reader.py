"""Test of the h5features.reader module.

.. note::

    This test assumes the h5features.writer pass it's tests.

"""

import numpy as np
import os
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

    def test_init_basic(self):
        reader = h5f.Reader(self.filename, self.groupname)
        assert reader.version == '1.1'
        assert reader.dformat == 'dense'
        assert len(reader.items.data) == self.nitems

    def test_read_time(self):
        reader = h5f.Reader(self.filename, self.groupname)
        assert reader.read(from_time=0, to_time=1) == reader.read()


@pytest.mark.parametrize('dim', [1, 2, 10])
def test_read_tofromtimes(tmpdir, dim):
    filename = os.path.join(str(tmpdir), 'test.h5f')
    groupname = 'group'
    data = generate.full_data(1, dim, 300)
    h5f.Writer(filename, mode='w').write(data, groupname=groupname)

    data2 = h5f.Reader(filename, groupname).read()
    assert data == data2

    data3 = h5f.Reader(filename, groupname).read(from_time=0, to_time=1)
    assert data3 == data

    data4 = h5f.Reader(filename, groupname).read(from_time=0.4, to_time=0.5)
    #print data4.labels()
    assert data4.labels()[0][0] >= 0.4
    assert data4.labels()[0][-1] <= 0.5
