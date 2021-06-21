"""Implementation of the class h5features.Reader"""
import pathlib
import numpy as np

from h5features import Item
from _h5features import ReaderWrapper, ItemWrapper, OstreamRedirect


class Reader:
    """Reads :class:`~h5features.Item` from  h5features file

    A reader is attached to a HDF5 file and a h5features group within this
    file.

    Parameters
    ----------
    filename : str or pathlib.Path
      The HDF5 file to read from
    group: str, optional
      The group within the file to read items from. If not specified, assume
      there is a single group in the file.

    Raises
    ------
    RuntimeError
      If the file cannot be opened or if the group does not exist in the file.
      If `group` is None and there are several groups in the file.
    TypeError
      If `filename` is not a `Path` or `str`, if `group` is not a `str`.

    """
    def __init__(self, filename, group=None):
        if isinstance(filename, pathlib.Path):
            filename = str(filename)
        if not group:
            groups = self.list_groups(filename)
            if len(groups) != 1:
                raise RuntimeError(
                    f'There is more than a unique group in {filename}, '
                    'group must be specified.')
            group = groups[0]

        self._reader = ReaderWrapper(filename, group)

    @staticmethod
    def _create_item(item):
        """Helper function for item instanciation

        Creates a h5features.Item instance from a _h5features._ItemWrapper
        instance without using the usual h5features.Item constructor.

        """
        assert isinstance(item, ItemWrapper)
        instance = Item.__new__(Item)
        instance._item = item
        instance._properties = None
        return instance

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        del self

    def read_all(self, ignore_properties=False):
        """Returns all the items stored in the file as a list"""
        return [self._create_item(item)
                for item in self._reader.read_all(ignore_properties)]

    def read(self, name, start=None, stop=None, ignore_properties=False):
        """Reads an item from the file

        When `start` and `stop` are specified, partially read an item within
        the time interval ``(start, stop)``.

        Parameters
        ----------
        name : str
          The name of item to read
        start : float, optional
          The start time (in seconds) to read the item from
        stop : float, optional
          The stop time (in seconds) to read the item from
        ignore_properties : bool, optional
          if True, do not read item properties, default to False

        Returns
        -------
        item : :class:`~h5features.Item`
          The item with the name specified

        Raises
        ------
        RuntimeError
          If `name` is not an existing item in the file

        TypeError
          If name is not `str`, if `start` and `stop` are specified but cannot
          be converted to float.

        if ignore_properties is not `bool`,
                if features_between_times is not `tuple`,
                if features_between_times as a length != 2,
                if if one of time is None only
            ValueError: If times are not convertible to float

        """
        # force to bool
        ignore_properties = bool(ignore_properties)

        if not isinstance(name, str):
            raise TypeError('name must be str')

        # complete read of the item
        if start is None and stop is None:
            with OstreamRedirect(stderr=True):
                return self._create_item(self._reader.read(
                    name, ignore_properties))

        # partial read of the item
        if start is not None and stop is not None:
            try:
                start = np.float64(start)
                stop = np.float64(stop)
            except ValueError as err:
                raise TypeError(err) from None

            with OstreamRedirect(stderr=True):
                return self._create_item(self._reader.read_partial(
                    name, start, stop, ignore_properties))

        raise TypeError('start and stop arguments must be both None or float')

    @staticmethod
    def list_groups(filename) -> list:
        """Returns the groups in the specified HDF5 file as a list

        Parameters
        ----------
        filename : str or pathlib.Path
            The HDF5 to read groups from

        Raises
        ------
        RuntimeError
            If the `filename` cannot be opened or is not a HDF5 file

        """
        if isinstance(filename, pathlib.Path):
            filename = str(filename)
        return ReaderWrapper.list_groups(filename)

    @property
    def version(self) -> str:
        """The file format version"""
        return {
            "v1_0": "1.0",
            "v1_1": "1.1",
            "v1_2": "1.2",
            "v2_0": "2.0"}[self._reader.version().name]

    def items(self) -> list:
        """Returns the name of readable items as a list"""
        return self._reader.items()

    @property
    def groupname(self):
        """The group from which items are read in the file"""
        return self._reader.groupname()

    @property
    def filename(self):
        """The file being read"""
        return self._reader.filename()
