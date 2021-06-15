
from os.path import exists, abspath
from _h5features import read_group

def get_groups(name):
    if not isinstance(name, str):
        raise TypeError("name must be str")
    if not exists(abspath(name)):
        raise FileNotFoundError("{} is not a file".format(abspath(name)))

    return read_group(abspath(name))