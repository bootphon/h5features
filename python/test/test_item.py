import numpy as np
import pytest

from h5features import Item


@pytest.fixture
def item():
    features = np.arange(40).reshape((10, 4)).astype(np.float64)
    times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)
    return Item('item', features, times, properties={'spam': 'spam a lot'})


def test_basic(item):
    assert item.name == 'item'
    assert item.size == 10
    assert item.dim == 4
    assert np.all(
        item.features
        == np.arange(40).reshape((10, 4)).astype(np.float64))
    assert item.times[:, 0].tolist() == list(range(10))
    assert item.properties == {'spam': 'spam a lot'}


def test_name(item):
    # name must be a string
    with pytest.raises(RuntimeError):
        Item(10, item.features, item.times)


def test_times(item):
    # helper fonction to generate an item with custom times
    def make_item(times):
        return Item(item.name, item.features, times)

    #  error if times is not a float64 numpy array
    with pytest.raises(RuntimeError):
        make_item([1, 2, 3])
    with pytest.raises(RuntimeError):
        make_item('abc')
    with pytest.raises(RuntimeError):
        make_item(item.times.astype(np.float32))

    # times as 1D array
    item2 = make_item(item.times[:, 0].T)
    assert item2.times.shape == (10, 1)
    assert item2.times.flatten().tolist() == list(range(10))


    # # test error if features is a list
    # with pytest.raises(TypeError):
    #     _ = Item(
    #         name,
    #         features.tolist(),
    #         (begin, end),
    #         properties=properties)

    # # test error if properties are not in dict
    # features = np.ones((10, 4), dtype=np.float64)
    # with pytest.raises(TypeError):
    #     _ = Item(
    #         name,
    #         features,
    #         (begin, end),
    #         properties=[])

    # # test if features is not flaot64
    # with pytest.raises(TypeError):
    #     _ = Item(
    #         name,
    #         np.asarray(features, dtype=np.int8),
    #         (begin, end))



def test_features_firstdim(item):
    """ test features copy or not """
    f1 = item.features
    f2 = np.copy(item.features)
    f3 = item.features
    f1[0, 1] = 3.14

    assert f1[0, 1] == 3.14
    assert f2[0, 1] == 1
    assert f3[0, 1] == 3.14


def test_features_seconddim():
    """ test features copy or not """
    features = np.ones((10, 4), dtype=np.float64)
    times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)
    properties = {}
    name = "test"
    item = Item(name, features, times, properties=properties)
    f1 = item.features
    assert np.all(f1 == features)

    f2 = np.copy(item.features)
    f3 = item.features
    f1[0, 0] = 0
    assert f1[0, 0] == 0
    assert f2[0, 0] == 1
    assert f3[0, 0] == 0


# def test_times():
#     """ test time copy or not"""
#     features = np.ones((10, 4), dtype=np.float64)
#     times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)
#     properties = {}
#     name = "test"
#     item = Item(name, features, times, properties=properties)
#     t1 = item.times(copy=False)
#     t2 = item.times(copy=True)
#     t3 = item.times(copy=False)
#     t1[3, 0] = 0

#     assert t1[3, 0] == 0
#     assert t2[3, 0] == 3
#     assert t3[3, 0] == 0
#     assert np.all(t2 == times)


def test_properties():
    """test properties"""
    features = np.ones((10, 4), dtype=np.float64)
    times = np.vstack((np.arange(10), np.arange(10) + 1)).T.astype(np.float64)

    # a dict of dict
    properties = {
        'int': 1,
        'double': 1.,
        'bool': True,
        'string': 'str',
        'list of string': ['str1', 'str2'],
        'list of int': [1, 2, 3],
        'list of double': [1., 2., 3.],
        'dict': {
            'int ': 1,
            'double': 1.,
            'bool': True,
            'string': 'str',
            'list of string': ['str1', 'str2'],
            'list of int': [1, 2, 3],
            'list of double': [1., 2., 3.]}}
    name = 'test'
    item = Item(name, features, times, properties=properties)
    props = item.properties
    assert props['int'] == 1
    assert props['bool']
    assert props['double'] == 1.
    assert props['string'] == 'str'
    assert props['list of string'] == ['str1', 'str2']
    assert props['list of int'] == [1, 2, 3]
    assert props['list of double'] == [1., 2., 3.]
    assert props['dict'] == {
        'int ': 1,
        'double': 1.,
        'bool': True,
        'string': 'str',
        'list of string': ['str1', 'str2'],
        'list of int': [1, 2, 3],
        'list of double': [1., 2., 3.]}

    # # test update, add properties : string or dict
    # item.set_properties('int', 'set')
    # assert item.properties()['int'] == 'set'
    # assert isinstance(item.properties(), dict)

    # dic2 = {
    #     'int': 1,
    #     'double': 1.,
    #     'bool': True,
    #     'string': 'str',
    #     'list of string': ['str1', 'str2'],
    #     'list of int': [1, 2, 3],
    #     'list of double': [1., 2., 3.]}
    # item.set_properties('dict2', dic2)
    # assert item.properties()['dict2'] == dic2
    # assert item.properties_contains('int')

    # item.properties_erase('int')
    # assert not item.properties_contains('int')
    # assert 'int' not in item.properties()

    # item.set_properties('int', 8)
    # assert item.properties()['int'] == 8

    # # test bad function call
    # with pytest.raises(TypeError):
    #     _ = item.properties_contains(8)
    # with pytest.raises(TypeError):
    #     item.properties_erase(8)
    # with pytest.raises(TypeError):
    #     _ = item.set_properties(8, 8)

    # test bad key type
    properties = {
        2: 1,
        'double': 1.,
        'bool': True}
    with pytest.raises(RuntimeError):
        item = Item(name, features, times, properties=properties)

    properties = {
        'int': 1,
        'list of double': [1., 2., 3.],
        'dict': {
            2: 1,
            'double': 1.}}
    with pytest.raises(RuntimeError):
        item = Item(name, features, times, properties=properties)

    properties = {'not valid': ['a', 1]}
    with pytest.raises(RuntimeError):
        item = Item(name, features, times, properties=properties)

    properties = {'not valid': np.random.rand(5, 2)}
    with pytest.raises(RuntimeError):
        item = Item(name, features, times, properties=properties)
