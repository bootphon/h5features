from os.path import exists
from pyh5features import Reader as pyreader
from item import Item
import numpy as np
class Reader:
    def __init__(self, file, group):
        if not isinstance(file, str):
            raise TypeError("file name must be str")
        if not exists(file):
            raise FileNotFoundError("file {} does not exist".format(file))
        if not isinstance(group, str):
            raise TypeError("group name must be str")
        self.reader = pyreader(file, group)
    
    def read(self, name, ignore_properties=False, features_between_times=(None, None)):
            
        if not isinstance(name, str):
            raise TypeError("name must be str")
        if not isinstance(ignore_properties, bool):
            raise TypeError("ignore_properties must be bool")
        if not isinstance(features_between_times, tuple):
            raise TypeError("features_between_times must be tuple")
        if len(features_between_times) != 2:
            raise TypeError("features_between_times must be a tuple of to time's value")
        if features_between_times[0] is None or features_between_times[1] is None:
            if features_between_times[0] is None and features_between_times[1] is None:
                return Item(self.reader.read(name, ignore_properties))
                
            else:
                raise TypeError("features_between_times values must be none for start and stop, or double for the two values")
        # times not none
        start, stop = features_between_times
        start = np.float64(start)
        stop = np.float64(stop)
        return Item(self.reader.read_btw(name, start, stop, ignore_properties))

    def version(self):
        versions = {
            "v1_0" : "1.0",
            "v1_1" : "1.1",
            "v1_2" : "1.2",
            "v2_0" : "2.0",
        }
        return versions[self.reader.get_version().name]

    def items(self):
        return self.reader.items()
    
    def groupname(self):
        return self.reader.groupname()
    
    def filename(self):
        return self.reader.filename()