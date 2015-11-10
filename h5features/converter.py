# Copyright 2014-2015 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
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

"""Provides the Converter class to the h5features package."""

import h5py
import os
import numpy as np
import scipy.io as sio

from .data import Data
from .reader import Reader
from .writer import Writer

class Converter(object):
    """This class allows convertion from various formats to h5features."""
    def __init__(self, filename, groupname, chunk=0.1):
        self._writer = Writer(filename, chunk)
        self.groupname = groupname

    def _write(self, item, labels, features):
        data = Data([item], [labels], [features])
        self._writer.write(data, self.groupname, append=True)

    def _labels(self, data):
        labels = 'labels' if 'labels' in data else 'times'
        return data[labels]

    def close(self):
        self._writer.close()

    def convert(self, infile):
        if not os.path.isfile(infile):
            raise IOError('{} is not a valid file'.format(infile))

        ext = os.path.splitext(infile)[1]
        if ext == '.npz':
            self.npz_convert(infile)
        elif ext == '.mat':
            self.mat_convert(infile)
        elif ext == '.h5':
            self.h5features_convert(infile)
        else:
            raise IOError('Unknown file format for {}'.format(infile))

    def npz_convert(self, infile):
        data = np.load(infile)
        item = os.path.splitext(infile)[0]
        labels = self._labels(data)
        features = data['features']
        self._write(item, labels, features)

    def mat_convert(self, infile):
        data = sio.loadmat(infile)
        item = os.path.splitext(infile)[0]
        labels = self._labels(data)
        labels = labels[0] if labels.shape[0] == 1 else labels
        features = data['features']
        self._write(item, labels, features)

    def h5features_convert(self, infile):
        """Convert a h5features file to the latest version."""
        # TODO no need to read all data, just rename it
        # TODO test it !
        with h5py.File(infile, 'r') as f:
            groups = list(f.keys())

        for group in groups:
            self._writer.write(Reader(infile, group).read(),
                               self.groupname, append=True)
