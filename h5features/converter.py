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

"""Converter between different h5features versions."""

import argparse
import h5py
import os
import numpy as np
import scipy.io as sio

from .data import Data
from .reader import Reader
from .writer import Writer

class Converter(object):
    """This class allows convertion from various formats to h5features."""
    def __init__(self, filename, groupname, chunk=0.1, nitems=500):
        self._writer = Writer(filename, chunk)
        self.groupname = groupname
        self.nitems = nitems
        self._data = None

    def _push(self, data):
        # if not self._data == None:
        #     self._data.append(data)
        # else:
        #     self._data = data

        # if len(self._data.items()) >= self.nitems:
        #     self._writer.write(self._data, self.groupname, append=True)
        #     self._data.clear()
        self._writer.write(data, self.groupname, append=True)

    # def __del__(self):
    #     # write any stored data before destroying the instance
    #     self.flush()
    #     self.close()

    # def flush(self):
    #     if self._data is not None and not self._data.is_empty():
    #         self._writer.write(self._data, self.groupname, append=True)

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
        self._push(Data([os.path.splitext(infile)[0]],
                        data['times'], data['features']))

    def mat_convert(self, infile):
        data = sio.loadmat(infile)
        labels = data['times'][0]
        features = data['features']
        #print('convert', labels.shape, features.shape)

        self._push(Data([os.path.splitext(infile)[0]],
                        [labels], [features]))

    def h5features_convert(self, infile):
        """Convert a h5features file to the latest version."""
        # find groups in file
        with h5py.File(infile, 'r') as f:
            groups = list(f.keys())

        for g in groups:
            self._push(Reader(infile, g).read())
