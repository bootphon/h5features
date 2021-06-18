import os
import numpy as np

from h5features import Item
from _h5features import ReaderWrapper, ItemWrapper, ostream_redirect


class Reader:
    """Interface with the python wrapper Reader from h5features2

    It allow to read Item from hdf5 format

    Args:
        filename (`str`) : the h5features file to read from
        group (`str`) :  The group within the file to read items from

    Raises:
        TypeError: if file, group are not `str`
        FileNotFoundError :  if file does not exist

    """
    def __init__(self, filename, group):
        if not isinstance(filename, str):
            raise TypeError("file name must be str")
        if not os.path.exists(filename):
            raise FileNotFoundError(f"file {filename} does not exist")
        if not isinstance(group, str):
            raise TypeError("group name must be str")

        self._reader = ReaderWrapper(filename, group)

    def read_all(self, ignore_properties=False):
        """Returns all the items stored in the file as a list"""
        return self._reader.read_all(ignore_properties)

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
                with ostream_redirect(stderr=True):
                    return self._create_item(
                        self._reader.read(name, ignore_properties))

            raise TypeError(
                "features_between_times values must be none for start "
                "and stop, or double for the two values")

        # times not none
        start, stop = features_between_times
        start = np.float64(start)
        stop = np.float64(stop)
        with ostream_redirect(stderr=True):
            return self._create_item(
                self._reader.read_btw(name, start, stop, ignore_properties))

    @property
    def version(self):
        """The file format version"""
        return {
            "v1_0": "1.0",
            "v1_1": "1.1",
            "v1_2": "1.2",
            "v2_0": "2.0"}[self._reader.version().name]

    def items(self):
        """Returns the readable items as a list"""
        return self._reader.items()

    @property
    def groupname(self):
        """The group from which items are read in the file"""
        return self._reader.groupname()

    @property
    def filename(self):
        """The file being read"""
        return self._reader.filename()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        del self

    @staticmethod
    def _create_item(item):
        """Helper function for item instanciation

        Creates a h5features.Item instance from a _h5features._ItemWrapper
        instance without using the usual h5features.Item constructor.

        """
        assert isinstance(item, ItemWrapper)
        instance = Item.__new__(Item)
        instance._item = item
        return instance
