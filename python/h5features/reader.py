from os.path import exists
import numpy as np

from h5features import Item
from _h5features import ReaderWrapper


class Reader:
    """Interface with the python wrapper Reader from h5features2

    It allow to read Item from hdf5 format

    Args:
        file (`str`) : the name of the file to read
        group (`str`) :  a 'location' in the file to read

    Raises:
        TypeError: if file, group are not `str`
        FileNotFoundError :  if file does not exist

    """
    def __init__(self, file, group):
        """Creates an instance of Reader"""
        if not isinstance(file, str):
            raise TypeError("file name must be str")
        if not exists(file):
            raise FileNotFoundError("file {} does not exist".format(file))
        if not isinstance(group, str):
            raise TypeError("group name must be str")

        self.__reader = ReaderWrapper(file, group)

    def read(self, name, ignore_properties=False,
             features_between_times=(None, None)):
        """This method allow to read in the hdf5 file a part or a whole item

        Args:
            name (`str`): the name of item to return
            ignore_properties (`bool`) : if True, do not return item properties
                (default False)
            features_between_time (`tuple` of two floats) : if specified,
                return the segments between the times given else the whole item

        Returns:
            Item: the item with the name specified

        Raises:
            TypeError: If name is not `str`,
                if ignore_properties is not `bool`,
                if features_between_times is not `tuple`,
                if features_between_times as a length != 2,
                if if one of time is None only
            ValueError: If times are not convertible to float

        """
        if not isinstance(name, str):
            raise TypeError("name must be str")
        if not isinstance(ignore_properties, bool):
            raise TypeError("ignore_properties must be bool")
        if not isinstance(features_between_times, tuple):
            raise TypeError("features_between_times must be tuple")
        if len(features_between_times) != 2:
            raise TypeError(
                "features_between_times must be a tuple of to time's value")
        if (
                features_between_times[0] is None or
                features_between_times[1] is None):
            if (
                    features_between_times[0] is None and
                    features_between_times[1] is None):
                return Item(self.__reader.read(name, ignore_properties))

            raise TypeError(
                "features_between_times values must be none for start "
                "and stop, or double for the two values")

        # times not none
        start, stop = features_between_times
        start = np.float64(start)
        stop = np.float64(stop)
        return Item(
            self.__reader.read_btw(name, start, stop, ignore_properties))

    def version(self):
        """ This method allow to check which version of reading is used

        Returns:
            str: the version of reading
        """
        versions = {
            "v1_0": "1.0",
            "v1_1": "1.1",
            "v1_2": "1.2",
            "v2_0": "2.0",
        }
        return versions[self.__reader.get_version().name]

    def items(self):
        """Returns the name of item writed in file and group specified

        Returns:
            list : list of item's name

        """
        return self.__reader.items()

    def groupname(self):
        """Checks in which group the item is read

        Returns:
            str: the group of the file to read
        """
        return self.__reader.groupname()

    def filename(self):
        """Checks which file is used

        Returns:
            str: the file to read
        """
        return self.__reader.filename()

    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        del self
