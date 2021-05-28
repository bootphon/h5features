"""Test of the h5features.writer module."""

import h5py
import os
import pytest
import h5features as h5f

from .aux import generate
from .aux.utils import remove, assert_raise
from h5features.writer import Writer
from h5features.properties import read_properties
from h5features.data import Data


def test_create_a_file():
    name = 'azecqgxqsdqxws.eztcqezxf'
    assert not os.path.exists(name)
    with Writer(name):
        pass
    assert os.path.exists(name)
    remove(name)


def test_bas_version():
    with pytest.raises(IOError) as err:
        Writer('a.b', version='a')
    assert 'version a is not supported' in str(err)


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

    def test_bad_mode(self):
        with pytest.raises(IOError):
            Writer(self.filename, mode='r')

    def test_chunk_good(self):
        args = ['auto', 0.008, 0.01, 12, 1e30]
        for arg in args:
            Writer(self.filename, chunk_size=arg)

    def test_chunk_below(self):
        args = [0.008-1e-2, .0001, 0, -1e30]
        msg = "chunk size is below 8 Ko"
        for arg in args:
            with pytest.raises(IOError) as err:
                Writer(self.filename, chunk_size=arg)
            assert msg in str(err.value)

    def test_chunk_bad(self):
        args = ['spam', [1, 2, 3]]
        msg = "chunk size must be 'auto' or a number"
        for arg in args:
            with pytest.raises(IOError) as err:
                Writer(self.filename, chunk_size=arg)
            assert msg in str(err.value)


class TestWriteAppendable:
    """Test of the _appendable() method.

    This functionnality is removed since h5features-1.2 so this test
    is deprecated...

    """

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
    #         w.is_appendable_to(self.g, None)


class TestWrite:
    """test the Writer.write method"""
    def setup(self):
        self.filename = 'test.h5'
        remove(self.filename)

        self.group = 'group'

    def teardown(self):
        remove(self.filename)

    @pytest.mark.parametrize('dim', [1, 2, 10])
    def test_no_append(self, dim):
        h5f.Writer(self.filename).write(
            generate.full_data(10, dim=dim), self.group, append=False)

        with h5py.File(self.filename, 'r') as f:
            g = f[self.group]
            assert len(g['items'][...]) == 10
            assert not all([(h == 0).all() for h in g['features'][...]])

    @pytest.mark.parametrize('dim', [1, 2, 10])
    def test_append(self, dim):
        data1 = generate.full_data(
            10, dim=dim, properties=True)
        h5f.Writer(self.filename).write(data1, self.group, append=False)

        data2 = generate.full_data(
            10, dim=dim, items_root='items_bis', properties=True)
        h5f.Writer(self.filename).write(data2, self.group, append=True)

        # cannot append to incompatible versions
        with pytest.raises(IOError) as err:
            h5f.Writer(self.filename, version='0.1').write(
                data2, self.group, append=True)
        assert 'versions are different' in str(err)

        with h5py.File(self.filename, 'r') as f:
            g = f[self.group]
            items = g['items'][...].astype(str)
            assert len(items) == 20
            assert all('bis' not in i for i in items[:10])
            assert all('bis' in i for i in items[10:])
            assert not all([(feat == 0).all() for feat in g['features'][...]])
            assert len(read_properties(g)) == 20


@pytest.mark.parametrize('compression', [None, 'gzip', 'lzf'])
def test_compression(tmpdir, compression):
    filename = str(tmpdir.join('test.h5'))
    data = generate.full_data(10, dim=2)
    h5f.Writer(filename, compression=compression).write(data, 'group')
    assert data == h5f.Reader(filename, groupname='group').read()


def test_compression_size(tmpdir):
    data = generate.full_data(10, dim=2)
    sizes = []
    for i in range(10):
        filename = str(tmpdir.join('test.h5.' + str(i)))
        h5f.Writer(filename, compression=i).write(data, 'group')
        sizes.append(os.path.getsize(filename))

    assert sizes[::-1] == sorted(sizes)


@pytest.mark.parametrize('compression', ['zip', 'spam', 1.0, -1, 15])
def test_compression_bad(tmpdir, compression):
    filename = str(tmpdir.join('test.h5'))
    with pytest.raises(IOError):
        h5f.Writer(filename, compression=compression)
