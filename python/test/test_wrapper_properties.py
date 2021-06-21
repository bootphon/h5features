import numpy as np
import pytest
from _h5features import ItemWrapper


@pytest.fixture
def item():
    features = np.ones((2, 4))
    times = np.vstack((np.arange(2), np.arange(2) + 1)).T.astype(np.float64)
    name = "Test"
    properties = {
        "int": 1,
        "double": 1.,
        "bool": True,
        "string": "str",
        "list of string": ["str1", "str2"],
        "list of int": [1, 2, 3],
        "list of double": [1., 2., 3.],
        "dict": {
            "int ": 1,
            "double": 1.,
            "bool": True,
            "string": "str",
            "list of string": ["str1", "str2"],
            "list of int": [1, 2, 3],
            "list of double": [1., 2., 3.]}}

    return ItemWrapper(name, features, times, properties, True)


def test_properties(item):
    props = item.properties()
    assert props["int"] == 1
    assert props["bool"]
    assert props["double"] == 1.
    assert props["string"] == "str"
    assert props["list of string"] == ["str1", "str2"]
    assert props["list of int"] == [1, 2, 3]
    assert props["list of double"] == [1., 2., 3.]
    assert props["dict"] == {
        "int ": 1,
        "double": 1.,
        "bool": True,
        "string": "str",
        "list of string": ["str1", "str2"],
        "list of int": [1, 2, 3],
        "list of double": [1., 2., 3.]}

    assert item.properties() != {}


def test_no_properties():
    features = np.ones((1, 4))
    times = np.asarray([0]).reshape(-1, 1)
    name = "Test"
    properties = {}
    item = ItemWrapper(name, features, times, properties, True)
    assert item.properties() == {}
