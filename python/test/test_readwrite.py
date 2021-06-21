import os
import numpy as np
import pytest

from h5features import Item, Writer, Reader


@pytest.fixture
def item():
    array = np.random.rand(10, 3)
    array[1:3, ] = 0
    times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)
    name = "item"
    properties = {"test": True}

    return Item(name, array, times, properties=properties)


def test_constructor_writer(tmpdir):
    filename = str(tmpdir / 'test.h5')

    with pytest.raises(TypeError):
        _ = Writer(0, "test", False, True, "2.0")

    with pytest.raises(TypeError):
        _ = Writer(filename, 0, False, True, "2.0")

    with pytest.raises(TypeError):
        _ = Writer(filename, "test", "test", True, "2.0")

    with pytest.raises(TypeError):
        _ = Writer(filename, "test", False, "test", "2.0")

    with pytest.raises(KeyError):
        _ = Writer(filename, "test", False, True, "2.10")

    with pytest.raises(FileNotFoundError):
        _ = Writer(str(tmpdir / 'test/test.h5'), "test", False, True, "2.0")

    with Writer(filename, "test", False, True, "2.0") as writer:
        assert writer.version == "2.0"
        assert writer.filename == os.path.abspath(filename)
        assert writer.groupname == "test"


def test_v2_0(item, tmpdir):
    filename = str(tmpdir / 'test.h5f')
    with Writer(filename, "test", False, True, "2.0") as writer:
        assert writer.version == '2.0'
        writer.write(item)
    with Writer(filename, "test2", False, True, "2.0") as writer2:
        writer2.write(item)

    assert Reader.list_groups(filename) == ["test", "test2"]

    for group in Reader.list_groups(filename):
        with Reader(filename, group) as reader:
            it = reader.read('item')
            assert np.all(item.features == it.features)
            assert np.all(item.times == it.times)
            assert item.properties == it.properties
            assert item == it

            it = reader.read('item', ignore_properties=True)
            assert np.all(item.features == it.features)
            assert np.all(item.times == it.times)
            assert it.properties == {}
            assert not item == it
            assert item != it

            it = reader.read('item', start=1, stop=4, ignore_properties=True)
            assert np.all(item.features[1:4] == it.features)
            assert np.all(item.times[1:4] == it.times)
            assert not item == it
            assert item != it
            assert filename == reader.filename
            assert group == reader.groupname
            assert reader.version == "2.0"


def test_v1_1(capsys, item, tmpdir):
    filename = str(tmpdir / 'test.h5f')
    Writer(filename, "test", False, True, "1.1").write(item)
    assert 'version 1.1: ignoring properties' in capsys.readouterr().err

    with Reader(filename, "test") as reader:
        assert reader.version == "1.1"
        it = reader.read('item')
        assert 'version 1.1: ignoring properties' in capsys.readouterr().err
        assert it != item
        assert np.all(it.features == item.features)
        assert np.all(it.times == item.times)
        assert it.properties == {}


def test_v1_2(item, tmpdir):
    filename = str(tmpdir / 'test.h5f')
    Writer(filename, "test", False, True, "1.2").write(item)

    with Reader(filename, 'test') as reader:
        assert reader.version == "1.2"
        assert reader.read('item') == item


def test_read_all(item, tmpdir):
    filename = str(tmpdir / 'test.h5f')
    with Writer(filename, 'group') as writer:
        writer.write(item)

        with pytest.raises(RuntimeError) as err:
            writer.write(item)
            assert 'item already existing' in str(err)

        item2 = Item('item2', item.features, item.times)
        writer.write(item2)

    all_items = Reader(filename, 'group').read_all()
    assert len(all_items) == 2
    assert isinstance(all_items, list)
    assert all_items[0] == item
    assert all_items[1] == item2
