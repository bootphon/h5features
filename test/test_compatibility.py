"""Test compatibility of different versions of h5features."""

import h5py
import os

from generate import features as generate
from ABXpy.misc import compare
import h5features              as h5f_v1
import h5features2.h5features2 as h5f_v2

class TestReadWriteCompatibility:
    """Test that v1 and v2 behave equally."""

    def setup(self):
        self.file_v1 = 'v1.h5'
        self.file_v2 = 'v2.h5'
        self.teardown() # in case files already exist, remove it

        self.items, self.times, self.features = generate(20,10)
        h5f_v1.write(self.file_v1, 'features', self.items, self.times,
                     self.features)

        h5f_v2.write(self.file_v2, 'features', self.items, self.times,
                     self.features)

    def teardown(self):
        try:
            os.remove(self.file_v1)
            os.remove(self.file_v2)
        except:
            pass

    # silly test
    def test_files_exists(self):
        assert os.path.exists(self.file_v1)
        assert os.path.exists(self.file_v2)

    def test_write_works(self):
        assert compare.h5cmp(self.file_v1, self.file_v1)

    def test_read_works(self):
        fname = self.file_v1
        t1, f1 = h5f_v1.read(fname)
        t2, f2 = h5f_v2.read(fname)

        for tt1, tt2 in zip(t1,t2):
            assert tt1 == tt2
        for ff1, ff2 in zip(f1,f2):
            assert ff1 == ff2
