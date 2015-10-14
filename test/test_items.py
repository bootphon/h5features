"""Test of the h5features2.items module.

@author: Mathieu Bernard <mmathieubernardd@gmail.com>
"""

import h5py

import generate
from utils import assert_raise, remove
from h5features2.items import Items


class TestItemsInit:
    """Test of Items.__init__ and Items.check."""
    def test_good(self):
        args = [['a'], ['a', 'b'], [1], [1, 2]]
        for arg in args:
            assert arg == Items(arg).data

    def test_bad(self):
        args = [[1, 1], [1, 2, 2], ['a', 'b', 'c', 'a']]
        msg = 'all items must have different names.'
        for arg in args:
            assert_raise(Items, arg, msg)

class TestCreate:
    """Test of Items.create."""
    def setup(self):
        self.filename = 'test.h5'
        self.group = h5py.File(self.filename, 'w').create_group('group')
        self.items = Items(generate.items(10))

    def teardown(self):
        remove(self.filename)

    def test_create(self):
        self.items.create(self.group, 10)
        assert list(self.group.keys()) == ['items']

        group = self.group['items']
        assert group.name.split('/')[2] == 'items'
        assert group.shape == (0,)
        assert group.chunks == (10,)
        assert group.maxshape == (None,)
        assert group.dtype == type(str)

    def test_continue_last(self):
        # TODO
        pass

    def test_write(self):
        self.items.create(self.group, 10)
        self.items.write(self.group)
        writes = self.group[self.items.name][...]

        assert len(writes) == 10
        assert self.items.data == list(writes)

    def test_writetwice(self):
        pass
