from _h5features import ItemWrapper
from unittest import TestCase
import numpy as np
from copy import deepcopy

class FeaturesTests(TestCase):
    """Tests on features"""
    def test_data_equality(self):
        array = np.asarray([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]], dtype=np.float64)
        begin = np.asarray([0, 1, 2])
        end = np.asarray([1, 2, 3])
        begin = np.asarray([i for i in range(0, 4)])
        end = np.asarray([i for i in range(1, 5)])
        name = "Test"
        properties = {}
        item = ItemWrapper(name, array, begin, end, properties, True)
        features = item.features()
        assert np.all(array == np.array(features))

    def test_update_from_init(self):
        """ test if np.array is copied or passed by reference to c++ """
        array = np.ones((1000000, 4))
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        begin = np.asarray([i for i in range(0, 1000000)])
        end  = np.asarray([i for i in range(1, 1000000+1)])
        name = "Test"
        properties = {}
        item = ItemWrapper(name, array, begin, end, properties, True)
        features = item.features()
        copy = np.array(features, copy=False)
        array[0, 0] = 0
        assert array[0, 0] == 0
        assert copy[0, 0] != 0
        del item


    def test_in_equality(self):
        """ test numpy equality"""
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        begin = np.asarray([i for i in range(0, 1000000)])
        end  = np.asarray([i for i in range(1, 1000000+1)])
        # name = "Test"
        properties = {}
        a = ItemWrapper("a", np.ones((1000000, 4), dtype=np.float64), begin, end, properties, True)
        b = ItemWrapper("b", np.ones((1000000, 4) ,dtype=np.float64), begin, end, properties, True)
        c = ItemWrapper("c", np.zeros((1000000, 4) ,dtype=np.float64), begin, end, properties, True)
        f1 = np.array(a.features(), copy=False)
        f2 = np.array(b.features(), copy=False)
        f3 = np.array(c.features(), copy=False)
        # f1 = np.array(np.ones((100000, 4)), copy=False)
        # f2 = np.array(np.ones((100000, 4)), copy=False)
        # f3 = np.array(np.zeros((100000, 4)), copy=False)
        assert np.all(f1 == f2)
        assert np.all(f1 == np.ones((1000000, 4)))
        assert np.all(1 != f3)
        assert np.all(f2 != f3)
        del a
        del b
        del c
        del f1
        del f2
        del f3

    def test_copy_true(self):
        """ this method test the updates of severals call of features.data()
         when udpdate the numpy array with copy=true"""
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        begin = np.asarray([i for i in range(0, 1000000)])
        end  = np.asarray([i for i in range(1, 1000000+1)])
        feats = np.ones((1000000, 4), dtype=np.float64)
        # f2 = np.array(feats, copy=True)
        name = "Test"
        properties = {}
        features = ItemWrapper(name, feats, begin, end, properties, True)
        first_copy = deepcopy(np.asarray(features.features()))
        second_copy = deepcopy(np.asarray(features.features()))
        third_copy = np.array(features.features(), copy=False)
        first_copy[0, 0] = 0
        third_copy[1, 0] = 0
        # test if the array have changed after it-s update
        assert first_copy[0, 0] == 0
        # test if first_copy change after thrid update
        assert first_copy[1, 0] == 1
        # test if second copy change after other update
        assert second_copy[0, 0] == 1
        assert second_copy[1, 0] == 1
        # test if third copy change after other and it's updates
        assert third_copy[0, 0] == 1
        assert third_copy[1, 0] == 0

    def test_copy_false(self):
        """ this method test the updates of severals call of features()
         when udpdate the numpy array with copy=false"""
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        begin = np.asarray([i for i in range(0, 1000000)])
        end  = np.asarray([i for i in range(1, 1000000+1)])
        name = "Test"
        properties = {}
        features = ItemWrapper(name, np.ones((1000000, 4)), begin, end, properties, True)
        first_copy = np.array(features.features(), copy=False)
        fs_copy = np.array(features.features(), copy=False)
        sd_copy = deepcopy(np.asarray(features.features()))
        first_copy[0, 0] = 0
        second_copy = deepcopy(np.asarray(features.features()))
        third_copy = np.array(features.features(), copy=False)
        # test if update in pointor, change other call with copy or not
        assert first_copy[0, 0] == 0
        assert second_copy[0, 0] == 0
        assert third_copy[0, 0] == 0
        # test copy or not before changing first_copy
        assert sd_copy[0, 0] == 1
        assert fs_copy[0, 0] == 0
