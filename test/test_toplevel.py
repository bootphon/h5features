"""Test top level functions of the h5features package."""

import h5features as h5f
import generate
from utils import remove

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
