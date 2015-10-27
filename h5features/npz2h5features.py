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

- a 1D-array named 'times'
- a 2D-array named 'features', the 'feature' dimension along the
 columns and the 'time' dimension along the lines

"""
# -*- coding: utf-8 -*-
"""
Created on Fri May  2 09:33:20 2014

@author: Thomas Schatz
"""
import os
import numpy as np
import h5features

def npz_to_h5features(path, files, h5_filename, h5_groupname, batch_size=500):
    """Append a list of npz files to a h5features file.

    Files must have a relative name to a directory precised by the 'path'
    argument.

    Parameters
    ----------
    path : str
        Path of the directory where the numpy files are stored.
    files : list of filename
        List of file to convert and append.
    h5_filename : filename
        The output h5features file.
    h5_groupname : str
        Name of the h5 group where to store the numpy files (use '/features/')
        for h5features files)
    batch_size : int
        Size of the writing buffer (in number of npz files). By default 500.
    """
    features = []
    times = []
    internal_files = []
    i = 0
    for f in files:
        if i == batch_size:
            h5features.write(
                h5_filename, h5_groupname, internal_files, times, features)

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
        h5features.write(
            h5_filename, h5_groupname, internal_files, times, features)


def convert(npz_folder, h5_filename='./features.features'):
    """Append a folder of numpy ndarray files in npz format into a h5features
    file.

    Parameters
    ----------
    npz_folder : dirname
        The folder containing the npz files to convert.
    h5_filename : filename
        The output h5features file.
    """
    files = os.listdir(npz_folder)
    npz_to_h5features(npz_folder, files, h5_filename, '/features/')


# detects whether the script was called from command-line
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('npz_folder', help='folder containing the npz files '
                                           'to be converted')
    parser.add_argument('h5_filename',
                        help='desired path for the h5features file')
    args = parser.parse_args()
    convert(args.npz_folder, args.h5_filename)
