
from os.path import exists, abspath
from _h5features import read_group

def get_groups(name):
    """returns a list of groups in the hdf5 file specified

        Args:
            name (`str`): the name of hdf5 file
        Raises:
            TypeError: if name is not `str`
            FileNotFoundError: if file does not exists
    """

    if not isinstance(name, str):
        raise TypeError("name must be str")
    if not exists(abspath(name)):
        raise FileNotFoundError("{} is not a file".format(abspath(name)))

    return read_group(abspath(name))