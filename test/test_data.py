"""Test of the h5features.data module."""

import numpy as np
from h5features.data import Data
from aux import generate

class TestData:
    def setup(self):
        self.items = 'a b c d'.split()
        nitems = len(self.items)
        self.labels = [np.array([1, 2]) for _ in range(nitems)]
        self.features = [np.zeros((2, 10)) for _ in range(nitems)]
        self.data = Data(self.items, self.labels, self.features)

    def test_basic(self):
        assert self.data.items() == self.items
        assert self.data.labels() == self.labels
        assert self.data.features() == self.features

    def test_clear(self):
        for entry in self.data._entries.values():
            assert len(entry.data)
        self.data.clear()
        for entry in self.data._entries.values():
            assert not len(entry.data)

    def test_append(self):
        data2 = Data('e f g h'.split(), self.labels, self.features)
        self.data.append(data2)
        for entry in self.data._entries.values():
            assert len(entry.data) == 8
