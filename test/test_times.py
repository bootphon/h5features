"""Test h5features facilities related to time.

@author: Mathieu Bernard

"""

import os

import generate
import h5features2.h5features2 as h5f

class TestTimes1D:
    """Testing writing 1D (i.e. center times of windows)"""

    def setup(self):
        self.filename = 'test.h5'
        self.files, self.times, self.features = generate.features(
            10, time_format=1)

    def teardown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_write(self):
        h5f.write(self.filename, 'group',
                  self.files, self.times, self.features)

        t, fe = h5f.read(self.filename)
        #assert t == self.times


class TestTimes2D:

    def setup(self):
        self.filename = 'test.h5'
        self.files, self.times, self.features = generate.features(
            10, time_format=2)

    def teardown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)
