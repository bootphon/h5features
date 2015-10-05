"""Test of the h5features2 module

@author: Mathieu Bernard
"""

import os
import numpy as np
import h5py
import pytest

from ABXpy.misc.generate_data import feature as generate
import h5features2.h5features2 as h5f

def write_file(filename='test.h5', n_files=30, max_frames=400):
    features = []
    times = []
    files = []
    for i in xrange(n_files):
        n_frames = np.random.randint(max_frames)+1
        features.append(np.random.randn(n_frames, 20))
        times.append(np.linspace(0, 2, n_frames))
        files.append('File %d' % (i+1))

    h5f.write(filename, 'features', files, times, features)


class TestH5FeaturesCheckWriteArguments:
    """Test _check_write_arguments method."""

    def setup(self):
        self.features_format = 'dense'
        self.chunk_size = 0.1
        self.files, _, self.features = generate(10)

    def teardown(self):
        pass

    def test_features_format_good(self):
        for ff in ['dense', 'sparse']:
            h5f._check_write_arguments(ff, self.chunk_size,
                                       self.features, self.files)

    def test_features_format_bad(self):
        with pytest.raises(IOError) as ioerror:
            h5f._check_write_arguments('dance', self.chunk_size,
                                       self.features, self.files)
        assert 'features_format' in str(ioerror.value)

    def test_chunk(self):
        with pytest.raises(IOError) as ioerror:
            h5f._check_write_arguments(self.features_format, 0,
                                       self.features, self.files)
        assert 'chunk_size below 8Ko' in str(ioerror.value)

        for coef in [1, 0.1, 0.01, 0.008]:
            h5f._check_write_arguments(self.features_format, coef,
                                       self.features, self.files)

    def test_features_dim_good(self):
        fdim, _ = h5f._check_write_arguments(
            self.features_format, self.chunk_size, self.features, self.files)
        assert fdim == 2

    def test_features_dim_bad(self):
        _, _, bad_features  = generate(10)
        bad_features[5] = bad_features[5][:,:-1]

        with pytest.raises(IOError) as ioerror:
            h5f._check_write_arguments(
                self.features_format, self.chunk_size, bad_features, self.files)
        assert ' the same feature dimension' in str(ioerror.value)

        with pytest.raises(IndexError):
            h5f._check_write_arguments(
                self.features_format, self.chunk_size,
                [np.array([1,2,3]),np.array([1,2])], self.files)

    def test_features_empty(self):
        with pytest.raises(IOError) as ioerror:
            h5f._check_write_arguments(
                self.features_format, self.chunk_size,
                [np.array([]),np.array([])], self.files)
        assert ' files must be non-empty' in str(ioerror.value)

    def test_features_dim_zero(self):
        pass




class TestH5FeaturesWrite:
    """Test write methods."""

    def setup(self):
        self.filename = 'test.h5'
        self.features_0 = np.random.randn(300, 20)
        self.times_0 = np.linspace(0, 2, 300)

    def teardown(self):
        try:
            os.remove(self.filename)
        except:
            pass

    def test_simple_write(self):
        h5f.simple_write(self.filename, 'features_0',
                         self.times_0, self.features_0)

        with h5py.File(self.filename, 'r') as f:
            assert 'features_0' in f.keys()
            g = f.get('features_0')
            assert g.keys() == [u'features', u'file_index', u'files', u'times']
            assert g['features'].shape == (300,20)

    def test_write(self):
        write_file()
        with h5py.File(self.filename, 'r') as f:
            assert 'features' in f.keys()
            g = f.get('features')
            assert g.keys() == [u'features', u'file_index', u'files', u'times']
            assert g.get('features').shape[1] == 20
            assert g.get('files').shape == (30,)

    def test_concatenate(self):
        """concatenate to existing dataset"""
        write_file()
        features_added_1 = np.zeros(shape=(1, 20))
        times_added_1 = np.linspace(0, 2, 1)
        h5f.write('test.h5', 'features', ['File 31'],
                  [times_added_1], [features_added_1])

        features_added_2 = np.zeros(shape=(2, 20))
        times_added_2 = np.linspace(0, 2, 2)
        h5f.write('test.h5', 'features', ['File 31'],
                  [times_added_2], [features_added_2])

# if __name__ == '__main__':
#     try:
#         test_write()


#         # read
#         times_0_r, features_0_r = h5f.read('test.h5', 'features_0')
#         assert times_0_r.keys() == ['features']
#         assert features_0_r.keys() == ['features']
#         assert all(times_0_r['features'] == times_0)
#         assert all(features_0_r['features'] == features_0)

#         times_r, features_r = h5f.read('test.h5', 'features')
#         assert set(times_r.keys()) == set(files+['File 31'])
#         assert set(features_r.keys()) == set(files+['File 31'])
#         for i, f in  enumerate(files):
#             assert all(times_r[f] == times[i])
#             assert all(features_r[f] == features[i])
#             assert all(times_r['File 31'] == np.concatenate([times_added_1, times_added_2]))
#             assert all(features_r['File 31'] == np.concatenate([features_added_1, features_added_2], axis=0))
#             #FIXME test smaller reads

#     finally:
