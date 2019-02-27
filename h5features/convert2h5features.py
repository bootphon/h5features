#!/usr/bin/env python
#
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

"""Script converting files in various formats to a single h5features file."""

import argparse
import h5features as h5f


def parse_args():
    """Define and parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='''Convert a set of files to a single h5features file, input files
        can be npz (numpy) or mat (MATLAB) files.''')

    parser.add_argument('file', nargs='+', type=str,
                        help='File to convert in the h5features format')

    parser.add_argument('-o', '--output', default='features.h5', type=str,
                        help='''The output h5features file to write on
                        (default is %(default)s)''')

    parser.add_argument('-g', '--group', default='h5features', type=str,
                        help='''The group to write in the output file
                        (default is %(default)s)''')

    parser.add_argument('--chunk', default=0.1, type=float,
                        help='''size of a file chunk in MB
                        (default is %(default)s)''')

    return parser.parse_args()


def main():
    """Main function of the converter command-line tool,
    ``convert2h5features --help`` for a more complete doc."""
    args = parse_args()
    converter = h5f.Converter(args.output, args.group, args.chunk)
    for infile in args.file:
        converter.convert(infile)


if __name__ == '__main__':
    main()
