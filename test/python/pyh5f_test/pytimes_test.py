import sys
from pyh5features import Times
from unittest import TestCase
import psutil
import numpy as np

class TimesTests(TestCase):
    """Tests on class Times"""
    def test_interval_format(self):
        """test Times constructor and methods with times.interval"""
        array = np.asarray([1,2,2,3,3,4], dtype=np.float64)
        times = Times(array,Times.interval, True)
        assert np.all(array == np.array(times))
        assert times.dim() == 2
        assert times.size() == 3
        assert times.get_format().name == "interval"

    def test_simple_format(self):
        """test Times constructor and methods with times.simple"""
        array = np.asarray([0.5, 1, 1.5], dtype=np.float64)
        times = Times(array, Times.simple, True)
        assert np.all(array == np.array(times))
        assert times.dim() == 1
        assert times.size() == 3
        assert times.get_format().name == "simple"

    def test_beg_end_constructor(self):
        """test the constructor with begin and end arrays"""
        a = np.array([1,2,3], dtype=np.float64)
        b = np.array([2,3,4],dtype=np.float64)
        times = Times(a, b, True)
        assert times.dim() == 2
        assert times.size() == 3
        assert times.get_format().name == "interval"
        assert np.all(np.array(times) == np.asarray([1,2,2,3,3,4], dtype=np.float64))
    
    def test_start_stop_methods(self):
        """test the start() and stop() methods"""
        array = np.asarray([1,2,2,3,3,4], dtype=np.float64)
        times = Times(array,Times.interval, True)
        assert times.start() == 1
        assert times.stop() == 4
    
    def test_in_equality(self):
        """ test oprator== and operator!="""
        array = np.asarray([1,2,2,3,3,4], dtype=np.float64)
        t1 = Times(array,Times.interval, True)
        t2 = Times(array,Times.interval, True)
        
        array = np.asarray([1,2,2,3,3,4,4,5], dtype=np.float64)
        t3 = Times(array,Times.interval, True)
        a = np.array([1,2,3], dtype=np.float64)
        b = np.array([2,3,4],dtype=np.float64)
        t4 = Times(a, b, True)
        array = np.asarray([1.5, 2.5, 3.5], dtype=np.float64)
        t5 = Times(array,Times.simple, True)
        assert t1 == t2
        assert t1 != t3
        assert t2 != t3
        assert t4 == t1
        assert t4 != t5

    def test_update(self):
        """test the update of times"""
        array = np.asarray([1,2,2,3,3,4], dtype=np.float64)
        times = Times(array,Times.interval, True)
        copy_true = np.array(times, copy=True)
        copy_false = np.array(times, copy=False)
        np.array(times, copy=False)[0] = -1
        assert copy_true[0] == 1
        assert copy_false[0] == -1
