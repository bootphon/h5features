import sys
from os import remove
from os.path import exists
from pyh5features import Item
from pyh5features import Writer, Reader
# from pyh5features.Writer import version
from unittest import TestCase
import psutil
import numpy as np
from copy import deepcopy

class ReaderWritterTests(TestCase):
    def test_writting(self):
        """ test if np.array is copied or passed by reference to c++ """
        array = np.ones((1000000, 4))
        begin = np.asarray([0, 1, 2, 3])
        end = np.asarray([1, 2, 3, 4])
        name = "Test"
        properties = {}
        print( Writer.version.v2_0)
        item = Item(name, array, begin, end, properties, True)
        if exists("test.h5f"):
            remove("test.h5f")
        writer = Writer("test.h5f", "test", False, True, Writer.version.v2_0)
        writer.write(item)
        reader = Reader("test.h5f", "test")
        self.assertEqual(reader.items()[0], "Test")
        it = reader.read(reader.items()[0])
        self.assertTrue(np.all(array==np.array(it.features())))
        self.assertEqual(item, it)