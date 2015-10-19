#!/usr/bin/env python3
"""Converter between different h5features versions."""

import argparse
import os
import h5features2
from h5features2.reader import Reader
from h5features2.writer import Writer

def converter(filein, fileout, version='1.1', groupname='features',verb=False):
    reader = Reader(filein, 'features')
    reed = reader.read()
    if verb:
        print('version readed =', reader.version)
        print('index keys are', list(reader.index.keys()))

    if os.path.exists(fileout):
        os.remove(fileout)

    writer = Writer(fileout, version=version)
    writer.write({'items':reed[0], 'times':reed[1], 'features':reed[2]},
                 groupname=groupname, append=False)
    if verb:
        print('version writed =', writer.version)
        print('index keys are', list(writer.index.keys()))

        # TODO check compatibility
        # for stuf in zip(reed, wrote):
        #     assert stuff[0] == stuff[1]

def main():
    """Run a h5features2 converter from parsed arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='h5features input file to read')
    parser.add_argument('-o', '--output',
                        help='h5features output file to write',
                        default=os.path.join(os.getcwd(), 'output.h5'))
    parser.add_argument('-v', '--version',
                        help="h5features version of the written file."
                        " In '1.1', '1.0', '0.1'", default='1.1')

    args = parser.parse_args()
    converter(args.input, args.output, args.version)

if __name__ == '__main__':
    main()
