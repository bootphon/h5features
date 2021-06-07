import numpy as np
from h5features2.item import Item
from h5features2.writer import Writer
from h5features2.reader import Reader
from h5features2.versions import Versions


# Create features, times begin and end, name and properties
features = np.ones((9, 1000))
begin = np.asarray([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.float64)
end = np.asarray([1, 2, 3, 4, 5, 6, 7, 8, 9], dtype=np.float64)
name = "Test"
properties = {"test": True}

# Create item object by the class method create
item = Item.create(name, features, (begin, end), properties=properties)

# Create writer object and write item in test2.h5f, in group 'test'
writer = Writer("test2.h5f", "test", True, True, "2.0")
writer.write(item)

# Create reader object and read the file to get an item
reader = Reader("test2.h5f", "test")

it = reader.read("Test", ignore_properties=False)

# an item has several methods to get features, times, properties, name

assert np.all(features==it.features())
assert np.all(begin == it.times()[:,0])
assert np.all(end == it.times()[:,1])
assert it.properties() == properties

it = reader.read("Test", ignore_properties=True)
assert it.properties() == {}

# in order to check available version, use :
print(Versions.versions())

# see the API for other methods