"""Test h5features facilities related to time.

@author: Mathieu Bernard

"""

import generate
import h5features2

class TestTimes1D:
    def setup(self):
        self.files, self.times, self.features = generate.features(10)

    def teardown(self):
        pass

    # def test_
