from pathlib import Path

import numpy as np

from h5features import Item, Reader, Version, Writer


def test_read_write(tmpdir: Path) -> None:
    filename = str(tmpdir / "test.h5f")

    array = np.ones((9, 1))
    array[1:3,] = 0
    times = np.vstack((np.arange(9), np.arange(9) + 1)).T.astype(np.float64)
    props = {
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
                "dict": {
                    "int ": 1,
                    "double": 1.0,
                    "bool": True,
                    "string": "str",
                    "list of string": ["str1", "str2"],
                    "list of int": [1, 2, 3],
                    "list of double": [1.0, 2.0, 3.0],
                },
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
    item1 = Item("item1", array, times, props)
    item2 = Item("item2", array, times, {})

    writer = Writer(filename, group="group", overwrite=False, compress=True, version=Version.v2_0)
    assert writer.filename == filename
    assert writer.groupname == "group"
    writer.write(item1)
    writer.write(item2)
    assert Reader.list_groups(filename) == ["group"]

    reader = Reader(filename, group="group")
    assert reader.items() == ["item1", "item2"]

    it = reader.read(reader.items()[0])
    assert np.all(array == np.array(it.features()))
    assert item1 == it
    assert it.properties == item1.properties

    it = reader.read_partial(reader.items()[0], np.float64(1), np.float64(3))
    assert np.all(array[1:3, :] == np.array(it.features()))
    assert np.all(array[1:3, :] == np.zeros((2, 1000)))
    assert np.all(array[[0, 3, 4, 5, 6, 7, 8]] == np.ones((7, 1)))
    assert item1 != it
    assert filename == reader.filename
    assert reader.groupname == "group"
    assert reader.version == Version.v2_0

    all_items = reader.read_all()
    assert len(all_items) == 2
    assert isinstance(all_items, list)
    assert all_items[0] == item1
    assert all_items[1] == item2
