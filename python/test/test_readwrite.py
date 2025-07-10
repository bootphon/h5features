from pathlib import Path

import numpy as np
import pytest

from h5features import Item, Reader, Version, Writer


@pytest.fixture
def item(rng: np.random.Generator) -> Item:
    array = rng.random((10, 3))
    array[1:3,] = 0
    times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)
    name = "item"
    properties = {"test": True, "test2": [{"a": 1}, {"b": 2}]}
    return Item(name, array, times, properties=properties)


def test_constructor_writer(tmpdir: Path) -> None:
    filename = tmpdir / "test.h5"

    with pytest.raises(TypeError, match="incompatible function arguments."):
        Writer(0, group="test")
    with pytest.raises(TypeError, match="incompatible function arguments."):
        Writer(filename, group=0)
    with pytest.raises(TypeError, match="incompatible function arguments."):
        Writer(filename, group="test", overwrite=False, compress=True, version="2.10")
    with pytest.raises(RuntimeError, match="Unable to open file"):
        Writer(str(tmpdir / "test/test.h5"))

    writer = Writer(filename, group="test", overwrite=False, compress=True, version=Version.v2_0)
    assert writer.version == Version.v2_0
    assert writer.filename == str(Path(filename).resolve())
    assert writer.groupname == "test"


def test_v2_0(item: Item, tmpdir: Path) -> None:
    filename = tmpdir / "test.h5f"
    writer = Writer(filename, group="test", overwrite=False, compress=True, version=Version.v2_0)
    assert writer.version == Version.v2_0
    writer.write(item)
    writer2 = Writer(filename, group="test2", overwrite=False, compress=True, version=Version.v2_0)
    writer2.write(item)
    assert Reader.list_groups(filename) == ["test", "test2"]

    for group in Reader.list_groups(filename):
        reader = Reader(filename, group=group)
        it = reader.read("item")
        assert np.all(item.features() == it.features())
        assert np.all(item.times() == it.times())
        assert item.properties == it.properties
        assert item == it

        it = reader.read("item", ignore_properties=True)
        assert np.all(item.features() == it.features())
        assert np.all(item.times() == it.times())
        assert it.properties == {}
        assert item != it

        it = reader.read_partial("item", start=1, stop=4, ignore_properties=True)
        assert np.all(item.features()[1:4] == it.features())
        assert np.all(item.times()[1:4] == it.times())
        assert item != it
        assert filename == reader.filename
        assert group == reader.groupname
        assert reader.version == Version.v2_0


def test_v1_1(capfd: pytest.CaptureFixture[str], item: Item, tmpdir: Path) -> None:
    filename = tmpdir / "test.h5f"
    Writer(filename, group="test", overwrite=False, compress=True, version=Version.v1_1).write(item)
    assert "version 1.1: ignoring properties" in capfd.readouterr().err
    assert capfd.readouterr().err == ""

    reader = Reader(filename, group="test")
    assert reader.version == Version.v1_1
    it = reader.read("item")
    assert "version 1.1: ignoring properties" in capfd.readouterr().err
    assert it != item
    assert np.all(it.features() == item.features())
    assert np.all(it.times() == item.times())
    assert it.properties == {}


def test_v1_2(item: Item, tmpdir: Path) -> None:
    filename = tmpdir / "test.h5f"
    Writer(filename, group="test", overwrite=False, compress=True, version=Version.v1_2).write(item)
    reader = Reader(filename, group="test")
    assert reader.version == Version.v1_2
    assert reader.read("item") == item


def test_read_all(item: Item, tmpdir: Path) -> None:
    filename = tmpdir / "test.h5f"
    writer = Writer(filename, group="group")
    writer.write(item)
    with pytest.raises(RuntimeError, match="item already exists"):
        writer.write(item)

    item2 = Item("item2", item.features(), item.times())
    writer.write(item2)
    all_items = Reader(filename, group="group").read_all()
    assert len(all_items) == 2
    assert isinstance(all_items, list)
    assert all_items[0] == item
    assert all_items[1] == item2


def test_times1d(tmpdir: Path, rng: np.random.Generator) -> None:
    filename = tmpdir / "file.h5f"
    item = Item(
        name="name",
        features=rng.random((3, 5)),
        times=np.asarray([0, 1, 2]).astype(np.float64),
        properties={"param1": "toto", "param2": 1},
    )
    writer = Writer(filename, group="features")
    writer.write(item)

    reader = Reader(filename, group="features")
    assert reader.items() == ["name"]
    item2 = reader.read("name")
    assert item == item2

    item3 = reader.read_partial("name", 0, 1.5)
    assert item3.features().shape == (2, 5)
    item3 = reader.read_partial("name", 0, 0.5)
    assert item3.features().shape == (1, 5)
