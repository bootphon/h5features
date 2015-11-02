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
"""Converter between different h5features versions."""

import argparse
import os
from .reader import Reader
from .writer import Writer

def converter(filein, fileout, version='1.1', groupname='features',verb=False):
    """Convert a h5features file from a version to another.

    This function is a simple wrapper to a *Reader* and a *Writer*.
    """
    reader = Reader(filein, groupname)
    data = reader.read()
    if verb:
        print('version readed =', reader.version)

    if os.path.exists(fileout):
        os.remove(fileout)

    writer = Writer(fileout, version=version)
    writer.write(data, groupname, append=False)
    if verb:
        print('version writed =', writer.version)


def main():
    """Run a h5features converter from parsed arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='h5features input file to read')
    parser.add_argument('-g', '--group',
                        help='group in the file to convert',
                        default='features')
    parser.add_argument('-o', '--output',
                        help='h5features output file to write',
                        default=os.path.join(os.getcwd(), 'output.h5'))
    parser.add_argument('-v', '--version',
                        help='h5features version of the written file. '
                        "Either '1.1', '1.0' or '0.1'", default='1.1')

    args = parser.parse_args()
    converter(args.input, args.output, args.version, args.group)


if __name__ == '__main__':
    main()
