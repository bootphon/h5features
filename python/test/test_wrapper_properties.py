import numpy as np
import pytest
from _h5features import ItemWrapper


@pytest.fixture
def item():
    features = np.ones((2, 4))
    begin = np.asarray([0, 1])
    end = begin + 1
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

    return ItemWrapper(name, features, begin, end, properties, True)


def test_properties(item):
    props = item.properties()
    assert props.get("int", None) is not None
    assert props.get("double", None) is not None
    assert props.get("bool", None) is not None
    assert props.get("string", None) is not None
    assert props.get("list of int", None) is not None
    assert props.get("list of double", None) is not None
    assert props.get("list of string", None) is not None
    assert props.get("dict", None) is not None
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

    assert item.properties_contains("int")
    assert not item.properties_contains("tni")
    item.properties_erase("int")
    assert not item.properties_contains("int")
    item.properties_set("int", {
        "int ": 1,
        "double": 1.,
        "bool": True,
        "string": "str",
        "list of string": ["str1", "str2"],
        "list of int": [1, 2, 3],
        "list of double": [1., 2., 3.]})
    assert item.properties_contains("int")
    props = item.properties()
    assert props["int"] == {
        "int ": 1,
        "double": 1.,
        "bool": True,
        "string": "str",
        "list of string": ["str1", "str2"],
        "list of int": [1, 2, 3],
        "list of double": [1., 2., 3.]}

    item.properties_set("test", "test")
    assert item.properties_contains("test")

    props = item.properties()
    assert props["test"] == "test"

    item.properties_set("test", "tset")
    props = item.properties()
    assert props["test"] == "tset"
    assert item.properties()["test"] == "tset"
    assert item.has_properties()


def test_no_properties():
    features = np.ones((1, 4))
    begin = np.asarray([0])
    end = begin + 1
    name = "Test"
    properties = {}
    item = ItemWrapper(name, features, begin, end, properties, True)
    assert not item.has_properties()
