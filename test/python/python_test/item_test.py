import sys
import pytest
from unittest import TestCase
import numpy as np
sys.path.insert(0, "./h5features2")
from item import Item
# from pyh5features import Item as pyitem
class TestItem(TestCase):
    """Test Item class"""
    def test_constuctor(self):
        """ test constructor """
        features = np.ones((10, 4), dtype=np.float64)
        begin = np.array([0, 1, 2, 3], dtype=np.float64)
        end = np.array([1, 2, 3, 4], dtype=np.float64)
        begin = np.asarray([i for i in range(0, 10)])
        end = np.asarray([i for i in range(1, 11)])
        properties = {}
        name = "test"
        # test error if times is a list of begin end
        with pytest.raises(TypeError):
            _ = Item.create(name, features, [begin, end], properties=properties)
        # test error if begin or end are list and not numpy arrays
        with pytest.raises(TypeError):
            _ = Item.create(name, features, ([i for i in range(0, 10)], end), properties=properties)
        with pytest.raises(TypeError):
            _ = Item.create(name, features, (begin, [i for i in range(1, 11)]), properties=properties)
        # test error if features is a list
        with pytest.raises(TypeError):
            print(features.tolist())
            _ = Item.create(name, features.tolist(), (begin, end), properties=properties)
        # test error if properties are not in dict
        features = np.ones((10, 4), dtype=np.float64)
        with pytest.raises(TypeError):
            _ = Item.create(name, features, (begin, end), properties=[])
        # test if features is not flaot64
        with pytest.raises(TypeError):
            _ = Item.create(name, np.asarray(features, dtype=np.int8), (begin, end))
        # test not str(name)
        with pytest.raises(TypeError):
            name = 1001
            _ = Item(name, np.asarray(features, dtype=np.float64), (begin, end))

    def test_features(self):
        """ test features copy or not """

        features = np.ones((1000000, 4), dtype=np.float64)
        begin = np.asarray([0, 1, 2, 3],np.float64 )
        end = np.asarray([1, 2, 3, 4],np.float64)
        begin = np.asarray([i for i in range(0, 1000000)],np.float64)
        end = np.asarray([i for i in range(1, 1000000+1)],np.float64)
        properties = {}
        name = "test"
        item = Item.create(name, features, (begin, end), properties=properties)
        f1 = item.features(copy=False)
        f2 = item.features(copy=True)
        f3 = item.features(copy=False)
        f1[0, 0] = 0
        self.assertEqual(f1[0, 0], 0)
        self.assertEqual(f2[0, 0], 1)
        self.assertEqual(f3[0, 0], 0)

    def test_times(self):
        """ test time copy or not"""
        features = np.ones((1000000, 4), dtype=np.float64)
        begin = np.asarray([0, 1, 2, 3],np.float64)
        end = np.asarray([1, 2, 3, 4], np.float64)
        begin = np.asarray([i for i in range(0, 1000000)],np.float64)
        end = np.asarray([i for i in range(1, 1000000+1)],np.float64)
        properties = {}
        name = "test"
        item = Item.create(name, features, (begin, end), properties=properties)
        t1 = item.times(copy=False)
        t2 = item.times(copy=True)
        t3 = item.times(copy=False)
        t1[3, 0] = 0
        self.assertEqual(t1[3, 0], 0)
        self.assertEqual(t2[3, 0], 3)
        self.assertEqual(t3[3, 0], 0)
        self.assertTrue(np.all(t2[:,0]==begin))
        self.assertTrue(np.all(t2[:,1]==end))

    def test_properties(self):
        """test properties"""
        features = np.ones((1000000, 4), dtype=np.float64)
        begin = np.asarray([0, 1, 2, 3],np.float64)
        end = np.asarray([1, 2, 3, 4], np.float64)
        begin = np.asarray([i for i in range(0, 1000000)],np.float64)
        end = np.asarray([i for i in range(1, 1000000+1)],np.float64)
        # a dict of dict
        properties = {
            "int" : 1,
            "double" : 1.,
            "bool" : True,
            "string" : "str",
            "list of string" : ["str1", "str2"],
            "list of int" : [1, 2, 3],
            "list of double" : [1., 2., 3.],
            "dict": {
                "int " : 1,
                "double" : 1.,
                "bool" : True,
                "string" : "str",
                "list of string" : ["str1", "str2"],
                "list of int" : [1, 2, 3],
                "list of double" : [1., 2., 3.],
        }}
        name = "test"
        item = Item.create(name, features, (begin, end), properties=properties)
        props = item.properties()
        assert props.get("int", None) is not None
        assert props.get("double", None) is not None
        assert props.get("bool", None) is not None
        assert props.get("string", None) is not None
        assert props.get("list of int", None) is not None
        assert props.get("list of double", None) is not None
        assert props.get("list of string", None) is not None
        assert props.get("dict", None) is not None
        assert props["int"] == 1
        assert props["bool"]
        assert props["double"] == 1.
        assert props["string"] == "str"
        assert props["list of string"] == ["str1", "str2"]
        assert props["list of int"] == [1, 2, 3]
        assert props["list of double"] == [1., 2., 3.]
        assert props["dict"] == {
                            "int " : 1,
                            "double" : 1.,
                            "bool" : True,
                            "string" : "str",
                            "list of string" : ["str1", "str2"],
                            "list of int" : [1, 2, 3],
                            "list of double" : [1., 2., 3.],
        }
        # test update, add properties : string or dict
        item.set_properties("int", "set")
        self.assertEqual(item.properties()["int"], "set")
        self.assertTrue(isinstance(item.properties(), dict))
        dic2 = {
            "int" : 1,
            "double" : 1.,
            "bool" : True,
            "string" : "str",
            "list of string" : ["str1", "str2"],
            "list of int" : [1, 2, 3],
            "list of double" : [1., 2., 3.],
            }
        item.set_properties("dict2", dic2)
        self.assertEqual(item.properties()["dict2"], dic2)

        self.assertTrue(item.properties_contains("int"))
        item.properties_erase("int")
        self.assertFalse(item.properties_contains("int"))
        item.set_properties("int", 8)
        self.assertEqual(item.properties()["int"], 8)

        # test bad function call
        with pytest.raises(TypeError):
            _ = item.properties_contains(8)
        with pytest.raises(TypeError):
            item.properties_erase(8)
        with pytest.raises(TypeError):
            _ = item.set_properties(8, 8)
        
        # test bad key type
        properties = {
            2 : 1,
            "double" : 1.,
            "bool" : True,
            "string" : "str",
            "list of string" : ["str1", "str2"],
            "list of int" : [1, 2, 3],
            "list of double" : [1., 2., 3.],
            "dict": {
                "int " : 1,
                "double" : 1.,
                "bool" : True,
                "string" : "str",
                "list of string" : ["str1", "str2"],
                "list of int" : [1, 2, 3],
                "list of double" : [1., 2., 3.],
        }}
        with pytest.raises(TypeError):
            item = Item.create(name, features, (begin, end), properties=properties)

        properties = {
            "int" : 1,
            "double" : 1.,
            "bool" : True,
            "string" : "str",
            "list of string" : ["str1", "str2"],
            "list of int" : [1, 2, 3],
            "list of double" : [1., 2., 3.],
            "dict": {
                2 : 1,
                "double" : 1.,
                "bool" : True,
                "string" : "str",
                "list of string" : ["str1", "str2"],
                "list of int" : [1, 2, 3],
                "list of double" : [1., 2., 3.],
        }}
        with pytest.raises(TypeError):
            item = Item.create(name, features, (begin, end), properties=properties)