"""Test of auxiliary functions of the h5features2 module.

@author: Mathieu Bernard
"""

import h5py
import pytest

from utils import remove, assert_raise
import generate
import h5features2 as h5f


class TestWriteAppendable:
    """Test of the _appendable() method."""

    def setup(self):
        # init default parameters
        self.filename = 'test.h5'
        self.group = 'features'
        self.datasets = ['files', 'times', 'features', 'file_index']
        self.dim = 20
        self.version = '1.0'
        self.tformat = 1

        # create a simple feature file
        items, times, feat = generate.full(10, dim=self.dim)

        self.features = h5f.features.Features(feat)
        self.times = h5f.times.Times(times)
        self.items = h5f.items.Items(items)
        self.items2 = h5f.items.Items([i+'2' for i in items])
        h5f.write.write(self.filename, self.group, items, times, feat)

        # read it with h5py
        self.f = h5py.File(self.filename, 'r')
        self.g = self.f.get(self.group)

    def teardown(self):
        self.f.close()
        remove(self.filename)

    def test_basic_works(self):
        w = h5f.writer.Writer(self.filename)
        w.is_compatible(self.g, {'features':self.features,
                                 'items':self.items2,
                                 'times':self.times})

    # TODO Not here
    def test_version(self):
        assert self.g.attrs['version'] == self.version

    # def test_group(self):
    #     with pytest.raises(IOError):
    #         w = h5f.writer.Writer(self.filename)
    #         w.is_appendable(self.g, None)

    # def test_bad_dim(self):
    #     with pytest.raises(IOError) as ioerror:
    #         h5f._need_to_append(
    #             self.f, self.group, self.datasets, self.h5format,
    #             self.h5dim+1, self.h5type, self.version, self.times)
    #     assert 'mismatch' in str(ioerror.value)
