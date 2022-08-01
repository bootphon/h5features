import pathlib
import numpy as np
import pytest

import h5features as h5f


@pytest.fixture
def item1():
    return h5f.Item(
        'item1',
        np.random.rand(10, 3),
        np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64),
        {'prop1': False, 'prop2': ['a', 'b', 'c']})


@pytest.fixture
def item2():
    return h5f.Item(
        'item2',
        np.random.rand(15, 3),
        np.vstack((np.arange(15), np.arange(15) + 0.1)).T.astype(np.float64),
        {'prop1': True, 'prop2': ['a', 'b', 'c']})


@pytest.fixture
def h5file(tmpdir, item1, item2):
    filename = str(tmpdir / 'test.h5f')
    with h5f.Writer(filename, 'features') as writer:
        writer.write(item1)
        writer.write(item2)
    with h5f.Writer(filename, 'features2') as writer:
        writer.write(item1)
    return filename


def test_list_group(h5file):
    h5f.Reader.list_groups(h5file) == ['features', 'features2']
    h5f.Reader.list_groups(pathlib.Path(h5file)) == ['features', 'features2']

    with pytest.raises(RuntimeError) as err:
        h5f.Reader.list_groups(h5file + '.foo')
    assert 'Unable to open file' in str(err.value)

    with pytest.raises(RuntimeError) as err:
        h5f.Reader.list_groups(__file__)
    assert 'Not an HDF5 file' in str(err.value)


def test_ctor(h5file):
    with pytest.raises(TypeError) as err:
        h5f.Reader(12, 'features')
    assert 'incompatible constructor arguments' in str(err.value)

    with pytest.raises(TypeError) as err:
        h5f.Reader('spam', ['features'])
    assert 'incompatible constructor arguments' in str(err.value)

    with pytest.raises(RuntimeError) as err:
        h5f.Reader(pathlib.Path(h5file))
    assert 'group must be specified' in str(err.value)

    with h5f.Reader(pathlib.Path(h5file), 'features') as reader:
        assert reader.items() == ['item1', 'item2']
        assert reader.version == '2.0'
        assert reader.filename == h5file
        assert reader.groupname == 'features'


def test_read_all(h5file, item1, item2):
    assert h5f.Reader(h5file, 'features').read_all() == [item1, item2]
    assert h5f.Reader(h5file, 'features2').read_all() == [item1]


def test_read(h5file, item1):
    reader = h5f.Reader(h5file, 'features')

    with pytest.raises(RuntimeError) as err:
        reader.read('spam')
    assert "object 'spam' does not exist" in str(err)

    with pytest.raises(TypeError):
        reader.read(12)

    assert reader.read('item1') == item1
    assert reader.read('item2') != item1

    item3 = reader.read('item1', ignore_properties=True)
    assert item3 != item1
    assert item3.properties == {}
    assert np.all(item3.features() == item1.features())
    assert np.all(item3.times() == item1.times())


def test_read_partial(h5file, item1):
    reader = h5f.Reader(h5file, 'features')

    with pytest.raises(TypeError) as err:
        reader.read('spam', start=None, stop=2)
    assert 'arguments must be both None or float' in str(err.value)

    with pytest.raises(TypeError) as err:
        reader.read('spam', start='a', stop=None)
    assert 'arguments must be both None or float' in str(err.value)

    assert reader.read('item1', start=None, stop=None) == item1
    assert reader.read('item1', start=0, stop=100) == item1

    with pytest.raises(TypeError) as err:
        reader.read('item1', start='abc', stop=100)
    assert 'could not convert string to float' in str(err.value)

    item2 = reader.read('item1', start=0, stop=2)
    item3 = reader.read('item1', start=0, stop=2.5)
    assert item2.features().shape == (2, 3)
    assert np.all(item2.times() == np.asarray([[0, 1], [1, 2]]))
    assert item2 == item3
