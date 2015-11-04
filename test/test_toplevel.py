"""Test top level functions of the h5features package."""

import h5features as h5f
import generate
from utils import remove, assert_raise


def test_from_exemple():
    filename = '/tmp/exemple.h5'
    remove(filename)
    data = generate.full_dict(100)

    with h5f.Writer(filename) as w:
        w.write(data, 'group')

    with h5f.Reader(filename, 'group') as r:
        rdata = r.read()
        assert len(rdata['items'].data) == 100
        assert data == rdata
