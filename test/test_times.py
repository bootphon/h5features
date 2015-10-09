"""Test h5features facilities related to time.

@author: Mathieu Bernard

"""

import h5py
import os

import generate
import h5features2.h5features2 as h5f


class TestTimes:

    def setup(self):
        self.filename = 'test.h5'
        self.group = 'group'
        self.nbitems = 100

    def teardown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_wr_1D(self):
        self._test_wr(1)

    # def test_wr_2D(self):
    #     self._test_wr(2)

    # This function is prefixed by an in underscore so that it is not
    # detected by py.test as a test function.
    def _test_wr(self, time_format):
        """Test retrieving times and files after a write/read operation."""
        files, t_gold, feat = generate.features(
            self.nbitems, time_format=time_format)

        h5f.write(self.filename, self.group, files, t_gold, feat)
        t, _ = h5f.read(self.filename, self.group)

        assert len(t) == self.nbitems

        # build a dict from gold to compare with t
        d = {}
        for k, v in zip(files, t_gold):
            d[k] = v

        # compare the two dicts
        for dd, tt in zip(d, t):
            assert tt == dd
