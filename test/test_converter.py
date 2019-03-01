"""Test of the converter module of the h5features package."""

import h5features as h5f
import h5py

from .aux.utils import remove
from .aux import generate

import scipy.io as sio
import numpy as np
import os
import pytest


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
        data = generate.full_data(1, 20, 10)

        # write it to a mat file
        sio.savemat(
            self.matfile,
            {'labels': data.labels()[0], 'features': data.features()[0]})

        # check data conservation in mat file
        mat = sio.loadmat(self.matfile)
        assert (mat['labels'] == data.labels()[0]).all()
        assert (mat['features'] == data.features()[0]).all()

        # convert it to h5features
        h5f.Converter(self.h5file, 'group').convert(self.matfile)
        rdata = h5f.Reader(self.h5file, 'group').read()

        # check convertion is correct
        assert rdata.items() == [os.path.splitext(self.matfile)[0]]
        assert (rdata.labels()[0] == data.labels()[0]).all()
        assert (rdata.features()[0] == data.features()[0]).all()

    def test_2D_labels(self):
        data = generate.full(1, 5, 10, 2)
        sio.savemat(
            self.matfile,
            {'labels': data[1][0], 'features': data[2][0]})
        mat = sio.loadmat(self.matfile)
        assert (mat['labels'] == data[1][0]).all()
        assert (mat['features'] == data[2][0]).all()

        h5f.Converter(self.h5file, 'group').convert(self.matfile)
        rdata = h5f.Reader(self.h5file, 'group').read()
        assert rdata.items() == [os.path.splitext(self.matfile)[0]]
        assert (rdata.labels()[0] == data[1][0]).all()
        assert (rdata.features()[0] == data[2][0]).all()
        assert rdata == h5f.Data(
            [os.path.splitext(self.matfile)[0]], data[1], data[2])

    def test_2D_labels_one_frame(self):
        data = generate.full(1, 5, 1, 2)
        sio.savemat(self.matfile,
                    {'labels': data[1][0], 'features': data[2][0]})

        h5f.Converter(self.h5file, 'group').convert(self.matfile)
        rdata = h5f.Reader(self.h5file, 'group').read()
        assert rdata.items() == [os.path.splitext(self.matfile)[0]]
        assert (rdata.features()[0] == data[2][0]).all()

        assert (rdata.labels()[0] == data[1][0]).all()
        assert rdata == h5f.Data([os.path.splitext(self.matfile)[0]],
                                 data[1], data[2])


class TestNpz:
    def setup(self):
        self.nfiles = 10
        self.h5file = 'data.h5'
        self.matfiles = ['data_{}.npz'.format(i) for i in range(self.nfiles)]

    def teardown(self):
        remove(self.h5file)
        for m in self.matfiles:
            remove(m)

    @pytest.mark.parametrize('group', ['group', '/group', '/group/'])
    def test_npz(self, group):
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
        conv = h5f.Converter(self.h5file, group)
        for name in self.matfiles:
            conv.convert(name)
        conv.close()

        # check convertion is correct
        rdata = h5f.Reader(self.h5file, 'group').read()
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

        conv = h5f.Converter(self.h5file, 'group')
        for name in self.matfiles:
            conv.convert(name)
        conv.close()

        rdata = h5f.Reader(self.h5file, 'group').read()
        assert len(rdata.items()) == self.nfiles
        for i in range(self.nfiles):
            assert (rdata.labels()[i] == data[1][i]).all()
            assert (rdata.features()[i] == data[2][i]).all()


class TestMatOneFrame2D:
    def setup(self):
        self.h5file = 'data.h5'
        self.matfile = 'data.mat'
        self.teardown()

        self.data = h5f.Data(['item'], [np.array([[0., 1.]])],
                             [np.array([[0, 0, 0]])])
        self.labels = self.data.labels()[0]

        sio.savemat(self.matfile,
                    {'labels': self.labels,
                     'features': self.data.features()[0]})

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
        writed = h5py.File(self.h5file, 'r')['group']['labels'][...]
        assert (writed == self.labels).all()  # is it what I want?

    def test_rw(self):
        h5f.Writer(self.h5file).write(self.data)
        labels = h5f.Reader(self.h5file).read().labels()
        assert len(labels) == 1
        labels = labels[0]
        assert labels.ndim == 2
        assert labels.shape == (1, 2)
        assert (self.labels == labels).all()

    def test_convert_read(self):
        h5f.Converter(self.h5file, 'group').convert(self.matfile)
        labels = h5f.Reader(self.h5file, 'group').read().labels()
        assert len(labels) == 1
        labels = labels[0]
        assert labels.ndim == 2
        assert labels.shape == (1, 2)
        assert (self.labels == labels).all()


class TestMatFilesLabels:
    def setup(self):
        self.nfiles = 10
        self.h5file = 'data.h5'
        self.matfiles = ['data_{}.mat'.format(i) for i in range(self.nfiles)]
        self.teardown()

    def teardown(self):
        remove(self.h5file)
        for m in self.matfiles:
            remove(m)

    def _converter_test(self, tformat):
        data = generate.full_data(self.nfiles, 3, 5, tformat)
        for i in range(self.nfiles):
            sio.savemat(
                self.matfiles[i],
                {'labels': data.labels()[i],
                 'features': data.features()[i]},
                oned_as='column')

        conv = h5f.Converter(self.h5file)
        for name in self.matfiles:
            conv.convert(name)
        conv.close()

        rdata = h5f.Reader(self.h5file).read()
        assert len(rdata.items()) == self.nfiles
        for i in range(self.nfiles):
            assert (rdata.labels()[i] == data.labels()[i]).all()
            assert (rdata.features()[i] == data.features()[i]).all()

    def _writer_test(self, tformat):
        data = generate.full_data(self.nfiles, 3, 5, tformat)

        writer = h5f.Writer(self.h5file)
        for i in range(self.nfiles):
            d = h5f.Data([data.items()[i]],
                         [data.labels()[i]],
                         [data.features()[i]])
            writer.write(d, append=True)
        writer.close()

        rdata = h5f.Reader(self.h5file).read()
        assert len(rdata.items()) == self.nfiles
        for i in range(self.nfiles):
            assert (rdata.labels()[i] == data.labels()[i]).all()
            assert (rdata.features()[i] == data.features()[i]).all()

    def test_cmat_1d(self):
        self._converter_test(1)

    def test_wmat_1d(self):
        self._writer_test(1)

    def test_cmat_2d(self):
        self._converter_test(2)

    def test_wmat_2d(self):
        self._writer_test(2)
