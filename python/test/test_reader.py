from pathlib import Path

import numpy as np
import pytest

from h5features import Item, Reader, Version, Writer


@pytest.fixture
def item1(rng: np.random.Generator) -> Item:
    return Item(
        "item1",
        rng.random((10, 3)),
        np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64),
        {"prop1": False, "prop2": ["a", "b", "c"]},
    )


@pytest.fixture
def item2(rng: np.random.Generator) -> Item:
    return Item(
        "item2",
        rng.random((15, 3)),
        np.vstack((np.arange(15), np.arange(15) + 0.1)).T.astype(np.float64),
        {"prop1": True, "prop2": ["a", "b", "c"]},
    )


@pytest.fixture
def h5file(tmpdir: Path, item1: Item, item2: Item) -> str:
    filename = str(tmpdir / "test.h5f")
    writer = Writer(filename, group="features")
    writer.write(item1)
    writer.write(item2)
    writer = Writer(filename, group="features2")
    writer.write(item1)
    return filename


def test_list_group(h5file: str) -> None:
    assert Reader.list_groups(h5file) == ["features", "features2"]
    assert Reader.list_groups(Path(h5file)) == ["features", "features2"]

    with pytest.raises(RuntimeError, match="Unable to open file"):
        Reader.list_groups(h5file + ".foo")
    with pytest.raises(RuntimeError, match="Not an HDF5 file"):
        Reader.list_groups(__file__)


def test_ctor(h5file: str) -> None:
    with pytest.raises(TypeError, match="incompatible function arguments."):
        Reader(12, group="features")
    with pytest.raises(TypeError, match="incompatible function arguments."):
        Reader("spam", group=["features"])

    reader = Reader(Path(h5file), group="features")
    assert reader.items() == ["item1", "item2"]
    assert reader.version == Version.v2_0
    assert reader.filename == h5file
    assert reader.groupname == "features"


def test_read_all(h5file: Path, item1: Item, item2: Item) -> None:
    assert Reader(h5file, group="features").read_all() == [item1, item2]
    assert Reader(h5file, group="features2").read_all() == [item1]


def test_read(h5file: Path, item1: Item) -> None:
    reader = Reader(h5file, group="features")
    with pytest.raises(RuntimeError, match="object 'spam' does not exist"):
        reader.read("spam")
    with pytest.raises(TypeError):
        reader.read(12)

    assert reader.read("item1") == item1
    assert reader.read("item2") != item1

    item3 = reader.read("item1", ignore_properties=True)
    assert item3 != item1
    assert item3.properties == {}
    assert np.all(item3.features() == item1.features())
    assert np.all(item3.times() == item1.times())


def test_read_partial(h5file: Path, item1: Item) -> None:
    reader = Reader(h5file, group="features")

    with pytest.raises(TypeError, match="incompatible function arguments."):
        reader.read_partial("spam", start=None, stop=2)
    with pytest.raises(TypeError, match="incompatible function arguments."):
        reader.read_partial("spam", start="a", stop=None)

    assert reader.read("item1") == item1
    assert reader.read_partial("item1", start=0, stop=100) == item1

    with pytest.raises(TypeError, match="incompatible function arguments."):
        reader.read_partial("item1", start="abc", stop=100)

    item2 = reader.read_partial("item1", start=0, stop=2)
    item3 = reader.read_partial("item1", start=0, stop=2.5)
    assert item2.features().shape == (2, 3)
    assert np.all(item2.times() == np.asarray([[0, 1], [1, 2]]))
    assert item2 == item3
