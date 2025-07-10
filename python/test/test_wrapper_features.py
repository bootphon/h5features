"""Test of the Features from wrapper"""

import numpy as np

from h5features import Item


def test_data_equality() -> None:
    array = np.asarray([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]], dtype=np.float64)
    times = np.vstack((np.arange(4), np.arange(4) + 1)).T.astype(np.float64)
    name = "Test"
    item = Item(name, array, times, {})
    assert np.all(array == item.features())


def test_update_from_init() -> None:
    """test if np.array is copied or passed by reference to c++"""
    array = np.ones((4, 4))
    times = np.arange(4).astype(np.float64).reshape(-1, 1)
    name = "Test"
    item = Item(name, array, times, {})
    features = item.features()
    fcopy = np.array(features, copy=False)
    array[0, 0] = 0
    assert array[0, 0] == 0
    assert fcopy[0, 0] != 0


def test_in_equality() -> None:
    """test numpy equality"""
    times = np.asarray([[0, 1, 2, 3], [1, 2, 3, 4]]).T.astype(np.float64)

    a = Item("a", np.ones((4, 4), dtype=np.float64), times, {})
    b = Item("b", np.ones((4, 4), dtype=np.float64), times, {})
    c = Item("c", np.zeros((4, 4), dtype=np.float64), times, {})

    f1 = np.array(a.features(), copy=False)
    f2 = np.array(b.features(), copy=False)
    f3 = np.array(c.features(), copy=False)

    assert np.all(f1 == f2)
    assert np.all(f1 == np.ones((4, 4)))
    assert np.all(f3 != 1)
    assert np.all(f2 != f3)
