import h5features as h5f

########################
# Prelude to the exemple
########################

def generate_data(nitem, nfeat=2, dim=10, labeldim=1, base='item'):
    """Returns a randomly generated h5f.Data instance.

    - nitem is the number of items to generate.
    - nfeat is the number of features to generate for each item.
    - dim is the dimension of the features vectors.
    - base is the items basename
    - labeldim is the dimension of the labels vectors.
    """
    import numpy as np

    # A list of item names
    items = [base + '_' + str(i) for i in range(nitem)]

    # A list of features arrays
    features = [np.random.randn(nfeat, dim) for _ in range(nitem)]

    # A list on 1D or 2D times arrays
    if labeldim == 1:
        labels = [np.linspace(0, 1, nfeat)] * nitem
    else:
        t = np.linspace(0, 1, nfeat)
        labels = [np.array([t+i for i in range(labeldim)])] * nitem

    # Format data as required by the writer
    return h5f.Data(items, labels, features, check=True)

########################
# Writing data to a file
########################

# Generate some data for 100 items
data = generate_data(100)

# Initialize a writer, write the data in a group called 'group1' and
# close the file
writer = h5f.Writer('exemple.h5')
writer.write(data, 'group1')
writer.close()

# More pythonic, the with statement
with h5f.Writer('exemple.h5') as writer:
    # Write the same data to a second group
    writer.write(data, 'group2')

    # You can append new data to an existing group if all items have
    # different names. Here we generate 10 more items and append them
    # to the group 2, which now stores 110 items.
    data2 = generate_data(10,  base='item2')
    writer.write(data2, 'group2', append=True)

    # If append is not True, existing data in the group is overwrited.
    data3 = generate_data(10, base='item3')
    writer.write(data3, 'group2', append=True)  # 120 items
    writer.write(data3, 'group2')               # 10 items


##########################
# Reading data from a file
##########################

# Initialize a reader and load the entire group. A notable difference
# with the Writer is that a Reader is attached to a specific group of
# a file. This allows optimized read operations.
rdata = h5f.Reader('exemple.h5', 'group1').read()

# Hopefully we read the same data we just wrote
assert rdata == data

# Some more advance reading facilities
with h5f.Reader('exemple.h5', 'group1') as reader:
    # Same as before, read the whole data
    whole_data = reader.read()

    # Read the first item stored on the group.
    first_item = reader.items.data[0]
    rdata = reader.read(first_item)
    assert len(rdata.items()) == 1

    # Read an interval composed of the 10 first items.
    tenth_item = reader.items.data[9]
    rdata = reader.read(first_item, tenth_item)
    assert len(rdata.items()) == 10

#####################
# Playing with labels
#####################

# Previous exemples shown writing and reading labels associated to 1D
# times information (each feature vector correspond to a single
# timestamp, e.g. the center of a time window). In more advanced
# processing you may want to store 2D times information (e.g. begin
# and end of a time window). For now non-numerical labels or not
# supported.

data = generate_data(100, labeldim=2)
h5f.Writer('exemple.h5').write(data, 'group3')

rdata = h5f.Reader('exemple.h5', 'group3').read()
assert data == rdata
