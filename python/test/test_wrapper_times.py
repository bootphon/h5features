from _h5features import ItemWrapper
from unittest import TestCase
import numpy as np
import copy
class TimesTests(TestCase):
    """Tests on class Times"""

    def test_update(self):
        """test the update of times"""
        features = np.ones((100,4))
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        begin = np.asarray([i for i in range(0, 100)])
        end = np.asarray([i for i in range(1, 101)])
        name = "Test"
        properties = {}
        times = ItemWrapper(name, features, begin, end, properties, True)
        copy_true = copy.deepcopy(np.asarray(times.times(), dtype=np.int8))
        copy_false = np.array(times.times(), copy=False)
        np.array(times.times(), copy=False)[0][0] = -1
        assert copy.deepcopy(np.asarray(times.times(), dtype=np.int8)).shape == (100, 2)
        assert copy_true[0][0] == 0
        assert copy_false[0][0] == -1
