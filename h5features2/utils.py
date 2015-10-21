"""Provides functions related to h5features2 package."""
# TODO name this version.py and puts here the doc related on
# versioning, diff between versions, converter.
def is_supported_version(version):
    """Return True if the version is supported by h5features2."""
    supported_versions = ['0.1', '1.0', '1.1']
    return version in supported_versions
