"""Provides the Reader class to the h5features package."""

import h5py
import numpy as np

from .index import Index, IndexV0_1, IndexV1_0
from .utils import is_supported_version
from .dataset.items import Items
from .dataset.features import Features
from .dataset.times import Times

class Reader(object):
    """This class enables reading from h5features files.

        The **Reader** constructor open an HDF5 file for reading and
        load its index.

        Parameters

        *filename* : str --- hdf5 file potentially serving as a
        container for many small files.

        *groupname* : str --- h5 group to read the data from.

        *index* : int, optional -- for faster access.

        Raise
        -----

        IOError if *filename* is not an existing HDF5 file.
        IOError if *groupname* is not a valid group in *filename*.

    .. note:: **The functions are not concurrent nor thread-safe**
        because the HDF5 library is not concurrent and not always
        thread-safe. Moreover, they aren't even atomic for independent
        process (because there are several independent calls to the
        file system), so that thread-safety and atomicity of
        operations should be enforced externally when necessary.

    """
    # TODO Check the group contains a valid h5features structure.
    def __init__(self, filename, groupname, index=None):
        """Initializes a h5features reader to read a group in a HDF5 file."""

        # check filename
        if not h5py.is_hdf5(filename):
            raise IOError('{} is not a HDF5 file'.format(filename))
        self.filename = filename

        # open the HDF5 file for reading
        self.h5file = h5py.File(self.filename, 'r')

        # access to the requested group
        if not groupname in self.h5file:
            raise IOError('{} is not a valid group in {}'
                          .format(groupname, self.filename))
        self.groupname = groupname
        self.group = self.h5file[groupname]

        # Get the version of the readed file
        self.version = self._read_version()

        # read the index from group if not provided
        if index is None:
            # Choose the good index according to file version
            if self.version == '0.1':
                index_class = IndexV0_1()
            elif self.version == '1.0':
                index_class = IndexV1_0()
            else:
                index_class = Index()

            self.index = index_class.read(self.group)
        else:
            self.index = index

    def _read_version(self):
        """Return the h5features version of the readed file.

        This method raise IOError if version is not either 0.1, 1.0 or 1.1

        """
        version = ('0.1' if not 'version' in self.group.attrs
                   else self.group.attrs['version'])

        # decode from bytes to str
        if type(version) == bytes:
            version = version.decode()

        if not is_supported_version(version):
            raise IOError('version {} is not supported'.format(version))

        return version

    def read(self, from_item=None, to_item=None,
             from_time=None, to_time=None):
        """Retrieve requested datasets coordinates from the h5features index.

        Parameters
        ----------

        from_item : str, optional --- Read the data starting from this
            item. (defaults to the first stored item)

        to_item : str, optional --- Read the data until reaching the
            item. (defaults to from_item if it was specified and to
            the last stored item otherwise).

        from_time : float, optional --- (defaults to the beginning
            time in from_item) the specified times are included in the
            output.

        to_time : float, optional --- (defaults to the ending time in
            to_item) the specified times are included in the output.

        """

        from_item, to_item = self._get_items(from_item, to_item)

        # index coordinates associated with the begin/end of from/to_item
        # TODO put that in Index ?
        index_group = self.index['index']
        item1_start = 0 if from_item == 0 else index_group[from_item - 1] + 1
        item1_end = index_group[from_item]

        item2_start = 0 if to_item == 0 else index_group[to_item - 1] + 1
        item2_end = index_group[to_item]

        # TODO Factorize those two methods
        i1 = self._get_from_time(from_time, from_item, item1_start, item1_end)
        i2 = self._get_to_time(to_time, to_item, item2_start, item2_end)

        # Step 2: access actual data
        features_group = self.group['features']
        if self.index['format'] == 'sparse':
            # TODO implement this. will be different for v1.0 and legacy
            raise IOError('reading sparse features not yet implemented')
        else:
            # i2 included
            features = (features_group[:, i1:i2 + 1].T if self.version == '0.1'
                        else features_group[i1:i2 + 1, :])
            times = self.group['times'][i1:i2 + 1]

        # If we read a single item
        if to_item == from_item:
            features = [features]
            times = [times]
        # Several items case
        else:
            item_ends = index_group[from_item:to_item] - item1_start
            # TODO change axis from 1 to 0, but need to check that this doesn't
            # break compatibility with matlab generated files
            features = np.split(features, item_ends + 1, axis=0)
            times = np.split(times, item_ends + 1)

        items = self.index['items'][from_item:to_item + 1]
        return (Items(items),
                Times(times),
                Features(features))

    def _get_items(self, from_item, to_item):
        """Look for the given items in the indexed items list."""
        items_group = self.index['items']

        if to_item is None:
            to_item = items_group[-1] if from_item is None else from_item
        if from_item is None:
            from_item = items_group[0]

        res = []
        for item in [from_item, to_item]:
            try:
                res.append(items_group.index(item))
            except ValueError:
                raise IOError('No entry for item {} in the group {} in {}'
                              .format(item, self.groupname, self.filename))

        if not res[1] >= res[0]:
            raise IOError('from_item {} is located after to_item {} in file {}'
                          .format(res[0], res[1], self.filename))

        return res[0], res[1]

    def _get_from_time(self, from_time, from_item, item_start, item_end):
        times_group = self.index['times']
        if from_time is None:
            i1 = item_start
        else:
            # the end is included...
            times = times_group[item_start:item_end + 1]
            try:
                # smallest time larger or equal to from_time
                i1 = item_start + np.where(times >= from_time)[0][0]
            except IndexError:
                raise IOError('from_time {} is larger than the biggest time in '
                              'from_item {}'.format(from_time, from_item))
        return i1

    def _get_to_time(self, to_time, to_item, item_start, item_end):
        times_group = self.index['times']
        if to_time is None:
            i2 = item_end
        else:
            # the end is included...
            times = times_group[item_start:item_end + 1]
            try:
                # smallest time larger or equal to from_time
                i2 = item_start + np.where(times <= to_time)[0][-1]
            except IndexError:
                raise IOError('to_time {} is smaller than the smallest time in '
                              'to_item {}'.format(to_time, to_item))
        return i2
