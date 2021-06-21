"""Usage example of the h5features library in Python

Generate fake FFT transforms as features, store them in a h5features file and
read them back.

"""
import os
import numpy as np
import h5features as h5f


def generate_fft(name):
    # from 10 to 100 frames
    nframes = np.random.randint(10, 100)

    # features of shape [nframes, 10]
    features = np.random.rand(nframes, 10)

    # times windows of 25ms with overlap of 10ms
    times = np.asarray([
        np.arange(nframes).astype(np.float64) * 0.025,
        np.arange(nframes).astype(np.float64) * 0.025 + 0.01]).T

    return h5f.Item(name, features, times)


# write a file with 3 random items
with h5f.Writer('example_file.h5f') as writer:
    writer.write(generate_fft('item1'))
    writer.write(generate_fft('item2'))
    writer.write(generate_fft('item3'))


# read back the items
with h5f.Reader('example_file.h5f') as reader:
    assert reader.items() == ['item1', 'item2', 'item3']

    # read all the item1
    item1 = reader.read('item1')

    # partially read item2 from 0.1s to 0.2s
    item2 = reader.read('item2', start=0.1, stop=0.2)

    # item read from file are instance on h5features.Item. Features and times
    # are usual numpy array.
    assert isinstance(item2, h5f.Item)
    assert item2.features.shape == (4, 10)
    assert np.all(item2.times[0, :] == np.asarray([0.1, 0.11]))


# cleanup
os.remove('example_file.h5f')
