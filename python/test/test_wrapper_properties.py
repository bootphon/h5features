import numpy as np
import pytest

from h5features import Item


@pytest.fixture
def item() -> Item:
    features = np.ones((2, 4))
    times = np.vstack((np.arange(2), np.arange(2) + 1)).T.astype(np.float64)
    name = "Test"
    properties = {
        "int": 1,
        "double": 1.0,
        "bool": True,
        "string": "str",
        "list of string": ["str1", "str2"],
        "list of int": [1, 2, 3],
        "list of double": [1.0, 2.0, 3.0],
        "list of properties": [
            {
                "int ": 1,
                "double": 1.0,
                "bool": True,
                "string": "str",
                "list of string": ["str1", "str2"],
                "list of int": [1, 2, 3],
                "list of double": [1.0, 2.0, 3.0],
            },
            {
                "int ": 1,
                "double": 1.0,
                "bool": True,
                "string": "str",
                "list of string": ["str1", "str2"],
                "list of int": [1, 2, 3],
                "list of double": [1.0, 2.0, 3.0],
            },
        ],
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

    return Item(name, features, times, properties)


def test_properties(item: Item) -> None:
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
    assert props["list of properties"] == [
        {
            "int ": 1,
            "double": 1.0,
            "bool": True,
            "string": "str",
            "list of string": ["str1", "str2"],
            "list of int": [1, 2, 3],
            "list of double": [1.0, 2.0, 3.0],
        },
        {
            "int ": 1,
            "double": 1.0,
            "bool": True,
            "string": "str",
            "list of string": ["str1", "str2"],
            "list of int": [1, 2, 3],
            "list of double": [1.0, 2.0, 3.0],
        },
    ]

    assert item.properties != {}


def test_no_properties() -> None:
    features = np.ones((1, 4))
    times = np.asarray([0]).reshape(-1, 1)
    name = "Test"
    properties = {}
    item = Item(name, features, times, properties)
    assert item.properties == {}
