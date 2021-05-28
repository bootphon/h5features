"""Test compatibility of different versions of h5features."""

import h5py
import os

from .aux.utils import remove, h5cmp
from .aux import generate
from .aux import h5features_v1_0 as h5f_1_0
import h5features as h5f_1_1


class TestReadWriteCompatibility:
    """Test that v1.0 and v1.1 behave equally."""

    def setup(self):
        self.file_v1 = 'v1.0.h5'
        self.file_v2 = 'v1.1.h5'
        self.teardown()  # in case files already exist, remove it

        items, times, features = generate.full(20, 10)
        h5f_1_0.write(self.file_v1, 'features', items, times, features)
        h5f_1_1.write(self.file_v2, 'features', items, times, features,
                      chunk_size=0.1)

    def teardown(self):
        remove(self.file_v1)
        remove(self.file_v2)

    # silly test
    def test_files_exists(self):
        assert os.path.exists(self.file_v1)
        assert os.path.exists(self.file_v2)

    def test_write_works(self):
        assert h5cmp(self.file_v1, self.file_v1)

    def test_chunks(self):
        g1 = h5py.File(self.file_v1, 'r')['features']
        g2 = h5py.File(self.file_v2, 'r')['features']
        for k1, k2 in zip('times file_index files features'.split(),
                          'labels index items features'.split()):
            # print(k1, '/', k2)
            chunk1 = g1[k1].chunks
            chunk2 = g2[k2].chunks
            assert chunk1 == chunk2

    def test_read_works(self):
        fname = self.file_v1
        t1, f1 = h5f_1_0.read(fname, 'features')
        # keys read as bytes instead of str because of h5py>=3.0
        t1 = {k.decode() if isinstance(k, bytes) else k: v
              for k, v in t1.items()}
        f1 = {k.decode() if isinstance(k, bytes) else k: v
              for k, v in f1.items()}

        t2, f2 = h5f_1_1.read(fname, 'features')

        for tt1, tt2 in zip(t1, t2):
            assert tt1 == tt2
        for ff1, ff2 in zip(f1, f2):
            assert ff1 == ff2
