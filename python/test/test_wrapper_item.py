from _h5features import ItemWrapper
from unittest import TestCase
import numpy as np

class ItemTests(TestCase):
    """Tests on Items"""

    def test_item(self):
        features = np.random.rand(100,4)
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        begin = np.asarray([i for i in range(0, 100)])
        end = np.asarray([i for i in range(1, 101)])
        name = "Test"
        properties = {}
        item = ItemWrapper(name, features, begin, end, properties, True)
        assert item.name() == "Test"
        assert item.dim() == 4
        assert item.size() == 100
        meti = ItemWrapper(name, features, begin, end, properties, True)
        self.assertEqual(item, meti)
        self.assertTrue(np.all(features  == np.array(item.features(), copy=False)))
