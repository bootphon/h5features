#!/usr/bin/env python3
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
    read = reader.read()
    if verb:
        print('version readed =', reader.version)
        print('index keys are', list(reader.index.keys()))

    if os.path.exists(fileout):
        os.remove(fileout)

    writer = Writer(fileout, version=version)
    writer.write({'items':read[0], 'times':read[1], 'features':read[2]},
                 groupname=groupname, append=False)
    if verb:
        print('version writed =', writer.version)
        print('index keys are', list(writer.index.keys()))


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
