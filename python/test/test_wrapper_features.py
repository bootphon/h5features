"""Test of the Features from wrapper"""
import copy
import numpy as np
from _h5features import ItemWrapper


def test_data_equality():
    array = np.asarray(
        [[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]],
        dtype=np.float64)
    times = np.vstack((np.arange(4), np.arange(4) + 1)).T.astype(np.float64)
    name = "Test"
    item = ItemWrapper(name, array, times, {}, True)

    assert np.all(array == item.features())


def test_update_from_init():
    """ test if np.array is copied or passed by reference to c++ """
    array = np.ones((4, 4))
    times = np.arange(4).astype(np.float64).reshape(-1, 1)
    name = "Test"
    item = ItemWrapper(name, array, times, {}, True)
    features = item.features()
    fcopy = np.array(features, copy=False)

    array[0, 0] = 0
    assert array[0, 0] == 0
    assert fcopy[0, 0] != 0


def test_in_equality():
    """ test numpy equality"""
    times = np.asarray([[0, 1, 2, 3], [1, 2, 3, 4]]).T.astype(np.float64)

    a = ItemWrapper(
        "a", np.ones((4, 4), dtype=np.float64), times, {}, True)
    b = ItemWrapper(
        "b", np.ones((4, 4), dtype=np.float64), times, {}, True)
    c = ItemWrapper(
        "c", np.zeros((4, 4), dtype=np.float64), times, {}, True)

    f1 = np.array(a.features(), copy=False)
    f2 = np.array(b.features(), copy=False)
    f3 = np.array(c.features(), copy=False)

    assert np.all(f1 == f2)
    assert np.all(f1 == np.ones((4, 4)))
    assert np.all(f3 != 1)
    assert np.all(f2 != f3)


def test_copy_true():
    """ this method test the updates of severals call of features.data()
    when udpdate the numpy array with copy=true"""
    times = np.asarray([[0, 1, 2, 3], [1, 2, 3, 4]]).T.astype(np.float64)
    feats = np.ones((4, 4), dtype=np.float64)
    name = "Test"
    features = ItemWrapper(name, feats, times, {}, True)
    first_copy = copy.deepcopy(np.asarray(features.features()))
    second_copy = copy.deepcopy(np.asarray(features.features()))
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


def test_copy_false():
    """ this method test the updates of severals call of features()
    when udpdate the numpy array with copy=false"""
    times = np.asarray([[0, 1, 2, 3], [1, 2, 3, 4]]).T.astype(np.float64)
    name = "Test"
    features = ItemWrapper(name, np.ones((4, 4)), times, {}, True)
    first_copy = np.array(features.features(), copy=False)
    fs_copy = np.array(features.features(), copy=False)
    sd_copy = copy.deepcopy(np.asarray(features.features()))
    first_copy[0, 0] = 0
    second_copy = copy.deepcopy(np.asarray(features.features()))
    third_copy = np.array(features.features(), copy=False)

    # test if update in pointor, change other call with copy or not
    assert first_copy[0, 0] == 0
    assert second_copy[0, 0] == 0
    assert third_copy[0, 0] == 0

    # test copy or not before changing first_copy
    assert sd_copy[0, 0] == 1
    assert fs_copy[0, 0] == 0
