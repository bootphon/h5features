#!/usr/bin/env python3
"""Main script to test some h5features2 functionalities."""

import os
import h5features2
from h5features2.reader import Reader
from h5features2.writer import Writer

def main():

    # open a sample file v1.0 for reading
    rfile = os.path.abspath(
        os.path.join(os.path.dirname(h5features2.__file__),
                     '../test/data/mfcc.h5'))

    reader = Reader(rfile, 'features')
    print('version readed =', reader.version)
    print(reader.index.keys())

    i, t, f = reader.read()
    print(type(i.data), type(t.data), type(f.data))

    # write it to v1.1
    wfile = rfile.split('.')[0]+'.eraseme.h5'
    if os.path.exists(wfile):
        os.remove(wfile)
    writer = Writer(wfile)
    writer.write({'items':i, 'features':f, 'times':t}, 'features')
    print('version writed =', writer.version)

    # check compatibility
    iw, tw, fw = Reader(wfile, 'features').read()
    assert i.data == iw.data
    return t, tw
    # for ff1, ff2 in zip(f.data, fw.data):
    #     assert (ff1 == ff2).all()
    # assert t.data == tw.data

if __name__ == '__main__':
    main()
