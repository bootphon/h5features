from os.path import exists, dirname, abspath
from h5features import Item
from _h5features import WriterWrapper, ostream_redirect


class Writer:
    """Interface with the python wrapper Writer from h5features2

    It allow to write Item in hdf5 format

    Args:
        filename (`str`) : the name of the file to write
        group (`str`) :  a 'location' in the file to write
        overwrite (`bool`, optionnal) : If True, overwrite the file (default
            False)
        compress (`bool`, optionnal) : If True, compress the file (default
            True)
        version (`str`, optionnal) : version of writing choosen in ['1.1',
            '1.2', '2.0'] (default "2.0")

    Raises:
        TypeError: if file, group are not `str`; compress and overwrite are
            not bool;
        KeyError: if version not in ['1.1', '1.2', '2.0']
        FileNotFoundError: if direname of file does not exist

    """
    def __init__(self, filename, group, overwrite=False,
                 compress=True, version="2.0"):
        versions = {
            # writing v1.0 is not supported
            "1.1": WriterWrapper.version.v1_1,
            "1.2": WriterWrapper.version.v1_2,
            "2.0": WriterWrapper.version.v2_0,
        }

        if not isinstance(filename, str):
            raise TypeError("file name must be str")
        filename = abspath(filename)
        if not exists(dirname(filename)):
            raise FileNotFoundError("file {} does not exist".format(filename))
        if not isinstance(group, str):
            raise TypeError("group name must be str")
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be bool")
        if not isinstance(compress, bool):
            raise TypeError("compress must be bool")
        if versions.get(version, None) is None:
            raise KeyError("version {} does not exist".format(version))

        self._writer = WriterWrapper(
            filename, group, overwrite, compress, versions[version])

    def write(self, item):
        """This method allow to write the item

        Args:
            item (Item) :  the Item to write

        Raises:
            TypeError: if item is not an instance of Item

        """
        if type(item).__name__ != Item.__name__:
            raise TypeError("item must have Item type")
        with ostream_redirect(stderr=True):
            self._writer.write(item._Item__item)

    @property
    def version(self) -> str:
        """The file format version used for writing"""
        return {
            'v1_0': '1.0',
            'v1_1': '1.1',
            'v1_2': '1.2',
            'v2_0': '2.0'}[self._writer.get_version().name]

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
