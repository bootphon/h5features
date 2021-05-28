"""Test of the h5features.reader module.

.. note::

    This test assumes the h5features.writer pass it's tests.

"""

import h5py
import os
import numpy as np
import pytest
import tempfile

from .aux import generate
from .aux.utils import remove
import h5features as h5f


def test_read_version(tmpdir):
    with h5py.File(str(tmpdir.join('foo.h5')), 'w') as f:
        g = f.create_group('g')
        g.attrs['version'] = '0.1'
        assert h5f.version.read_version(g) == '0.1'

        g.attrs['version'] = b'0.1'
        assert h5f.version.read_version(g) == '0.1'

        g.attrs['version'] = '125'
        with pytest.raises(IOError) as err:
            h5f.version.read_version(g)
        assert 'version 125 is not supported' in str(err)


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

    data4 = h5f.Reader(filename, groupname).read(from_time=0.2, to_time=0.5)
    assert data4.labels()[0][0] >= 0.2
    assert data4.labels()[0][-1] <= 0.5


@pytest.mark.parametrize('nitems', [4, 5, 7])
def test_simple_properties(tmpdir, nitems):
    filename = str(tmpdir.join('test.h5'))
    items, features, times = generate.full(nitems, 10, 10)
    props = [{'a'*(i+1): i, 'b': True} for i in range(len(items))]
    data = h5f.Data(items, features, times, properties=props)
    h5f.Writer(filename, mode='w').write(data)

    data2 = h5f.Reader(filename).read()
    assert data == data2

    data2 = h5f.Reader(filename).read(from_item=items[1], to_item=items[-2])
    assert data.properties()[1:-1] == data2.properties()
    assert data.items()[1:-1] == data2.items()

    lab1 = data.labels()[1:-1]
    lab2 = data2.labels()
    assert len(lab1) == len(lab2)
    for n in range(len(lab1)):
        assert np.array_equal(lab1[n], lab2[n])

    lab1 = data.features()[1:-1]
    lab2 = data2.features()
    assert len(lab1) == len(lab2)
    for n in range(len(lab1)):
        assert np.array_equal(lab1[n], lab2[n])


P = [{'a': 1.2, 'e': 0, 'c': False},
     {'a': {'f': 0.1}, 'e': 1, 'b': False},
     {'a': 1, 'b': 'two', 'c': True},
     {'a': 1, 'b': 'two', 'd': np.asarray([[1, 1]])}]


@pytest.mark.parametrize('props', [
    [P[0], P[0]],
    [P[0], P[2]],
    [P[1], P[3]], P])
def test_properties(tmpdir, props):
    filename = str(tmpdir.join('test.h5'))
    items, features, times = generate.full(len(props), 10, 10)

    data = h5f.Data(items, features, times, properties=props)
    h5f.Writer(filename, mode='w').write(data)
    data2 = h5f.Reader(filename).read()
    assert data == data2
