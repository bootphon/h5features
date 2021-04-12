import sys
from h5features import Item
from unittest import TestCase
import psutil
import numpy as np
import copy
class TimesTests(TestCase):
    """Tests on class Times"""
    
    def test_update(self):
        """test the update of times"""
        features = np.ones((100,4))
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        name = "Test"
        properties = {}
        times = Item(name, features, begin, end, properties, True).times()
        copy_true = copy.deepcopy(np.array(times, dtype=np.int8))
        copy_false = np.array(times, copy=False)
        np.array(times, copy=False)[0][0] = -1
        assert np.array(times, copy=True).shape == (2,4)
        assert copy_true[0][0] == 0
        assert copy_false[0][0] == -1
