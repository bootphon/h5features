"""Test of read/write facilities of the h5features2 module.

@author: Mathieu Bernard
"""

import os
import numpy as np
import h5py
import pytest

import h5features2.h5features2 as h5f
import generate

def test_raise_on_write_sparse():
    with pytest.raises(NotImplementedError) as ioerror:
        h5f.write('test.h5', 'group', None, None, None, features_format='sparse')
    assert 'sparse' in str(ioerror.value)

class TestH5FeaturesWrite:
    """Test write methods."""

    def setup(self):
        self.filename = 'test.h5'
        self.teardown()

    def teardown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_bad_file(self):
        with pytest.raises(IOError) as ioerror:
            h5f.write('/silly/path/to/no/where.h5', 'group', [], [], [])
        msg = str(ioerror.value)
        assert '/silly/path' in msg
        assert 'No such file' in msg

    def test_bad_file2(self):
        with open(self.filename, 'w') as f:
            f.write('This is not a HDF5 file')

        with pytest.raises(IOError) as ioerror:
            h5f.write(self.filename, 'group', [], [], [])
        msg = str(ioerror.value)
        assert self.filename in msg
        assert 'not an HDF5 file' in msg

    def test_simple_write(self):
        self.features_0 = np.random.randn(300, 20)
        self.times_0 = np.linspace(0, 2, 300)

        h5f.simple_write(self.filename, 'f',
                         self.times_0, self.features_0)

        with h5py.File(self.filename, 'r') as f:
            assert ['f'] == list(f.keys ())

            g = f.get('f')
            assert list(g.keys()) == (
                ['features', 'file_index', 'files', 'times'])

            assert g['features'].shape == (300,20)
            assert g['file_index'].shape == (1,)
            assert g['files'].shape == (1,)
            assert g['times'].shape == (300,)

    def test_write(self):
        files, times, features = generate.features(30, 20, 10)
        h5f.write(self.filename, 'f', files, times, features)

        with h5py.File(self.filename, 'r') as f:
            assert ['f'] == list(f.keys ())
            g = f.get('f')
            assert list(g.keys()) == ['features', 'file_index', 'files', 'times']
            assert g.get('features').shape[1] == 20
            assert g.get('file_index').shape == (30,)
            assert g.get('files').shape == (30,)
            assert g.get('features').shape[0] == g.get('times').shape[0]


class TestH5FeaturesReadWrite:
    """Test more advanced read/write facilities."""

    def setup(self):
        self.filename = 'test.h5'
        self.group = 'features_0'

    def teardown(self):
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def test_concatenate(self):
        """Cconcatenate to existing dataset.

        This is a legacy test from h5features v 1.0.

        """
        group = self.group
        filename = self.filename

        features_0 = np.random.randn(300, 20)
        times_0 = np.linspace(0, 2, 300)
        h5f.simple_write(filename, group, times_0, features_0)

        n_files = 30
        features = []
        times = []
        files = []
        for i in range(n_files):
            n_frames = np.random.randint(400)+1
            features.append(np.random.randn(n_frames, 20))
            times.append(np.linspace(0, 2, n_frames))
            files.append('File %d' % (i+1))
        h5f.write(filename, 'features', files, times, features)
        # files, times, features = generate.features(30, 20, 400)
        # h5f.write(filename, 'features_0', files, times, features)

        # concatenate to existing dataset
        features_added_1 = np.zeros(shape=(1, 20))
        times_added_1 = np.linspace(0, 2, 1)
        h5f.write(filename, 'features', ['File 31'],
                  [times_added_1], [features_added_1])

        features_added_2 = np.zeros(shape=(2, 20))
        times_added_2 = np.linspace(0, 2, 2)
        h5f.write(filename, 'features', ['File 31'],
                  [times_added_2], [features_added_2])

        # read
        times_0_r, features_0_r = h5f.read(filename, group)
        assert list(times_0_r.keys ()) == ['features']
        assert list(features_0_r.keys ()) == ['features']
        assert all(times_0_r['features'] == times_0)
        assert (features_0_r['features'] == features_0).all()

        times_r, features_r = h5f.read(filename, 'features')
        assert set(times_r.keys()) == set(files+['File 31'])
        assert set(features_r.keys()) == set(files+['File 31'])

        for i, f in  enumerate(files):
            assert all(times_r[f] == times[i])
            assert (features_r[f] == features[i]).all()

            assert all(times_r['File 31'] ==
                       np.concatenate([times_added_1, times_added_2]))

            assert (features_r['File 31'] ==
                    np.concatenate([features_added_1,
                                    features_added_2], axis=0) ).all()
