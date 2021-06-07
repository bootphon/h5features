import sys
from os import remove
from os.path import exists, abspath
import pytest
from unittest import TestCase
import numpy as np

sys.path.insert(0, "./h5features2")
from item import Item
from writer import Writer
from reader import Reader
from versions import Versions


class TestWriterReader(TestCase):
    """Test Item class"""
    def test_versions(self):
        self.assertEqual(Versions.versions(), ["1.0", "1.1", "1.2", "2.0"])

    def test_constructor_writer(self):
        # array = np.ones((9, 1000))
        # array[1:3, ] = 0
        # begin = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float64)
        # end = np.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.float64)
        # name = "Test"
        # properties = {}
        # item = Item(name, array, (begin, end), properties=properties)
        # del array
        # del begin
        # del end
        if exists("test.h5f"):
            remove("test.h5f")
        with pytest.raises(TypeError):
            _ = Writer(0, "test", False, True, "2.0")
        with pytest.raises(TypeError):
            _ = Writer("test.h5f", 0, False, True, "2.0")
        with pytest.raises(TypeError):
            _ = Writer("test.h5f", "test", "test", True, "2.0")
        with pytest.raises(TypeError):
            _ = Writer("test.h5f", "test", False, "test", "2.0")
        with pytest.raises(KeyError):
            _ = Writer("test.h5f", "test", False, True, "2.10")
        with pytest.raises(FileNotFoundError):
            _ = Writer("/test/test.h5f", "test", False, True, "2.0")
        writer = Writer("test.h5f", "test", False, True, "2.0")
        self.assertEqual(writer.version(), "2.0")
        self.assertEqual(writer.filename(), abspath("test.h5f"))
        self.assertEqual(writer.groupname(), "test")

    def test_v2_0(self):
        array = np.ones((9, 1000))
        array[1:3, ] = 0
        begin = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float64)
        end = np.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.float64)
        name = "Test"
        properties = {"test": True}
        item = Item.create(name, array, (begin, end), properties=properties)

        print(item)
        if exists("test2.h5f"):
            remove("test2.h5f")
        writer = Writer("test2.h5f", "test", False, True, "2.0")
        writer.write(item)
        writer2 = Writer("test2.h5f", "test2", False, True, "2.0")
        writer2.write(item)
        reader = Reader("test2.h5f", "test")
        # self.assertEqual(reader.items()[0], "Test")
        it = reader.read("Test", ignore_properties=False)
        self.assertTrue(np.all(array==it.features()))
        self.assertTrue(np.all(begin == it.times()[:,0]))
        self.assertTrue(np.all(end == it.times()[:,1]))
        self.assertEqual(it.properties(), properties)
        self.assertEqual(item, it)
        it = reader.read("Test", ignore_properties=True)
        self.assertTrue(np.all(array==it.features()))
        self.assertTrue(np.all(begin == it.times()[:,0]))
        self.assertTrue(np.all(end == it.times()[:,1]))
        self.assertEqual(it.properties(), {})
        self.assertNotEqual(item, it)
        it = reader.read("Test", ignore_properties=True, features_between_times=(1, 4))
        self.assertTrue(np.all(array[1:4]==it.features()))
        self.assertTrue(np.all(begin[1:4] == it.times()[:,0]))
        self.assertTrue(np.all(end[1:4] == it.times()[:,1]))
        self.assertNotEqual(item, it)
        self.assertEqual("test2.h5f", reader.filename())
        self.assertEqual("test", reader.groupname())
        self.assertEqual(reader.version(), "2.0")
        reader = Reader("test2.h5f", "test2")
        # self.assertEqual(reader.items()[0], "Test")
        it = reader.read("Test", ignore_properties=False)
        it = reader.read("Test", ignore_properties=False)
        self.assertTrue(np.all(array==it.features()))
        self.assertTrue(np.all(begin == it.times()[:,0]))
        self.assertTrue(np.all(end == it.times()[:,1]))
        self.assertEqual(it.properties(), properties)
        self.assertEqual(item, it)
        it = reader.read("Test", ignore_properties=True)
        self.assertTrue(np.all(array==it.features()))
        self.assertTrue(np.all(begin == it.times()[:,0]))
        self.assertTrue(np.all(end == it.times()[:,1]))
        self.assertEqual(it.properties(), {})
        self.assertNotEqual(item, it)
        it = reader.read("Test", ignore_properties=True, features_between_times=(1, 4))
        self.assertTrue(np.all(array[1:4]==it.features()))
        self.assertTrue(np.all(begin[1:4] == it.times()[:,0]))
        self.assertTrue(np.all(end[1:4] == it.times()[:,1]))
        self.assertNotEqual(item, it)
        self.assertEqual("test2.h5f", reader.filename())
        self.assertEqual("test2", reader.groupname())
        self.assertEqual(reader.version(), "2.0")
    # def test_v1_0(self):
    #     array = np.ones((9, 1000))
    #     array[1:3, ] = 0
    #     begin = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float64)
    #     end = np.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.float64)
    #     name = "Test"
    #     properties = {}
    #     item = Item(name, array, (begin, end), properties=properties)
    #     del array
    #     del begin
    #     del end
    #     if exists("test.h5f"):
    #         remove("test.h5f")
    #     writer = Writer("test.h5f", "test", False, False, "1.0")
    #     writer.write(item)

    def test_v1_1(self):
        array = np.ones((9, 1000))
        array[1:3, ] = 0
        begin = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float64)
        end = np.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.float64)
        name = "Test"
        properties = {}
        item = Item.create(name, array, (begin, end), properties=properties)
        del array
        del begin
        del end
        if exists("test.h5f"):
            remove("test.h5f")
        writer = Writer("test.h5f", "test", False, True, "1.1")
        writer.write(item)
        reader = Reader("test.h5f", "test")
        self.assertEqual(reader.version(), "1.1")

    def test_v1_2(self):
        array = np.ones((9, 1000))
        array[1:3, ] = 0
        begin = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float64)
        end = np.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.float64)
        name = "Test"
        properties = {}
        item = Item.create(name, array, (begin, end), properties=properties)
        del array
        del begin
        del end
        if exists("test.h5f"):
            remove("test.h5f")
        writer = Writer("test.h5f", "test", False, True, "1.2")
        writer.write(item)
        reader = Reader("test.h5f", "test")
        self.assertEqual(reader.version(), "1.2")
