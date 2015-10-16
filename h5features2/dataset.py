"""Provides the Dataset interface implemented by Features, Times and Items.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

class Dataset(object):
    """TODO"""
    def __init__(self, name):
        self.name = name

    def create(self, group):
        pass

    def is_compatible(self, group):
        pass

    def write(self, group):
        pass
