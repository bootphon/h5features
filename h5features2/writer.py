from os.path import exists, dirname, abspath
from item import Item
from pyh5features import Writer as pywriter

class Writer:
    def __init__(self, file, group, overwrite=False, compress=True, version="2.0"):
        versions = {
            "1.0" : pywriter.version.v1_0,
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
        self.writer = pywriter(file, group, overwrite, compress, versions[version])
    
    def write(self, item):
        if not isinstance(item, Item):
            raise TypeError("item must have Item type")
        self.writer.write(item.item)
    
    def version(self):
        versions = {
            "v1_0" : "1.0",
            "v1_1" : "1.1",
            "v1_2" : "1.2",
            "v2_0" : "2.0",
        }
        return versions[self.writer.get_version().name]

    def filename(self):
        return self.writer.filename()
    
    def groupname(self):
        return self.writer.groupname()

