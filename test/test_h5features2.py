"""Test of the h5features2 module

@author: Mathieu Bernard
"""

import os
import numpy as np
import h5py

import h5features2 as h5f

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
        n_files = 30
        features = []
        times = []
        files = []
        for i in xrange(n_files):
            n_frames = np.random.randint(400)+1
            features.append(np.random.randn(n_frames, 20))
            times.append(np.linspace(0, 2, n_frames))
            files.append('File %d' % (i+1))

        h5f.write('test.h5', 'features', files, times, features)

        with h5py.File(self.filename, 'r') as f:
            assert 'features' in f.keys()
            g = f.get('features')
            assert g.keys() == [u'features', u'file_index', u'files', u'times']
            #assert g['features'].shape == (300,20)


# if __name__ == '__main__':
#     try:
#         test_write()

#         # concatenate to existing dataset
#         features_added_1 = np.zeros(shape=(1, 20))
#         times_added_1 = np.linspace(0, 2, 1)
#         h5f.write('test.h5', 'features', ['File 31'], [times_added_1], [features_added_1])
#         features_added_2 = np.zeros(shape=(2, 20))
#         times_added_2 = np.linspace(0, 2, 2)
#         h5f.write('test.h5', 'features', ['File 31'], [times_added_2], [features_added_2])

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
