# Copyright 2014-2019 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
#
# This file is part of h5features.
#
# h5features is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# h5features is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with h5features.  If not, see <http://www.gnu.org/licenses/>.

"""Provides the read() and write() wrapper functions.

.. note::

   For compatibility with h5features 1.0, this legacy top-level API
   have been conserved in this module. Except for use in legacy code,
   it is **better not to use it**. Use instead the `h5features.writer`
   and `h5features.reader` modules.

"""

from .data import Data
from .reader import Reader
from .writer import Writer


def read(filename, groupname=None, from_item=None, to_item=None,
         from_time=None, to_time=None, index=None):
    """Reads in a h5features file.

    :param str filename: Path to a hdf5 file potentially serving as a
        container for many small files

    :param str groupname: HDF5 group to read the data from. If None,
        guess there is one and only one group in `filename`.

    :param str from_item: Optional. Read the data starting from this
        item. (defaults to the first stored item)

    :param str to_item: Optional. Read the data until reaching the
        item. (defaults to from_item if it was specified and to the
        last stored item otherwise)

    :param float from_time: Optional. (defaults to the beginning time
        in from_item) the specified times are included in the output

    :param float to_time: Optional. (defaults to the ending time in
        to_item) the specified times are included in the output

    :param int index: Not implemented, raise if used.

    :return: A tuple (times, features) or (times, features,
        properties) such as:

        * time is a dictionary of 1D arrays values (keys are items).

        * features: A dictionary of 2D arrays values (keys are items)
          with the 'features' dimension along the columns and the
          'time' dimension along the lines.

        * properties: A dictionnary of dictionnaries (keys are items)
          with the corresponding properties. If there is no properties
          recorded, this value is not returned.

    .. note:: Note that all the files that are present on disk between
        to_item and from_item will be loaded and returned. It's the
        responsibility of the user to make sure that it will fit into
        RAM memory.

    """
    # TODO legacy read from index not implemented
    if index is not None:
        raise NotImplementedError

    reader = Reader(filename, groupname)
    data = (reader.read(from_item, to_item, from_time, to_time)
            if index is None else reader.index_read(index))
    if data.has_properties():
        return data.dict_labels(), data.dict_features(), data.dict_properties()
    else:
        return data.dict_labels(), data.dict_features()


def write(filename, groupname, items, times, features, properties=None,
          dformat='dense', chunk_size='auto', sparsity=0.1, mode='a'):
    """Write h5features data in a HDF5 file.

    This function is a wrapper to the Writer class. It has three purposes:

    * Check parameters for errors (see details below),
    * Create Items, Times and Features objects
    * Send them to the Writer.

    :param str filename: HDF5 file to be writted, potentially serving
        as a container for many small files. If the file does not
        exist, it is created. If the file is already a valid HDF5
        file, try to append the data in it.

    :param str groupname: Name of the group to write the data in, or
        to append the data to if the group already exists in the file.

    :param items: List of files from which the features where
        extracted. Items must not contain duplicates.
    :type items: list of str

    :param times: Time value for the features array. Elements of
        a 1D array are considered as the center of the time window
        associated with the features. A 2D array must have 2 columns
        corresponding to the begin and end timestamps of the features
        time window.
    :type times: list of  1D or 2D numpy arrays

    :param features: Features should have
        time along the lines and features along the columns
        (accomodating row-major storage in hdf5 files).
    :type features: list of 2D numpy arrays

    :param properties: Optional. Properties associated with each
        item. Properties describe the features associated with each
        item in a dictionnary. It can store parameters or fields
        recorded by the user.
    :type properties: list of dictionnaries

    :param str dformat: Optional. Which format to store the features
        into (sparse or dense). Default is dense.

    :param float chunk_size: Optional. In Mo, tuning parameter
        corresponding to the size of a chunk in the h5file. By default
        the chunk size is guessed automatically. Tis parameter is
        ignored if the file already exists.

    :param float sparsity: Optional. Tuning parameter corresponding to
        the expected proportion (in [0, 1]) of non-zeros elements on
        average in a single frame.

    :param char mode: Optional. The mode for overwriting an existing
        file, 'a' to append data to the file, 'w' to overwrite it

    :raise IOError: if the filename is not valid or parameters are
        inconsistent.

    :raise NotImplementedError: if dformat == 'sparse'

    """
    # Prepare the data, raise on error
    sparsity = sparsity if dformat == 'sparse' else None
    data = Data(items, times, features, properties=properties,
                sparsity=sparsity, check=True)

    # Write all that stuff in the HDF5 file's specified group
    Writer(filename, chunk_size=chunk_size).write(data, groupname, append=True)


def simple_write(filename, group, times, features,
                 properties=None, item='item', mode='a'):
    """Simplified version of `write()` when there is only one item."""
    write(filename, group, [item], [times], [features], mode=mode,
          properties=[properties] if properties is not None else None)
