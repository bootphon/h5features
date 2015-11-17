"""Test top level functions of the h5features package."""

import numpy as np
import h5features as h5f
from aux import generate
from aux.utils import remove

def test_from_exemple():
    filename = '/tmp/exemple.h5'
    remove(filename)
    a1, a2, a3 = generate.full(100)
    data = h5f.Data(a1, a2, a3)

    with h5f.Writer(filename) as w:
        w.write(data, 'group')

    with h5f.Reader(filename, 'group') as r:
        rdata = r.read()
        assert len(rdata.items()) == 100
        assert data == rdata
    remove(filename)

def test_rw_one_frame_2D():
    h5file = 'data.h5'
    gold = generate.full_data(1,3,1,2)
    remove(h5file)
    h5f.Writer(h5file).write(gold)
    test = h5f.Reader(h5file).read()
    assert test == gold
    remove(h5file)
