import os
import numpy as np
import pytest

from _h5features import ItemWrapper, WriterWrapper, ReaderWrapper, read_group


def test_reading_writting(tmpdir):
    filename = str(tmpdir / 'test')

    array = np.ones((9, 1))
    array[1:3, ] = 0
    begin = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float64)
    end = begin + 1
    name = "Test"
    item = ItemWrapper(name, array, begin, end, {}, True)

    writer = WriterWrapper(
        filename, "test", False, True, WriterWrapper.version.v2_0)
    writer.write(item)
    assert read_group(filename) == ['test']

    reader = ReaderWrapper(filename, "test")
    assert reader.items()[0] == "Test"

    it = reader.read(reader.items()[0], False)
    assert np.all(array == np.array(it.features()))
    assert item == it

    it = reader.read_btw(
        reader.items()[0], np.float64(1), np.float64(3), False)
    assert np.all(array[1:3, :] == np.array(it.features()))
    assert np.all(array[1:3, :] == np.zeros((2, 1000)))
    assert np.all(array[[0, 3, 4, 5, 6, 7, 8]] == np.ones((7, 1)))
    assert not item == it
    assert item != it
    assert filename == reader.filename()
    assert reader.groupname() == "test"
    assert reader.get_version().name == "v2_0"
