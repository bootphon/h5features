"""Test compatibility of different versions of h5features."""

import os

from ABXpy.misc.generate_data import feature as generate
import h5features  as h5f_v1
import h5features2 as h5f_v2

class TestWriteCompatibility:
    """Test that v1 and v2 behave equally when writting."""

    def setup(self):
        self.file_v1 = 'v1.h5'
        self.file_v2 = 'v2.h5'
        self.items, self.times, self.features = generate(10)

        h5f_v1.write(self.file_v1,
                     'features', self.items, self.times, self.features)

        h5f_v2.write(self.file_v2,
                     'features', self.items, self.times, self.features)

    def teardown(self):
        try:
            os.remove(self.file_v1)
            os.remove(self.file_v2)
        except:
            pass

    def test_exists(self):
        assert os.path.exists(self.file_v1)
        assert os.path.exists(self.file_v2)
