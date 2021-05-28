"""Test of the h5features.index module."""

import h5py
import pytest
from .aux import generate
from .aux.utils import remove
from h5features import Data, index


class TestIndex:
    def setup(self):
        self.filename = 'test.h5'
        self.teardown()
        self.h5file = h5py.File(self.filename, 'w')
        self.group = self.h5file.create_group('group')

    def teardown(self):
        remove(self.filename)

    def test_create(self):
        index.create_index(self.group, 0.1)
        assert list(self.group.keys()) == ['index']

        # Exception is OSError for h5py<3.0 and ValueError for h5py>=3.0
        with pytest.raises(Exception) as err:
            index.create_index(self.group, 0.1)
        assert 'name already exists' in str(err.value).lower()

    def test_write(self):
        index.create_index(self.group, 0.1)

        items, times, features = generate.full(100, dim=5, max_frames=10)
        data = Data(items, times, features)
        index.write_index(data, self.group, append=False)
