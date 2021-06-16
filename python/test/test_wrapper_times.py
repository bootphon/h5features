import numpy as np
import copy
from _h5features import ItemWrapper


def test_update():
    """test the update of times"""
    features = np.ones((100,4))
    begin = np.asarray([0, 1, 2, 3])
    end = np.asarray([1, 2, 3, 4])
    begin = np.asarray(range(0, 100))
    end = begin + 1
    name = "Test"
    properties = {}
    times = ItemWrapper(name, features, begin, end, properties, True)

    copy_true = copy.deepcopy(np.asarray(times.times(), dtype=np.int8))
    copy_false = np.array(times.times(), copy=False)
    np.array(times.times(), copy=False)[0][0] = -1
    assert copy.deepcopy(
        np.asarray(times.times(), dtype=np.int8)).shape == (100, 2)
    assert copy_true[0][0] == 0
    assert copy_false[0][0] == -1
