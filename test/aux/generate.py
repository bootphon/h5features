# Copyright 2014-2019 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
#
# This file is part of h5features.
#
# h5features is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# h5features is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with h5features.  If not, see <http://www.gnu.org/licenses/>.
"""Generate an artificial dataset for testing h5features."""

import numpy as np
import os
import scipy.io as sio


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


def items(nitems, root='item'):
    """Item names generator"""
    return ['{}_{}'.format(root, i) for i in range(nitems)]


def labels(nitems, max_frames=3, tformat=1):
    """Random times data generator."""
    return [_times_value(_nframes(max_frames), tformat) for _ in range(nitems)]


def features(nitems, dim=2, max_frames=3):
    """Random features data generator.

    Generate random features, given the number of items the feature
    dimension and the maximum number of frames in each items.

    """
    return [np.random.randn(_nframes(max_frames), dim) for _ in range(nitems)]


def full(nitems, dim=2, max_frames=3, tformat=1,
         items_root='item', properties=False):
    """Random (items, features, times) generator.

    Generate a random tuple of (items, features, times,[, properties])
    for a set of items, given the features dimension, the maximum
    number of frames in items and the time format (either 1 or 2).

    Return
    ------

    items : list of item names associated with generated features
    times : list of timestamps for each file
    features : list of feature vectors for each file
    properties : list of dictionnaires, one per item

    We have len(files) == len(times) == len(features) == n_items

    """
    times, feat = [], []
    for _ in range(nitems):
        nframes = _nframes(max_frames)
        feat.append(np.random.randn(nframes, dim))
        times.append(_times_value(nframes, tformat))
    if properties:
        props = [{'n': n} for n in range(nitems)]
        return items(nitems, items_root), times, feat, props
    else:
        return items(nitems, items_root), times, feat


def full_dict(nitems, dim=2, max_frames=3, tformat=1,
              items_root='item', properties=False):
    """Return a data dictionary"""
    from h5features.items import Items
    from h5features.labels import Labels
    from h5features.features import Features
    from h5features.properties import Properties

    data = full(nitems, dim, max_frames, tformat,
                items_root=items_root, properties=properties)

    d = {'items': Items(data[0]),
         'labels': Labels(data[1]),
         'features': Features(data[2])}
    if properties:
        d['properties'] = Properties(data[3])
    return d


def full_data(nitems, dim=2, max_frames=3, tformat=1,
              items_root='item', properties=False):
    """Return a h5features.Data instance"""
    from h5features.data import Data
    data = full(nitems, dim, max_frames, tformat,
                items_root=items_root, properties=properties)
    return Data(data[0], data[1], data[2], check=True,
                properties=data[3] if properties else None)


def npz(directory='./npz', nfiles=100,
        dim=2, max_frames=3, tformat=1, items_root='item'):
    if os.path.exists(directory):
        raise OSError('directory {} already exists'.format(directory))
    os.mkdir(directory)
    data = full(nfiles, dim, max_frames, tformat, items_root)
    for i in range(nfiles):
        name = os.path.join(directory, data[0][i] + '.npz')
        np.savez(name, labels=data[1][i], features=data[2][i])


def mat(directory='./mat', nfiles=100,
        dim=2, max_frames=3, tformat=1, items_root='item'):
    if os.path.exists(directory):
        raise OSError('directory {} already exists'.format(directory))
    os.mkdir(directory)
    data = full(nfiles, dim, max_frames, tformat, items_root)
    for i in range(nfiles):
        name = os.path.join(directory, data[0][i] + '.mat')
        sio.savemat(name, {'labels': data[1][i], 'features': data[2][i]})
