import numpy as np
from _h5features import ItemWrapper


def test_item():
    features = np.random.rand(10, 3)
    times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)
    props = {'pi': 3.14}
    item = ItemWrapper('item', features, times, props, True)

    assert item.name() == 'item'
    assert item.dim() == 3
    assert item.size() == 10
    assert np.all(features == item.features())
    assert np.all(times == item.times())
    assert item.properties() == props

    item2 = ItemWrapper('item', features, times, props, True)
    assert item == item2
