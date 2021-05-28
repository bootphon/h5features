"""Test of the h5features.data module."""

import os
import pytest
import numpy as np
import h5features as h5f
from h5features.data import Data


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
        assert not self.data.is_empty()

    def test_clear(self):
        for entry in self.data._entries.values():
            assert len(entry.data)
        self.data.clear()
        assert self.data.is_empty()
        for entry in self.data._entries.values():
            assert not len(entry.data)

    def test_append(self):
        data2 = Data('e f g h'.split(), self.labels, self.features)
        self.data.append(data2)
        for entry in self.data._entries.values():
            assert len(entry.data) == 8

    @pytest.mark.parametrize(
        'mode, append',
        [(m, a) for m in ('a', 'w') for a in (True, False)])
    def test_const_on_write(self, tmpdir, mode, append):
        # A Data instance must not change before/after writing it to a group
        h5file = os.path.join(str(tmpdir) + 'test.h5')

        # first write
        assert self.data.items() == self.items
        h5f.Writer(h5file, mode=mode).write(self.data, append=append)
        assert self.data.items() == self.items
        assert h5f.Reader(h5file).read() == self.data

        # second write of the same data
        if mode == 'a' and append is True:
            with pytest.raises(IOError):
                h5f.Writer(h5file, mode=mode).write(self.data, append=append)
        else:
            h5f.Writer(h5file, mode=mode).write(self.data, append=append)
            assert self.data.items() == self.items
            assert h5f.Reader(h5file).read() == self.data


def test_bad_len():
    with pytest.raises(ValueError) as err:
        Data([1], [1], [1, 2])
    assert 'all entries must have the same length' in str(err)
