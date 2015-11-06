"""Test top level functions of the h5features package."""

import numpy as np
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
    remove(filename)

# class TestLabels():
#     """Test labels other than 1D times stamps"""
#     def setup(self):
#         self.filename = 'test.h5'
#         self.nitems = 10
#         self.features = generate.features(self.nitems)
#         self.items = generate.items(self.nitems)

#     def teardown(self):
#         remove(self.filename)

#     def test_str(self):
#         labels = [np.array(['a'])] * self.nitems
#         data = h5f.Data(self.items, labels, self.features)
#         h5f.Writer(self.filename).write(data, 'group')
#         rdata = h5f.Reader(self.filename, 'group').read()
#         assert rdata == data
