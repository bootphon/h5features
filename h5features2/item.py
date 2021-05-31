from pyh5features import Item as pyitem
import numpy as np
from copy import deepcopy
class Item:
    def __init__(self, name, features, times, properties={}):

        def rec_properties(props):
            for k, v in props.items():
                if not isinstance(k, str):
                    raise TypeError("propertie key must be str")
                if isinstance(v, dict):
                    rec_properties(v)

        if not isinstance(times, tuple):
            raise TypeError("times is not a tuple")

        start, stop = times
        if not isinstance(name, str):
            raise TypeError("item's name must be str")
        if not isinstance(features, np.ndarray):
            raise TypeError("features is not a np.ndarray")
        if features.dtype != "float64":
            raise TypeError("features must have float64 type")
        if not isinstance(start, np.ndarray):
            raise TypeError("start is not a np.ndarray")
        if start.dtype != "float64":
            raise TypeError("start must have float64 type")
        if not isinstance(stop, np.ndarray):
            raise TypeError("stop is not a np.ndarray")
        if stop.dtype != "float64":
            raise TypeError("stop must have float64 type")   
        if not isinstance(properties, dict):
            raise TypeError("properties is not a dict")
        rec_properties(properties)
        self.item = pyitem(name, features, start, stop, properties, True)

    def features(self,  copy=False):
        if copy:
            return deepcopy(np.asarray(self.item.features(), dtype=np.float64))
        return np.array(self.item.features(),dtype=np.float64,  copy=False)

    def times(self, copy=False):
        if copy:
            return deepcopy(np.asarray(self.item.times(), dtype=np.float64))
        return np.array(self.item.times(), dtype=np.float64, copy=False)
    
    def properties(self):

        return self.item.properties()
    
    # def get_properties(self, name):
    #     return self.item.properties_get(name)
    
    def set_properties(self, name, value):
        if not isinstance(name, str):
            raise TypeError("name must be str")
        self.item.properties_set(name, value)

    def has_properties(self):
        return self.item.has_properties()
    
    def properties_contains(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be str")
        return self.item.properties_contains(name)

    def properties_erase(self, name):
        if not isinstance(name, str):
            raise TypeError("name must be str")
        self.item.properties_erase(name)