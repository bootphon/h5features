import sys
from pyh5features import Item
from unittest import TestCase
import psutil
import numpy as np

class ItemTests(TestCase):
    """Tests on Items"""
   
    def test_item(self):
        features = np.ones((100,4))
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        name = "Test"
        properties = {}
        item = Item(name, features, begin, end, properties, True)
        assert item.name() == "Test"
        assert item.dim() == 100
        assert item.size() == 4
        meti = Item(name, features, begin, end, properties, True)
        self.assertEqual(item, meti)