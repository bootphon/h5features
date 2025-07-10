import numpy as np

from h5features import Item


def test_item(rng: np.random.Generator) -> None:
    features = rng.random((10, 3))
    times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)
    props = {"pi": 3.14}
    item = Item("item", features, times, props)

    assert item.name == "item"
    assert item.dim == 3
    assert item.size == 10
    assert np.all(features == item.features())
    assert np.all(times == item.times())
    assert item.properties == props

    item2 = Item("item", features, times, props)
    assert item == item2
