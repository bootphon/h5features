"""Test the chunk facilities in the h5features module."""

import h5py

import generate
from utils import remove
from h5features.dataset.items import Items


class TestChunk:
    def setup(self):
        self.filename = 'chunk.h5'
        self.h5file = h5py.File(self.filename, 'w')
        self.group = self.h5file.create_group('group')

    def teardown(self):
        self.h5file.close()
        remove(self.filename)

    def test_items(self):
        items = Items(generate.items(10))
        items.create_dataset(self.group, 0.1)
        assert self.group[items.name].chunks == (5000,)

    # def test_float(self):
    #     dtype = np.float64
