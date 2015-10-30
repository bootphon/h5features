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
"""Profiling and stress test of the h5features package."""

import os
import timeit

import generate
import h5features      as h5f_11
import h5features_v1_0 as h5f_10
from utils import remove

# generate artificial data
nitems, dim, max_frames = 10000, 20, 500
class data: pass
data.items, data.times, data.features = generate.full(nitems, dim, max_frames)
data.filename = 'test.h5'
data.groupname = 'group'

v10_setup = """\
import h5features_v1_0 as h5f
from utils import remove
from __main__ import data
"""

v11_setup = """\
import h5features as h5f
from utils import remove
from __main__ import data
"""

write = """\
remove(data.filename)
h5f.write(data.filename, data.groupname, data.items, data.times, data.features)
"""
read = "h5f.read(data.filename, data.groupname)"

if __name__ == '__main__':
    number = 1
    repeat = 10

    print('On writing')
    print('timeit v1.0: ', min(timeit.repeat(
        write, setup=v10_setup, number=number, repeat=repeat)))
    print('timeit v1.1: ', min(timeit.repeat(
        write, setup=v11_setup, number=number, repeat=repeat)))

    remove(data.filename)
    h5f_10.write(data.filename, data.groupname,
                 data.items, data.times, data.features)

    print('On reading')
    print('timeit v1.0: ', min(timeit.repeat(
        read, setup=v10_setup, number=number, repeat=repeat)))

    remove(data.filename)
    h5f_11.write(data.filename, data.groupname,
                 data.items, data.times, data.features)

    print('timeit v1.1: ', min(timeit.repeat(
        read, setup=v11_setup, number=number, repeat=repeat)))
    remove(data.filename)
