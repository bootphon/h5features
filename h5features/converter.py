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
    """This class allows convertion from various formats to h5features.

    * A *Converter* instance owns an h5features file and write converted
      input files to it, in a specified group.

    * An input file is converted to h5fatures using the *convert*
      method, which choose a concrete conversion method based on the
      input file extension.

    * Supported extensions are:

        * **.npz** for numpy NPZ files

        * **.mat** for Octave/Matlab files

        * **.h5** for h5features files. In this later case, the files
            are simply converted to latest version of the h5features
            data format


    :param str filename: The h5features to write in.
    :param str groupname: The group to write in *filename*
    :param float chunk: Size a chunk in *filename*, in MBytes.

    """
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
        """Close the converter and release the owned h5features file."""
        self._writer.close()

    def convert(self, infile):
        """Convert an input file to h5features based on its extension.

        :raise IOError: if *infile* is not a valid file.
        :raise IOError: if *infile* extension is not supported.

        """
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
        """Convert a numpy NPZ file to h5features."""
        data = np.load(infile)
        item = os.path.splitext(infile)[0]
        labels = self._labels(data)
        features = data['features']
        self._write(item, labels, features)

    def mat_convert(self, infile):
        """Convert a Octave/Matlab file to h5features."""
        data = sio.loadmat(infile)
        item = os.path.splitext(infile)[0]
        labels = self._labels(data)
        labels = labels[0] if labels.shape[0] == 1 else labels
        features = data['features']
        self._write(item, labels, features)

    def h5features_convert(self, infile):
        """Convert a h5features file to the latest h5features version."""
        with h5py.File(infile, 'r') as f:
            groups = list(f.keys())

        for group in groups:
            self._writer.write(Reader(infile, group).read(),
                               self.groupname, append=True)
