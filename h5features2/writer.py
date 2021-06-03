from os.path import exists, dirname, abspath
from item import Item
from pyh5features import Writer as pywriter

class Writer:
    """This class implement the interface with the python wrapper Writer from h5features2

    It allow to write Item in hdf5 format
    """
    def __init__(self, file, group, overwrite=False, compress=True, version="2.0"):
        """ As constructor, create the instance of Writer according to the following parameters:
        Args:
            file (`str`) : the name of the file to write
            group (`str`) :  a 'location' in the file to write
            overwrite (`bool`, optionnal) : If True, overwrite the file (default False)
            compress (`bool`, optionnal) : If True, compress the file (default True)
            version (`str`, optionnal) : version of writing choosen in ['1.1', '1.2', '2.0'] (default "2.0")

        Raises:
            TypeError: if file, group are not `str`; compress and overwrite are not bool;
            KeyError: if version not in ['1.1', '1.2', '2.0']
            FileNotFoundError: if direname of file does not exist
        """
        versions = {
            # "1.0" : pywriter.version.v1_0,
            "1.1" : pywriter.version.v1_1,
            "1.2" : pywriter.version.v1_2,
            "2.0" : pywriter.version.v2_0,
        }
        if not isinstance(file, str):
            raise TypeError("file name must be str")
        file = abspath(file)
        if not exists(dirname(file)):
            raise FileNotFoundError("file {} does not exist".format(file))
        if not isinstance(group, str):
            raise TypeError("group name must be str")
        if not isinstance(overwrite, bool):
            raise TypeError("overwrite must be bool")
        if not isinstance(compress, bool):
            raise TypeError("compress must be bool")
        if versions.get(version, None) is None:
            raise KeyError("version {} does not exist".format(version))
        self.__writer = pywriter(file, group, overwrite, compress, versions[version])
    
    def write(self, item):
        """This method allow to write the item

        Args:
            item (:obj: Item) :  the Item to write
        
        Raises:
            TypeError: if item is not an instance of Item

        """
        if not isinstance(item, Item):
            raise TypeError("item must have Item type")
        self.__writer.write(item._Item__item)
    
    def version(self) -> str:
        """ This method allow to check which version of writing is used
        Returns:
            str: the version of writing
        """

        versions = {
            "v1_0" : "1.0",
            "v1_1" : "1.1",
            "v1_2" : "1.2",
            "v2_0" : "2.0",
        }
        return versions[self.__writer.get_version().name]

    def filename(self) -> str:
        """ This method allow to check which file is used
        Returns:
            str: the file to write
        """
        return self.__writer.filename()
    
    def groupname(self) -> str:
        """ This method allow to check in which group the item is writed
        Returns:
            str: the group of the file to write
        """
        return self.__writer.groupname()

