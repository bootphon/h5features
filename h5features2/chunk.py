"""Provides functions related to HDF5 chunking."""

def nb_lines(item_size, n_columns, size_in_mem):
    """Item_size given in bytes, size_in_mem given in kilobytes."""
    return int(round(size_in_mem * 1000. / (item_size * n_columns)))
