"""Generate an artificial dataset for testing h5features.

@author: Mathieu Bernard

"""

import numpy as np


def _times_value(n_frames, time_format):
    """Generate a new random value for times"""
    if time_format == 1:
        return np.linspace(0, 1, n_frames)
    else:
        simple = np.linspace(0, 1, 3)
        return np.array([simple, simple+1])


def items(n_items):
    """Random items generator"""
    itm = []
    for i in range(n_items):
        itm.append('item {}'.format(i))
    return itm


def features(n_items, dim=2, max_frames=3):
    """Random feature generator.

    Generate random features, given the number of items the feature
    dimension and the maximum number of frames in each items.

    """
    feat = []
    for _ in range(n_items):
        n_frames = np.random.randint(max_frames) + 1
        feat.append(np.random.randn(n_frames, dim))
    return feat


def full(n_items, dim=2, max_frames=3, tformat=1):
    """Random (items, features, times) generator.

    Generate a random tuple of (items, features, times) for a set of
    items, given the features dimension, the maximum number of
    frames in items and the time format (either 1 or 2).

    Return
    ------

    items : list of item names associated with generated features
    times : list of timestamps for each file
    features : list of feature vectors for each file

    We have len(files) == len(times) == len(features) == n_items

    """

    itm, times, feat = [], [], []
    for i in range(n_items):
        n_frames = np.random.randint(max_frames) + 1
        feat.append(np.random.randn(n_frames, dim))
        times.append(_times_value(n_frames, tformat))
        itm.append('s%d' % i)

    return itm, times, feat
