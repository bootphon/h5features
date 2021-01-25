import sys
from pyh5features import Features
from unittest import TestCase
import psutil
import numpy as np

class FeaturesTests(TestCase):
    """Tests on class Features"""
    def test_data_equality(self):
        array = np.asarray([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]], dtype=np.float64)
        features = Features(array, 4, True)
        assert np.all(array == np.array(features))
    def test_update_from_init(self):
        """ test if np.array is copied or passed by reference to c++ """
        array = np.ones((10000000, 4))
        features = Features(np.array(array, copy=False), 10000000, True)
        copy = np.array(features, copy=False)
        array[0, 0] = 0
        assert array[0, 0] == 0
        assert copy[0, 0]!= 0
    
    def test_dim_size(self):
        """ this method test the method dim and size of Features"""
        features = Features(np.ones((10000000, 4)), 10000000, True)
        assert features.dim() == 10000000
        assert features.size() == 4

    def test_in_equality(self):
        """ test oprator== and operator!="""
        f1 = Features(np.ones((10000000, 4)), 10000000, True)
        f2 = Features(np.ones((10000000, 4)), 10000000, True)
        f3 = Features(np.zeros((10000000, 4)), 10000000, True)
        assert f1 == f2
        assert f1 != f3
        assert f2 != f3

    def test_copy_true(self):
        """ this method test the updates of severals call of features.data()
         when udpdate the numpy array with copy=true"""
        features = Features(np.ones((10000000, 4)), 10000000, True)
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
        features = Features(np.ones((10000000, 4)), 10000000, True)
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