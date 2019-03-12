"""Test of the h5features.prpoerties module"""

import copy
import h5py
import numpy as np
import pytest
import random
import string
import h5features.properties


@pytest.mark.parametrize('props', [0, [0, 1], {'a': 0}, [{'a': 0}, 0]])
def test_bad_properties(props):
    with pytest.raises(IOError) as err:
        h5features.properties.Properties(props, check=True)
    assert 'properties must be a list of dictionnaries' in str(err)

    p = h5features.properties.Properties(props, check=False)
    assert p.data == props


def test_equality():
    p = [{'a': 1.2, 'e': 0, 'c': False},
         {'a': {'f': 0.1}, 'e': 1, 'b': False},
         {'a': 1, 'b': 'two', 'c': True},
         {'a': 1, 'b': 'two', 'd': np.asarray([[1, 1]])}]

    P = h5features.properties.Properties

    assert P(p) == P(p)
    assert P(p) != P(p[1:])

    p2 = copy.deepcopy(p)
    p2[0]['a'] = int(0)
    assert P(p) != P(p2)

    p2 = copy.deepcopy(p)
    p2[0]['a'] = 1.1
    assert P(p) != P(p2)

    p2 = copy.deepcopy(p)
    p2[0]['b'] = 0
    assert P(p) != P(p2)

    p2 = copy.deepcopy(p)
    p2[-1]['d'] = np.asarray([[0, 1]])
    assert P(p) != P(p2)


@pytest.mark.parametrize(
    'props', [[{}], [{1: 0}], [{'a': {'a': 'a'}}], [{'a': 0, 'b': 'b'}]])
def test_rw(props, tmpdir):
    f = h5py.File(tmpdir.join('spam.hdf5'), 'w')
    g = f.create_group('spam')
    p = h5features.properties.Properties(props)

    p.create_dataset(g)
    p.write_to(g)
    p2 = h5features.properties.read_properties(g)
    assert p2 == props


@pytest.mark.parametrize('N', [int(1e3), int(1e5)])
def test_rw_huge(N, tmpdir):
    data = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(N))
    f = h5py.File(tmpdir.join('spam.hdf5'), 'w')
    g = f.create_group('spam')
    p = h5features.properties.Properties([{'props': data}])

    p.create_dataset(g)
    p.write_to(g)
    p2 = h5features.properties.read_properties(g)
    assert p2[0]['props'] == data
