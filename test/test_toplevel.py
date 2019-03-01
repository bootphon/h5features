"""Test top level functions of the h5features package."""

import copy
import os
import pytest
import h5features as h5f

from .aux import generate


def test_from_exemple(tmpdir):
    filename = os.path.join(str(tmpdir), 'exemple.h5')
    a1, a2, a3 = generate.full(100)
    data = h5f.Data(a1, a2, a3)

    h5f.Writer(filename).write(data, 'group')

    with h5f.Reader(filename, 'group') as r:
        rdata = r.read()
        assert len(rdata.items()) == 100
        assert data == rdata


def test_rw_one_frame_2D(tmpdir):
    h5file = os.path.join(str(tmpdir), 'exemple.h5')
    gold = generate.full_data(1, 3, 1, 2)

    h5f.Writer(h5file).write(gold)
    test = h5f.Reader(h5file).read()
    assert test == gold


@pytest.mark.parametrize(
    'mode, append',
    [(m, a) for m in ('w', 'a') for a in (False, True)])
def test_write_mode(tmpdir, mode, append):
    h5file = os.path.join(str(tmpdir) + 'test.h5')
    data = generate.full_data(1, 3, 1, 2)
    copy_data = copy.deepcopy(data)

    h5f.Writer(h5file).write(data, append=False)
    assert h5f.Reader(h5file).read() == data

    # write data a second time
    if mode == 'a' and append is True:
        with pytest.raises(IOError):
            h5f.Writer(h5file, mode=mode).write(data, append=append)
    else:
        h5f.Writer(h5file, mode=mode).write(data, append=append)
        assert data == copy_data
        assert h5f.Reader(h5file).read() == copy_data
