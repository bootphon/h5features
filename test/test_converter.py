"""Test of the converter module of the h5features package."""

from h5features.converter import Converter
from h5features.reader import Reader
from h5features.data import Data
from utils import remove
import generate
import scipy.io as sio
import numpy as np
import os

class TestConverterSimple:
    def setup(self):
        self.h5file = 'data.h5'
        self.matfile = 'data.mat'
        self.teardown()

    def teardown(self):
        remove(self.h5file)
        remove(self.matfile)

    def test_mat(self):
        # generate a unique item
        data = generate.full(1, 20, 30)

        # write it to a mat file
        sio.savemat(self.matfile, {'labels':data[1][0], 'features':data[2][0]})

        # check data conservation in mat file
        mat = sio.loadmat(self.matfile)
        assert (mat['labels'] == data[1][0]).all()
        assert (mat['features'] == data[2][0]).all()

        # convert it to h5features
        Converter(self.h5file, 'group').convert(self.matfile)
        rdata = Reader(self.h5file, 'group').read()

        # check convertion is correct
        assert rdata.items() == [os.path.splitext(self.matfile)[0]]
        assert (rdata.labels()[0] == data[1][0]).all()
        assert (rdata.features()[0] == data[2][0]).all()

    def test_2D_labels(self):
        data = generate.full(1, 5, 10, 2)
        sio.savemat(self.matfile, {'labels':data[1][0], 'features':data[2][0]})
        mat = sio.loadmat(self.matfile)
        assert (mat['labels'] == data[1][0]).all()
        assert (mat['features'] == data[2][0]).all()

        Converter(self.h5file, 'group').convert(self.matfile)
        rdata = Reader(self.h5file, 'group').read()
        assert rdata.items() == [os.path.splitext(self.matfile)[0]]
        assert (rdata.labels()[0] == data[1][0]).all()
        assert (rdata.features()[0] == data[2][0]).all()
        assert rdata == Data([os.path.splitext(self.matfile)[0]], data[1], data[2])


class TestMatFiles:
    def setup(self):
        self.nfiles = 10
        self.h5file = 'data.h5'
        self.matfiles = ['data_{}.mat'.format(i) for i in range(self.nfiles)]
        self.teardown()

    def teardown(self):
        remove(self.h5file)
        for m in self.matfiles:
            remove(m)

    def test_mat(self):
        # generate 10 items
        data = generate.full(self.nfiles, 10, 30)

        # write them in 10 mat files
        for i in range(self.nfiles):
            sio.savemat(self.matfiles[i],
                        {'labels':data[1][i], 'features':data[2][i]})

            # check data conservation in mat file
            mat = sio.loadmat(self.matfiles[i])
            assert (mat['features'] == data[2][i]).all()
            assert (mat['labels'] == data[1][i]).all()

        # convert it to h5features
        conv = Converter(self.h5file, 'group')
        for name in self.matfiles:
            conv.convert(name)
        conv.close()

        # check convertion is correct
        rdata = Reader(self.h5file, 'group').read()
        assert len(rdata.items()) == self.nfiles
        for i in range(self.nfiles):
            assert (rdata.labels()[i] == data[1][i]).all()
            assert (rdata.features()[i] == data[2][i]).all()

class TestNpz:
    def setup(self):
        self.nfiles = 10
        self.h5file = 'data.h5'
        self.matfiles = ['data_{}.npz'.format(i) for i in range(self.nfiles)]

    def teardown(self):
        remove(self.h5file)
        for m in self.matfiles:
            remove(m)

    def test_npz(self):
        # generate 10 items
        data = generate.full(self.nfiles, 10, 30)

        # write them in 10 mat files
        for i in range(self.nfiles):
            np.savez(self.matfiles[i],
                        labels=data[1][i], features=data[2][i])

            # check data conservation in mat file
            mat = np.load(self.matfiles[i])
            assert (mat['features'] == data[2][i]).all()
            assert (mat['labels'] == data[1][i]).all()

        # convert it to h5features
        conv = Converter(self.h5file, 'group')
        for name in self.matfiles:
            conv.convert(name)
        conv.close()

        # check convertion is correct
        rdata = Reader(self.h5file, 'group').read()
        assert len(rdata.items()) == self.nfiles
        for i in range(self.nfiles):
            assert (rdata.labels()[i] == data[1][i]).all()
            assert (rdata.features()[i] == data[2][i]).all()


    def test_2D_labels(self):
        data = generate.full(self.nfiles, 5, 10, 2)
        # write them in 10 mat files
        for i in range(self.nfiles):
            np.savez(self.matfiles[i],
                        labels=data[1][i], features=data[2][i])

        conv = Converter(self.h5file, 'group')
        for name in self.matfiles:
            conv.convert(name)
        conv.close()

        rdata = Reader(self.h5file, 'group').read()
        assert len(rdata.items()) == self.nfiles
        for i in range(self.nfiles):
            assert (rdata.labels()[i] == data[1][i]).all()
            assert (rdata.features()[i] == data[2][i]).all()

# class TestH5f():
#     def setup(self):
#         pass

#     def teardown(self):
#         pass
