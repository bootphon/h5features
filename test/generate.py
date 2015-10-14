"""Generate an artificial dataset for testing h5features.

@author: Mathieu Bernard

"""

import numpy as np


def _times_value(nframes, tformat):
    """Generate a new random value for times"""
    if tformat == 1:
        return np.linspace(0, 1, nframes)
    else:
        simple = np.linspace(0, 1, nframes)
        return np.array([simple, simple+1]).T


def _nframes(max_frames):
    """Return a random number of frames in [1, max_frames]."""
    return np.random.randint(max_frames) + 1


def items(nitems):
    """Item names generator"""
    return ['item {}'.format(i) for i in range(nitems)]


def times(nitems, max_frames=3, tformat=1):
    """Random times data generator."""
    return [_times_value(_nframes(max_frames), tformat) for _ in range(nitems)]


def features(nitems, dim=2, max_frames=3):
    """Random features data generator.

    Generate random features, given the number of items the feature
    dimension and the maximum number of frames in each items.

    """
    return [np.random.randn(_nframes(max_frames), dim) for _ in range(nitems)]


def full(nitems, dim=2, max_frames=3, tformat=1):
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
    times, feat = [], []
    for _ in range(nitems):
        nframes = _nframes(max_frames)
        feat.append(np.random.randn(nframes, dim))
        times.append(_times_value(nframes, tformat))
    return items(nitems), times, feat
