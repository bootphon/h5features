import numpy as np
from _h5features import ItemWrapper


def test_item():
    features = np.random.rand(100, 4)
    begin = np.asarray([0, 1, 2, 3])
    end = np.asarray([1, 2, 3, 4])
    begin = np.asarray([i for i in range(0, 100)])
    end = np.asarray([i for i in range(1, 101)])

    item = ItemWrapper('item', features, begin, end, {}, True)

    assert item.name() == 'item'
    assert item.dim() == 4
    assert item.size() == 100

    meti = ItemWrapper('item', features, begin, end, {}, True)
    assert item == meti
    assert np.all(features == np.array(item.features(), copy=False))
