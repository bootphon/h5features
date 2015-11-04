import h5features as h5f

########################
# Prelude to the exemple
########################

def generate_data(nitem, nfeat=2, dim=10, base='item'):
    """generate random h5features data.

    :param int nitem: The number of items to generate
    :param int nfeat: The number of features to generate for each item
    :param int dim: The dimension of the generated feature vectors
    :param str base: The base of items names
    :return: A h5features data dictionary with keys 'items', 'times'
        and 'features'.
    """
    import numpy as np

    # A list of strings
    items = [base + '_' + str(i) for i in range(nitem)]

    # lists of numpy arrays
    features = [np.random.randn(nfeat, dim) for _ in range(nitem)]
    times = [np.linspace(0, 1, nfeat) for _ in range(nitem)]

    # Format data as a dictionary, as required by the writer
    return {'items':h5f.Items(items),
            'features':h5f.Features(features),
            'times':h5f.Times(times)}

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

# Hopefully h5features conserves data
# TODO make this pass
# assert rdata == data
