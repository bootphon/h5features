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
        self.data = generate.full_data(1, 3, 1, 2)
        self.teardown()

    def teardown(self):
        remove(self.h5file)
        remove(self.matfile)
    
    def test_labels_ok_in_mat(self):
        sio.savemat(self.matfile,
                    {'labels':self.data.labels()[0],
                     'features':self.data.features()[0]})

        data = sio.loadmat(self.matfile)['labels']
        data = data[0] if data.shape[0] == 1 else data
        assert (self.data.labels()[0] == data).all()

    def test_mat_convert(self):
        sio.savemat(self.matfile,
                    {'labels':self.data.labels()[0],
                     'features':self.data.features()[0]})

        # BUG (1,2) is writed as (2,1)
        h5f.Converter(self.h5file, 'group').convert(self.matfile)
        writed =  h5py.File(self.h5file, 'r')['group']['labels'][...]
        assert (writed == self.data.labels()[0]).all() # is it what I want?

    def test_rw(self):
        h5f.Writer(self.h5file).write(self.data)
        data = h5f.Reader(self.h5file).read()
        print(self.data.labels()[0])
        print(data.labels()[0])
        assert self.data._entries['features'] == data._entries['features']
        assert (self.data.labels()[0] == data.labels()[0]).all()
        assert self.data == data
        
        print('gold:\n', self.data.labels()[0])
        print('read:', data.labels()[0].shape, '\n', data.labels()[0])
        

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
    
