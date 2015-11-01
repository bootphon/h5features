#!/usr/bin/env python
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
"""Provides functions to convert numpy files to the h5features format.

The numpy npz files must contains 2 arrays:

* a 1D-array named 'times'
* a 2D-array named 'features', the 'feature' dimension along the
  columns and the 'time' dimension along the lines

"""

import os
import numpy as np

from .h5features import write

def npz_to_h5features(path, files, h5_filename, h5_groupname, batch_size=500):
    """Append a list of npz files to a h5features file.

    Files must have a relative name to a directory precised by the 'path'
    argument.

    :param str path: Path of the directory where the numpy files are stored.

    :param list files: A list of paths to npz files to convert and append.

    :param str h5_filename: Path to the output h5features file.

    :param str h5_groupname: Name of the h5 group where to store the
        numpy files (use '/features/') for h5features files)

    :param int batch_size: Optional. Size of the writing buffer (in
        number of npz files).

    """
    features = []
    times = []
    internal_files = []
    i = 0
    for f in files:
        if i == batch_size:
            write(h5_filename, h5_groupname, internal_files, times, features)

            features = []
            times = []
            internal_files = []
            i = 0

        i = i+1
        data = np.load(os.path.join(path, f))
        features.append(data['features'])
        times.append(data['time'])
        internal_files.append(os.path.splitext(f)[0])

    if features:
        write(h5_filename, h5_groupname, internal_files, times, features)


def convert(npz_folder, h5_filename='./features.features'):
    """Append a folder of npz files into a h5features file.

    The npz files must be numpy ndarray files.

    :param str npz_folder: Path to the folder containing the npz files.

    :param str h5_filename: Path to the output h5features file.

    """
    files = os.listdir(npz_folder)
    npz_to_h5features(npz_folder, files, h5_filename, '/features/')


def main():
    """Command line API to convert npz files to the h5features format."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('npz_folder', help='folder containing the npz files '
                                           'to be converted')
    parser.add_argument('h5_filename',
                        help='desired path for the h5features file')
    args = parser.parse_args()
    convert(args.npz_folder, args.h5_filename)


if __name__ == '__main__':
    main()
