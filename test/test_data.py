"""Test of the h5features.data module."""

import numpy as np
from h5features.data import Data
import generate

class TestData:
    def setup(self):
        self.items = 'a b c d'.split()
        nitems = len(self.items)
        self.labels = [np.array([1, 2]) for _ in range(nitems)]
        self.features = [np.zeros((2, 10)) for _ in range(nitems)]

    def test_basic(self):
        data = Data(self.items, self.labels, self.features)
        assert data.items() == self.items
        assert data.labels() == self.labels
        assert data.features() == self.features
