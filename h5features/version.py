"""Provides functions related to h5features versions."""
# TODO puts here the doc related on diff between versions, converter.


SUPPORTED_VERSIONS = ['0.1', '1.0', '1.1']
"""The different versions supported by the h5features module """


def is_supported_version(version):
    """Return True if the version is supported by h5features."""
    return version in SUPPORTED_VERSIONS


def is_same_version(version, group):
    """Return True if *version* and *group* versions are equals."""
    return version == read_version(group)


def read_version(group):
    """Return the h5features version of a given HDF5 *group*.

    This method raise IOError if version is not supported.

    """
    version = ('0.1' if not 'version' in group.attrs
               else group.attrs['version'])

    # decode from bytes to str if needed
    if type(version) == bytes:
        version = version.decode()

    if not is_supported_version(version):
        raise IOError('version {} is not supported'.format(version))

    return version
