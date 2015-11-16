import os
import h5py
import h5features as h5f
import numpy as np
import scipy.io as sio
from utils import remove
import generate


class TestOneFrame2D:
    def setup(self):
        self.h5file = 'data.h5'
        self.matfile = 'data.mat'
        self.teardown()

        self.data = h5f.Data(['item'], [np.array([[0., 1.]])],
                             [np.array([[0, 0, 0]])])
        self.labels = self.data.labels()[0]

        sio.savemat(self.matfile,
                    {'labels':self.labels,
                     'features':self.data.features()[0]})

    def teardown(self):
        remove(self.h5file)
        remove(self.matfile)

    def test_basic(self):
        assert self.labels.ndim == 2

    def test_labels_ok_in_mat(self):
        data = sio.loadmat(self.matfile)['labels']
        assert (self.labels == data).all()

    def test_convert_writed(self):
        # BUG (1,2) is writed as (2,1)
        h5f.Converter(self.h5file, 'group').convert(self.matfile)
        writed =  h5py.File(self.h5file, 'r')['group']['labels'][...]
        assert (writed == self.labels).all() # is it what I want?

    def test_rw(self):
        h5f.Writer(self.h5file).write(self.data)
        labels = h5f.Reader(self.h5file).read().labels()
        assert len(labels) == 1
        labels = labels[0]
        assert labels.ndim == 2
        assert labels.shape == (1,2)
        assert (self.labels == labels).all()

    def test_convert_read(self):
        h5f.Converter(self.h5file, 'group').convert(self.matfile)
        labels = h5f.Reader(self.h5file, 'group').read().labels()
        assert len(labels) == 1
        labels = labels[0]
        assert labels.ndim == 2
        assert labels.shape == (1,2)
        assert (self.labels == labels).all()


# def test_rw_one_frame_2D():
#     h5file = 'data.h5'
#     gold = generate.full_data(1,3,1,2)
#     remove(h5file)
#     h5f.Writer(h5file).write(gold)
#     test = h5f.Reader(h5file).read()
#     assert test == gold


# def test_label_one_frame_2D():
#     from h5features.labels import Labels
#     gold = np.array([[0, 1, 2]])
#     label = Labels([gold])
#     assert isinstance(label.data, list)
#     assert len(label.data) == 1

#     test = label.data[0]
#     assert isinstance(test, np.ndarray)
#     assert test.ndim == gold.ndim
#     assert test.shape == gold.shape
#     assert (test == gold).all()
