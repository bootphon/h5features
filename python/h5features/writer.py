"""Implementation of the class h5features.Writer"""
import pathlib
from h5features import Item
from _h5features import WriterWrapper, VersionWrapper, OstreamRedirect


class Writer:
    """Writes :class:`~h5features.Item` to a h5features file

    Parameters
    ----------
    filename : str or pathlib.Path
      The name of the file to write
    group : str, optional
      The group in the file to write on. Default to "features".
    overwrite : bool, optionnal
      If true erase the file content if it is already existing. If false it
      will append new items to the existing group. Default to False.
    compress : bool, optionnal
      When true, compress the data. Default to True.
    version : str, optionnal
      The version of the file to write. Version 1.0 is **not
      available** to write, only read. Default to "2.0"

    Raises
    ------
    RuntimeError
      If the file cannot be opened. When `overwrite` is true, if the `group`
      already exists in the file and the version is not supported. Or if the
      requested `version` is not supported. If `group` is not a str.
    TypeError
      If `filename` is not a `Path` or `str`, if `group` is not a `str`.

    """
    def __init__(self, filename, group='features',
                 overwrite=False, compress=True, version='2.0'):
        versions = {
            # writing v1.0 is not supported
            '1.1': VersionWrapper.v1_1,
            '1.2': VersionWrapper.v1_2,
            '2.0': VersionWrapper.v2_0}
        if version not in versions:
            raise RuntimeError(f'version {version} is not supported')

        if isinstance(filename, pathlib.Path):
            filename = str(filename)

        self._writer = WriterWrapper(
            filename, group,
            bool(overwrite), bool(compress), versions[version])

    def write(self, item):
        """Writes an item to file

        Raises
        ------
        TypeError
          if `item` is not an instance of Item.
        RuntimeError
          If `item` cannot be wrote (e.g. an item with this same name already
          exists in the file).

        """
        if not isinstance(item, Item):
            raise TypeError("item must be of type h5features.Item")

        with OstreamRedirect(stderr=True):
            self._writer.write(item._item)

    @property
    def version(self) -> str:
        """The file format version used for writing"""
        return {
            'v1_0': '1.0',
            'v1_1': '1.1',
            'v1_2': '1.2',
            'v2_0': '2.0'}[self._writer.version().name]

    @property
    def filename(self) -> str:
        """The file to write on"""
        return self._writer.filename()

    @property
    def groupname(self) -> str:
        """The group in which items are wrote"""
        return self._writer.groupname()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        del self
