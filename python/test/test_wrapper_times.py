import numpy as np
from _h5features import ItemWrapper


def test_times():
    """test access to times by reference"""
    features = np.ones((5, 2))
    times = np.vstack((np.arange(5), np.arange(5) + 1)).T.astype(np.float64)
    name = "Test"
    properties = {}
    times = ItemWrapper(name, features, times, properties, True)

    copy_true = np.array(times.times(), dtype=np.int8, copy=True)
    copy_false = np.array(times.times(), copy=False)
    np.array(times.times(), copy=False)[0][0] = -1
    assert np.array(times.times(), dtype=np.int8, copy=True).shape == (5, 2)
    assert copy_true[0][0] == 0
    assert copy_false[0][0] == -1
