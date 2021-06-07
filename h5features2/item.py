from copy import deepcopy
import numpy as np
from pyh5features import Item as pyitem

class Item:
    """This class implement the interface with the python wrapper Item from h5features2

    It allow to create an object with several characteristics
    The features are datas of type time x characteristics. They store several value each of several segment, for example of time
    The time are datas of type time x (begin-end). The store the begin and the end of each time segment
    The properties are datas stored in an hash table. They contribute to characterize the Item
    """
    def __init__(self, item):
        """Constructor of Item class
        
        Args:
            item (`pyh5features.Item`): Construct directly Item from wrapper
                It is used internaly.
        Raises:
            TypeError: If `item` is not an instance of `pyh5features.Item`
        """
        if not isinstance(item, pyitem):
            raise TypeError("item must have pyh5features.Item class")
        self.__item = item
    @classmethod
    def create(cls, name, features, times, properties={}):
        """Main constructor of Item class for user usage

        Args:
            name (`str`): a string to qualify the `Item`.

            features (`numpy.ndarray`): a two-dimensionnal numpy array of data.
                The first dimension correspond to times or segments in the data.
                The second dimension correspond to one/several values according to shape for the segment.

            times (`tuple` of `numpy.ndarray`): a tuple with two numpy array.
                The first correspond to a numpy array where each value correspond to the start time of same index in first dimension of features.
                The second correspond to end time in the same way.

            properties (`dict`, optional): a python dictionnary to record characteristics on the Item.


        Notes:
            properties values can be either `dict`, `bool`, `int`, `float`, `string`, `list` of `int`, `float`, `string`

        Returns:
            Item

        Raises:
            TypeError: if item's name is not `str`, if features is not a two dimensionnal `numpy.ndarray` of `float64 type,
                if times is not a `tuple` of two  one-dimensionnal `numpy.ndarray` of `float64` type,
                if properties keys are not `str`.

        """
        def rec_properties(props):
            for k, v in props.items():
                if not isinstance(k, str):
                    raise TypeError("propertie key must be str")
                if isinstance(v, dict):
                    rec_properties(v)

        if not isinstance(times, tuple):
            raise TypeError("times is not a tuple")
        if len(times) != 2:
            raise TypeError("times must contain to numpy arrays")
        start, stop = times
        if not isinstance(name, str):
            raise TypeError("item's name must be str")
        if not isinstance(features, np.ndarray):
            raise TypeError("features is not a np.ndarray")
        if features.dtype != "float64":
            raise TypeError("features must have float64 type")
        if len(features.shape) != 2:
            raise TypeError("features must be two-dimensionnal")
        if not isinstance(start, np.ndarray):
            raise TypeError("start is not a np.ndarray")
        if start.dtype != "float64":
            raise TypeError("start must have float64 type")
        if not isinstance(stop, np.ndarray):
            raise TypeError("stop is not a np.ndarray")
        if stop.dtype != "float64":
            raise TypeError("stop must have float64 type") 
        if len(start.shape) != 1:
            raise TypeError("start must be one-dimensionnal")
        if len(stop.shape) != 1:
            raise TypeError("stop must be one-dimensionnal") 
        if not isinstance(properties, dict):
            raise TypeError("properties is not a dict")
        rec_properties(properties)

        return cls(pyitem(name, features, start, stop, properties, True))


    def __eq__(self, it) -> bool:
        """Test equality of two Item

        the method test the equality of features, times and properties from the wrapper

        Returns:
            bool: True if equal, else False
        """
        return self.__item == it
    def __ne__(self, it):
        """Test inequality of two Item

        the method test the inequality of features, times and properties from the wrapper

        Returns:
            bool: True if inequal, else False
        """
        return self.__item != it

    def features(self,  copy=False) -> np.ndarray:
        """The method returns the features of the Item

        Allow to return the reference or to do a deepcopy of the features

        Args:
            copy (`bool`): If True, return a deepcopy of the features
                else, return the reference

        Returns:
           np.ndarray : the features

        """
        if copy:
            return deepcopy(np.asarray(self.__item.features(), dtype=np.float64))
        return np.array(self.__item.features(),dtype=np.float64,  copy=False)

    def times(self, copy=False) -> np.ndarray:
        """The method returns the times of the Item

        Allow to return the reference or to do a deepcopy of the times

        Args:
            copy (`bool`): If True, return a deepcopy of the times
                else, return the reference

        Returns:
           np.ndarray : the times

        Notes:
            the times returned is two dimensionnal. The first dimension correspond to the segments according to the features
                the second dimension correspond to two values, the start and the stop of the segment

        """
        if copy:
            return deepcopy(np.asarray(self.__item.times(), dtype=np.float64))
        return np.array(self.__item.times(), dtype=np.float64, copy=False)
    
    def properties(self) -> dict:
        """This method returns the properties of the Item

        Returns:
            dict : the properties
        """
        return self.__item.properties()
    
    
    def set_properties(self, name, value):
        """This method allow to set a new propertie or update an existing propertie

        Args:
            name (`str`): key of propertie
            value : value of properties, see constructor to check the possible types

        Raises:
            TypeError is name is not `str`
        """
        if not isinstance(name, str):
            raise TypeError("name must be str")
        self.__item.properties_set(name, value)

    def has_properties(self) -> bool:
        """This method allow to check if Item has properties

        Returns:
            bool:True if Itme has properties, else False

        """
        return self.__item.has_properties()
    
    def properties_contains(self, name) -> bool:
        """This method allow to check if a propertie exists

        Args:
            name (`str`) : key of propertie

        Raises:
            TypeError is name is not `str`

        Returns:
            bool : True if contains the name, else False
        """
        if not isinstance(name, str):
            raise TypeError("name must be str")
        return self.__item.properties_contains(name)

    def properties_erase(self, name):
        """This method allow to delete a propertie

        Args:
            name (`str`) : key of propertie

        Raises:
            TypeError is name is not `str`
        """
        if not isinstance(name, str):
            raise TypeError("name must be str")
        self.__item.properties_erase(name)

    def ncharacteristic(self) -> int:
        """ This method returns the number of characterics of one segment of features
        
        Returns:
            int: the number of characteristics
        """
        return self.__item.dim()

    def size(self) -> int:
        """This methods the number of segments of features or times

        Returns:
            int: the number of segments

        """
        return self.__item.size()