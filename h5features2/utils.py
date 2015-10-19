"""Provides functions related to h5features2 package."""

def is_supported_version(version):
    """Return True if the version is supported by h5features2."""
    supported_versions = ['0.1', '1.0', '1.1']
    return version in supported_versions


def nb_lines(item_size, n_columns, size_in_mem):
    """Item_size given in bytes, size_in_mem given in kilobytes."""
    return int(round(size_in_mem * 1000. / (item_size * n_columns)))
