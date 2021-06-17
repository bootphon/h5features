import numpy as np

from _h5features import ItemWrapper, WriterWrapper, ReaderWrapper, read_group


def test_read_write(tmpdir):
    filename = str(tmpdir / 'test')

    array = np.ones((9, 1))
    array[1:3, ] = 0
    begin = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float64)
    end = begin + 1
    item1 = ItemWrapper('item1', array, begin, end, {}, True)
    item2 = ItemWrapper('item2', array, begin, end, {}, True)

    writer = WriterWrapper(
        filename, 'group', False, True, WriterWrapper.version.v2_0)
    assert writer.filename() == filename
    assert writer.groupname() == 'group'
    writer.write(item1)
    writer.write(item2)
    assert read_group(filename) == ['group']

    reader = ReaderWrapper(filename, 'group')
    assert reader.items() == ['item1', 'item2']

    it = reader.read(reader.items()[0], False)
    assert np.all(array == np.array(it.features()))
    assert item1 == it

    it = reader.read_btw(
        reader.items()[0], np.float64(1), np.float64(3), False)
    assert np.all(array[1:3, :] == np.array(it.features()))
    assert np.all(array[1:3, :] == np.zeros((2, 1000)))
    assert np.all(array[[0, 3, 4, 5, 6, 7, 8]] == np.ones((7, 1)))
    assert not item1 == it
    assert item1 != it
    assert filename == reader.filename()
    assert reader.groupname() == 'group'
    assert reader.version().name == 'v2_0'

    all_items = reader.read_all(False)
    assert len(all_items) == 2
    assert isinstance(all_items, list)
    assert all_items[0] == item1
    assert all_items[1] == item2
