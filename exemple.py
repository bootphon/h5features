import h5features as h5f

########################
# Prelude to the exemple
########################

def generate_data(nitem, nfeat=2, dim=10, tdim=1, base='item'):
    """generate random h5features data.

    :param int nitem: The number of items to generate.
    :param int nfeat: The number of features to generate for each item.
    :param int dim: The dimension of the Features vectors.
    :param str base: The base of items names.
    :param int tdim: The dimension of the Times vectors. If greater
        than 1, generates 2D numpy arrays.
    :return: A h5features data dictionary with keys 'items', 'times'
        and 'features'.

    """
    import numpy as np

    # A list of item names
    items = [base + '_' + str(i) for i in range(nitem)]

    # A list of features arrays
    features = [np.random.randn(nfeat, dim) for _ in range(nitem)]

    # A list on 1D or 2D times arrays
    if tdim == 1:
        times = [np.linspace(0, 1, nfeat)] * nitem
    else:
        t = np.linspace(0, 1, nfeat)
        times = [np.array([t+i for i in range(tdim)])] * nitem

    # Format data as required by the writer
    return h5f.Data(items, times, features, check=True)

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

# Hopefully we read the same data we just writed
assert rdata == data

# Some more advance reading facilities
with h5f.Reader('exemple.h5', 'group1') as reader:
    # read the first item stored on the group.
    first_item = reader.items.data[0]
    first_data = reader.read(first_item)

    # TODO read selected times


###################
# Times data format
###################

# Previous exemples shown writing and reading features associated to
# 1D times information (each feature vector correspond to a single
# timestamp, e.g. the center of a time window). In more advanced
# processing you may want to store 2D times information (e.g. begin
# and end of a time window)

# TODO make this pass with tdim>2
# data = generate_data(100, tdim=2)
# h5f.Writer('exemple.h5').write(data, 'group3')

# rdata = h5f.Reader('exemple.h5', 'group3').read()
# assert data == rdata
