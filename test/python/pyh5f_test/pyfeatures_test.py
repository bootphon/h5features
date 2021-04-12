import sys
from h5features import Item
from unittest import TestCase
import psutil
import numpy as np

class FeaturesTests(TestCase):
    """Tests on features"""
    def test_data_equality(self):
        array = np.asarray([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]], dtype=np.float64)
        begin = np.asarray([0, 1, 2])
        end = np.asarray([1, 2, 3])
        name = "Test"
        properties = {}
        item = Item(name, array, begin, end, properties, True)
        features = item.features()
        assert np.all(array == np.array(features))

    def test_update_from_init(self):
        """ test if np.array is copied or passed by reference to c++ """
        array = np.ones((10000000, 4))
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        name = "Test"
        properties = {}
        item = Item(name, array, begin, end, properties, True)
        features = item.features()
        copy = np.array(features, copy=False)
        array[0, 0] = 0
        assert array[0, 0] == 0
        assert copy[0, 0] != 0
        


    def test_in_equality(self):
        """ test oprator== and operator!="""
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        name = "Test"
        properties = {}
        f1 = Item(name, np.ones((10000000, 4)), begin, end, properties, True).features()
        f2 = Item(name, np.ones((10000000, 4)), begin, end, properties, True).features()
        f3 = Item(name, np.zeros((10000000, 4)), begin, end, properties, True).features()
        assert np.all(f1 == f2)
        assert np.all(1 != f3)
        assert np.all(f2 != f3)

    def test_copy_true(self):
        """ this method test the updates of severals call of features.data()
         when udpdate the numpy array with copy=true"""
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        name = "Test"
        properties = {}
        features = Item(name, np.ones((10000000, 4)), begin, end, properties, True).features()
        first_copy = np.array(features, copy=True)
        second_copy = np.array(features, copy=True)
        third_copy = np.array(features, copy=False)
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
        """ this method test the updates of severals call of features.data()
         when udpdate the numpy array with copy=false"""
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        name = "Test"
        properties = {}
        features = Item(name, np.ones((10000000, 4)), begin, end, properties, True).features()
        first_copy = np.array(features, copy=False)
        first_copy[0, 0] = 0
        second_copy = np.array(features, copy=True)
        third_copy = np.array(features, copy=False)
        # test if update in pointor, change other call with copy or not
        assert first_copy[0, 0] == 0
        assert second_copy[0, 0] == 0
        assert third_copy[0, 0] == 0

    # def test_memory(self):
    #     """ this method test the update in memory after calling Features and 
    #     features.data() """
    #     mem_zero = psutil.virtual_memory()[1]  # available memory
    #     features = Features(np.ones((10000000, 4)), 10000000, True)
    #     mem_one = psutil.virtual_memory()[1]  # available memory
    #     copy_true = np.array(features, copy=True)
    #     mem_two = psutil.virtual_memory()[1]  # available memory
    #     copy_false = np.array(features, copy=False)
    #     mem_three = psutil.virtual_memory()[1]  # available memory
    #     del copy_false
    #     mem_four = psutil.virtual_memory()[1]  # available memory
    #     del copy_true
    #     mem_five = psutil.virtual_memory()[1]  # available memory
    #     del features
    #     mem_six = psutil.virtual_memory()[1]  # available memory
    #     # test the copy=False
    #     assert mem_three - mem_two == 0
    #     # test copy = True
    #     assert mem_two - mem_one < 0
    #     # test the delete on copy=True
    #     assert mem_five - mem_four > 0
    #     # test the delete of features
    #     assert mem_six - mem_five > 0
    #     # test the creation of features
    #     assert mem_one - mem_zero < 0
    #     # test the delete of copy_false
    #     assert mem_four - mem_three == 0