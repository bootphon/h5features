"""Test of auxiliary functions of the h5features2 module.

@author: Mathieu Bernard
"""

import h5py
import os
import numpy as np
import pytest

from ABXpy.misc.generate_data import feature as generate_features
import h5features2.h5features2 as h5f

class TestCheckWriteFilename:
    """Test _append_existing_file method."""
    def setup(self):
        self.filename = 'test.h5'
        self.group = 'features'
        self.teardown()

    def teardown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_no_file(self):
        with pytest.raises(IOError) as ioerror:
            h5f._check_write_filename('/path/to/non/existant/file', self.group)
        assert 'No such file' in str(ioerror.value)

    def test_nohdf5_file(self):
        with open(self.filename,'w') as f:
            f.write('This is not a HDF5 file')

        with pytest.raises(IOError) as ioerror:
            h5f._check_write_filename(self.filename, self.group)
        assert 'not an HDF5 file' in str(ioerror.value)

    def test_good(self):
        generate_features(10, name=self.filename, group=self.group)
        assert h5f._check_write_filename(self.filename, self.group)


class TestCheckWriteArguments:
    """Test _check_write_arguments method."""

    def setup(self):
        self.filename = ''
        self.group = 'features'
        self.features_format = 'dense'
        self.chunk_size = 0.1
        self.files, _, self.features = generate_features(10)

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

    def test_chunk_size(self):
        with pytest.raises(IOError) as ioerror:
            h5f._check_write_arguments(self.features_format, 0,
                                       self.features, self.files)
        assert 'chunk_size below 8Ko' in str(ioerror.value)

        for coef in [1, 0.1, 0.01, 0.008]:
            h5f._check_write_arguments(self.features_format, coef,
                                       self.features, self.files)

    def test_features_dim_good(self):
        fdim, _ = h5f._check_write_arguments(self.features_format,
                                                self.chunk_size,
                                                self.features,
                                                self.files)
        assert fdim == 2

    def test_features_dim_bad(self):
        _, _, bad_features  = generate_features(10)
        bad_features[5] = bad_features[5][:,:-1]

        with pytest.raises(IOError) as ioerror:
            h5f._check_write_arguments(self.features_format,
                                       self.chunk_size, bad_features,
                                       self.files)
        assert ' the same feature dimension' in str(ioerror.value)

        with pytest.raises(IndexError):
            h5f._check_write_arguments(self.features_format, self.chunk_size,
                [np.array([1,2,3]),np.array([1,2])], self.files)

    def test_features_empty(self):
        with pytest.raises(IOError) as ioerror:
            h5f._check_write_arguments(self.features_format,
                                       self.chunk_size,
                                       [np.array([]),np.array([])],
                                       self.files)
        assert ' files must be non-empty' in str(ioerror.value)

    # def test_features_dim_zero(self):
    #     pass

class TestCheckAppendable:
    """Test of the _check_write_appendable() method."""
    def setup(self):
        # create a simple feature file
        self.filename = 'test.h5'
        generate_features(10,name=self.filename)

        # read it with h5py
        self.f = h5py.File(self.filename, 'r')
        self.g = self.f.get('features')

    def teardown(self):
        self.f.close()
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    # TODO Not here
    def test_version(self):
        assert self.g.attrs['version'] == '1.0'

    def test_format(self):
        pass
