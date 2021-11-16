"""Implementation of the class h5features.Item"""
import numpy as np
from _h5features import ItemWrapper


# an immutable dictionnay to store item properties, from
# https://www.python.org/dev/peps/pep-0351/
class _immutable_dict(dict):
    def __hash__(self):
        return id(self)

    def _immutable(self, *args, **kws):
        raise ValueError('properties are read-only')

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable
    pop = _immutable
    popitem = _immutable


class Item:
    """Handles temporal numerical data related to a single item.

    An ``Item`` instance is at the interface between
    :class:`~h5features.Reader` / :class:`~h5features.Writer` and user code. By
    design an ``Item`` instance is not modifiable once created. It is made of a
    **name**, some **features** attached to **times** stamps and optional
    **properties**.

    Parameters
    ----------
    name : str
      The name of the item

    features : numpy.ndarray, shape = [nframes, ndims], type = np.float64
      The underlying data matrix as a two-dimensionnal array.

    times : numpy.ndarray, shape = [nframes, 1 or 2], type = np.float64
      The timestamps in seconds associated to each features frame. If
      timestamps have a single dimension they are interpreted as the
      ``tcenter`` time of the associated frames. If timestamps have two
      dimensions, they are interpreted as the ``(tstart, tstop)`` times of the
      frames.

    properties : dict, optional
      An optional dictionnary to record item's properties and metadata. Key
      must be ``str``. Values can be one of ``bool``, ``int``, ``float``,
      ``str``, ``list of int``, ``list of float``, ``list of str`` or nested
      ``properties``.

    Raises
    ------
    RuntimeError
        If the item features, times or properties are not valid.

    """
    def __init__(self, name, features, times, properties=None):
        if not isinstance(name, str):
            raise RuntimeError('item name must be str')

        if not (isinstance(times, np.ndarray) and times.dtype == 'float64'):
            raise RuntimeError('times is not a float64 numpy array')
        if times.ndim not in (1, 2):
            raise RuntimeError('times is not a 1D or 2D numpy array')
        # force as a 2D array. From shape (n,) to (n, 1).
        if times.ndim == 1:
            times = np.reshape(times, (-1, 1))

        if not (
                isinstance(features, np.ndarray) and
                features.dtype == 'float64' and
                features.ndim == 2):
            raise RuntimeError('features is not a 2D float64 numpy array')

        # from None to empty dict
        properties = properties or {}
        self._check_properties(properties)

        # force item validation to ensure consistency from C++ side
        validate = True
        self._item = ItemWrapper(name, features, times, properties, validate)

    @classmethod
    def _check_properties(cls, properties):
        """Ensure properties are valid"""
        if not isinstance(properties, dict):
            raise RuntimeError('properties is not a dict')

        for key, value in properties.items():
            if isinstance(value, np.floating):
                # convert numpy floats to pure Python floats
                value = float(value)
                properties[key] = value

            if not isinstance(key, str):
                raise RuntimeError('property keys must be str')
            if not isinstance(value, (bool, int, float, str, list, dict)):
                raise RuntimeError(
                    f'property value type invalid: {type(value)}')

            if isinstance(value, list):
                ltype = type(value[0])
                # TODO the dict here pass but do not work
                if not isinstance(value[0], (int, float, str, dict)):
                    raise RuntimeError(
                        f'property value type invalid: list of {ltype}')
                if not all(isinstance(v, ltype) for v in value):
                    raise RuntimeError(
                        'property list must be homogoneous')

            if isinstance(value, dict):
                cls._check_properties(value)

    def __eq__(self, other) -> bool:
        """Returns True if the two items are equal, False otherwise"""
        if not isinstance(other, Item):
            return False
        return self._item == other._item

    def __ne__(self, other):
        """Returns Fasle if the two items are not equal, True otherwise"""
        if not isinstance(other, Item):
            return True
        return self._item != other._item

    @property
    def name(self) -> str:
        """The item's name"""
        return self._item.name()

    @property
    def dim(self) -> int:
        """Features frame dimension"""
        return self._item.dim()

    @property
    def size(self) -> int:
        """Number of frames"""
        return self._item.size()

    @property
    def features(self) -> np.ndarray:
        """A reference to the item's features"""
        return self._item.features()

    @property
    def times(self) -> np.ndarray:
        """A reference to the item's timestamps"""
        return self._item.times()

    @property
    def properties(self) -> dict:
        """A reference to the item's properties"""
        return _immutable_dict(self._item.properties())
