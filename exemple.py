#!/usr/bin/env python

# Copyright 2014-2015 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
#
# This file is part of h5features.
#
# h5features is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# h5features is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with h5features.  If not, see <http://www.gnu.org/licenses/>.

"""A running exemple of the h5features package functionalities."""

import numpy as np
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

# Initialize a writer and write data in a 'exemple' group
writer = h5f.Writer('exemple.h5')
writer.write(data, 'exemple')
writer.close()

# You can also use the with statement and forgot the call to close()
with h5f.Writer('exemple.h5') as writer:
    # Here we write the same data to another group
    writer.write(data, 'exemple_2')

    # more intersting, you can also append new data to an existing
    # group if no items are shared. Here we generate 10 more items
    # with different names and append them to the first group.
    data2 = generate_data(10,  base='item2')
    writer.write(data2, 'exemple', append=True)

    # do it agin. Note that when append is not True, this erases any
    # existing data in the group
    data3 = generate_data(10, base='item3')
    writer.write(data3, 'exemple', append=True)


##########################
# Reading data from a file
##########################

# Initialize a reader and read all data in the group 'example_2'
rdata = h5f.Reader('exemple.h5', 'exemple_2').read()
