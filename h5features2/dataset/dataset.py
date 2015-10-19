"""Provides the Dataset interface implemented by Features, Times and Items.

@author Mathieu Bernard <mmathieubernardd@gmail.com>

"""

# TODO Some pythonic way ensuring this is an abstract class (ABC) ?
class Dataset(object):
    """The Dataset class is an **abstract base class** of h5features data.

    It provides a shared interface to the classes `Items`, `Times` and
    'Features' which all together constitutes an h5features file.

    """
    def __init__(self, name):
        self.name = name

    # TODO implement this in childs
    def __eq__(self, other):
        pass

    def is_appendable_to(self, group):
        pass

    def write(self, group):
        pass

    # TODO We should need this method!!
    def read(self, group):
        pass
