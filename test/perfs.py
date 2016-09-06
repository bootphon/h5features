#!/usr/bin/env python
# Copyright 2014-2016 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
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

"""Comparing execution times of h5features 1.0 and 1.1 versions."""

import argparse
import cProfile
import os
import timeit

from aux import generate
import aux.h5features_v1_0 as h5f
from aux.utils import remove


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--nitems',
                        help='number of items to generate',
                        default=10000, type=int)

    parser.add_argument('-d', '--dimension',
                        help='features dimension',
                        default=20, type=int)

    parser.add_argument('-f', '--max_frames',
                        help='maximal number of frames per items',
                        default=10, type=int)

    parser.add_argument('-n', '--ntimes',
                        help='number of times each operation is timed',
                        default=10, type=int)

    parser.add_argument('-r', '--repeat',
                        help='number of repetitions (lowest time is resulted)',
                        default=3, type=int)

    return parser.parse_args()


def timeme(cmd, setup, args):
    return min(timeit.repeat(
        cmd, setup=setup, number=args.ntimes, repeat=args.repeat))


if __name__ == '__main__':
    args = parse_args()
    print('Parameters are i={}, d={}, f={}, n={}, r={}'
          .format(args.nitems, args.dimension, args.max_frames,
                  args.ntimes, args.repeat))

    data = generate.full_data(args.nitems, args.dimension, args.max_frames)
    filename = 'test.h5'
    groupname = 'group'

    v10_setup = """\
import aux.h5features_v1_0 as h5f
from aux.utils import remove
from __main__ import data, filename, groupname
    """
    v10_write = """\
remove(filename)
h5f.write(filename, groupname, data.items(), data.labels(), data.features())
    """
    v11_setup = """\
import h5features as h5f
from aux.utils import remove
from __main__ import data, filename, groupname
    """
    v11_write = """\
remove(filename)
h5f.Writer(filename).write(data, groupname)
    """
    read = "h5f.read(filename, groupname)"

    print('Writing:')
    print('  1.0: ', timeme(v10_write, v10_setup, args))
    print('  1.1: ', timeme(v11_write, v11_setup, args))

    print('Reading:')
    remove(filename)
    h5f.write(
        filename, groupname, data.items(), data.labels(), data.features())
    print('  1.0: ', timeme(read, v10_setup, args))
    print('  1.1: ', timeme(read, v11_setup, args))

    # cProfile.run(v10_setup + '\n' + v10_write, 'stats0')
    # remove(data['filename'])

    # cProfile.run(v11_setup + '\n' + v11_write, 'stats1')
    # remove(data['filename'])
