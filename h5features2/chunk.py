"""Provides functions related to HDF5 chunking."""

def nb_lines(item_size, n_columns, size_in_mem):
    """Item_size given in bytes, size_in_mem given in kilobytes."""
    return int(round(size_in_mem * 1000. / (item_size * n_columns)))


def check_size(chunk_size):
    """Raise IOError if the size of a chunk (in Mo) is below 8 Ko."""
    if chunk_size < 0.008:
        raise IOError('chunk size below 8 Ko are not allowed as they'
                      ' result in poor performances.')
