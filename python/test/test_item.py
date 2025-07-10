import numpy as np
import pytest

from h5features import Item


@pytest.fixture
def item() -> Item:
    features = np.arange(40).reshape((10, 4)).astype(np.float64)
    times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)
    return Item("item", features, times, properties={"spam": "spam a lot"})


def test_basic(item: Item) -> None:
    assert item.name == "item"
    assert item.size == 10
    assert item.dim == 4
    assert np.all(item.features() == np.arange(40).reshape((10, 4)).astype(np.float64))
    assert item.times()[:, 0].tolist() == list(range(10))
    assert item.properties == {"spam": "spam a lot"}


def test_name(item: Item) -> None:
    # name must be a string
    with pytest.raises(TypeError):
        Item(10, item.features, item.times)


def test_times(item: Item) -> None:
    # helper fonction to generate an item with custom times
    def make_item(times: np.ndarray) -> Item:
        return Item(item.name, item.features(), times)

    #  error if times is not a float64 numpy array
    with pytest.raises(TypeError):
        make_item([1, 2, 3])
    with pytest.raises(TypeError):
        make_item("abc")

    # times as 1D array
    item2 = make_item(item.times()[:, 0].T)
    assert item2.times().shape == (10, 1)
    assert item2.times().flatten().tolist() == list(range(10))

    # test error if features is a list
    with pytest.raises(TypeError):
        Item(item.name, item.features().tolist(), item.times())

    # test error if properties are not in dict
    with pytest.raises(TypeError):
        Item(item.name, item.features(), item.times(), properties=[1, 2, 3])


def test_casting(item: Item) -> None:
    # test if features are cast to float64
    item2 = Item(item.name, item.features().astype(np.int8), item.times())
    assert item2.features().dtype == np.float64


def test_properties(rng: np.random.Generator) -> None:
    """test properties"""
    features = np.ones((10, 4), dtype=np.float64)
    times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)

    # a dict of dict
    properties = {
        "int": 1,
        "double": 1.0,
        "bool": True,
        "string": "str",
        "list of string": ["str1", "str2"],
        "list of int": [1, 2, 3],
        "list of double": [1.0, 2.0, 3.0],
        "dict": {
            "int ": 1,
            "double": 1.0,
            "bool": True,
            "string": "str",
            "list of string": ["str1", "str2"],
            "list of int": [1, 2, 3],
            "list of double": [1.0, 2.0, 3.0],
        },
    }
    name = "test"
    item = Item(name, features, times, properties=properties)
    props = item.properties
    assert props["int"] == 1
    assert props["bool"]
    assert props["double"] == 1.0
    assert props["string"] == "str"
    assert props["list of string"] == ["str1", "str2"]
    assert props["list of int"] == [1, 2, 3]
    assert props["list of double"] == [1.0, 2.0, 3.0]
    assert props["dict"] == {
        "int ": 1,
        "double": 1.0,
        "bool": True,
        "string": "str",
        "list of string": ["str1", "str2"],
        "list of int": [1, 2, 3],
        "list of double": [1.0, 2.0, 3.0],
    }

    # test bad key type
    properties = {2: 1, "double": 1.0, "bool": True}
    with pytest.raises(RuntimeError):
        item = Item(name, features, times, properties=properties)

    properties = {"int": 1, "list of double": [1.0, 2.0, 3.0], "dict": {2: 1, "double": 1.0}}
    with pytest.raises(RuntimeError):
        item = Item(name, features, times, properties=properties)

    properties = {"not valid": ["a", 1]}
    with pytest.raises(RuntimeError):
        item = Item(name, features, times, properties=properties)

    # works with reshape : needs to have an information about dims in properties
    properties = {"not valid": rng.random((5, 2))}
    with pytest.raises(ValueError, match="Unsupported Python type for h5features::properties"):
        item = Item(name, features, times, properties=properties)


def test_strides() -> None:
    features = np.arange(20).astype(np.float64).reshape((10, 2))
    times = np.arange(10).astype(np.float64)
    item = Item("item", features[::2], times[::2])
    assert np.all(item.features() == features[::2])
    assert np.all(item.times().flatten() == times[::2].flatten())


def test_build_by_copy(rng: np.random.Generator) -> None:
    features = rng.random((10, 2))
    times = np.arange(10).astype(np.float64)
    item = Item("item", features, times)

    features_copy = np.copy(features)
    features[:] = 0
    assert np.all(item.features() == features_copy)

    times_copy = np.copy(times)
    times[:] = 0
    assert np.all(item.times().flatten() == times_copy.flatten())
