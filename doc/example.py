"""Usage example of the h5features library in Python.

Generate fake FFT transforms as features, store them in a h5features file and
read them back.
"""

import tempfile

import numpy as np

from h5features import Item, Reader, Writer

rng = np.random.default_rng(seed=0)


def generate_fft(name: str) -> Item:
    """Generate a random FFT item with a given name."""
    nframes = rng.integers(10, 100)  # from 10 to 100 frames
    features = rng.random((nframes, 10))  # features of shape [nframes, 10]
    times = np.asarray(  # time windows of 25ms with overlap of 10ms
        [
            np.arange(nframes).astype(np.float64) * 0.025,
            np.arange(nframes).astype(np.float64) * 0.025 + 0.01,
        ]
    ).T
    return Item(name, features, times)


with tempfile.NamedTemporaryFile(suffix=".h5f") as tempfile:
    # write a file with 3 random items
    writer = Writer(tempfile.name)
    writer.write([generate_fft("item1"), generate_fft("item2"), generate_fft("item3")])

    # read back the items
    reader = Reader(tempfile.name)
    assert reader.items() == ["item1", "item2", "item3"]

    # read all the item1
    item1 = reader.read("item1")

    # partially read item2 from 0.1s to 0.2s
    item2 = reader.read_partial("item2", start=0.1, stop=0.2)

    # item read from file are instance on h5features.Item. Features and times
    # are usual numpy array.
    assert isinstance(item2, Item)
    assert item2.features().shape == (4, 10)
    assert np.all(item2.times()[0, :] == np.asarray([0.1, 0.11]))
