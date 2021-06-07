from os import remove
from os.path import exists
from _h5features import ItemWrapper, WriterWrapper, ReaderWrapper

from unittest import TestCase
import numpy as np


class ReaderWritterTests(TestCase):
    def test_reading_writting(self):
        """ """
        array = np.ones((9, 1000))
        array[1:3, ] = 0
        begin = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float64)
        end = np.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.float64)
        name = "Test"
        properties = {}
        print(WriterWrapper.version.v2_0)
        item = ItemWrapper(name, array, begin, end, properties, True)
        if exists("test.h5f"):
            remove("test.h5f")
        writer = WriterWrapper("test.h5f", "test", False, True, WriterWrapper.version.v2_0)
        writer.write(item)
        reader = ReaderWrapper("test.h5f", "test")
        self.assertEqual(reader.items()[0], "Test")
        it = reader.read(reader.items()[0], False)
        self.assertTrue(np.all(array==np.array(it.features())))
        self.assertEqual(item, it)
        it = reader.read_btw(reader.items()[0], np.float64(1), np.float64(3), False)
        self.assertTrue(np.all(array[1: 3,:]==np.array(it.features())))
        self.assertTrue(np.all(array[1: 3,:]==np.zeros((2, 1000))))
        self.assertTrue(np.all(array[[0,3,4,5,6,7,8]] == np.ones((7, 1000))))
        self.assertNotEqual(item, it)
        self.assertEqual("test.h5f", reader.filename())
        self.assertEqual("test", reader.groupname())
        self.assertEqual(reader.get_version().name, "v2_0")
