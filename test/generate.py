"""Generate an artificial dataset for testing h5features.

@author: Mathieu Bernard

"""

import numpy as np

def features(n_items, n_feat=2, max_frames=3):
    """Random feature generator.

    Generate random features for a set of items, given the feature
    vector size and the maximum number of frames in items.

    Parameters
    ----------

    n_items : int
        number of items for which to generate features

    n_feat : int, optional
        dimension of the generated feature vector. Default is n_feat = 2

    max_frame : int, optional
        number of frames for each item is randomly choosen in [1,max_frame]

    Return
    ------

    items : list of item names associated with generated features
    times : list of timestamps for each file
    features : list of feature vectors for each file

    We have len(files) == len(times) == len(features) == n_items

    """

    items, times, features = [], [], []
    for i in xrange(n_items):
        n_frames = np.random.randint(max_frames) + 1
        features.append(np.random.randn(n_frames, n_feat))
        times.append(np.linspace(0, 1, n_frames))
        items.append('s%d' % i)

    return items, times, features
