"""Provides some utility finctions for testing h5features.

@author: thiolliere
@author: Mathieu Bernard
"""

import filecmp
import os
import pytest
import subprocess

def cmp(f1, f2):
    """Compare two files.

    Return True if f1 and f2 are equal, False else. Equality is
    checked only on file descriptors (see os.stat).
    """
    return filecmp.cmp(f1, f2, shallow=True)

def h5cmp(f1, f2):
    """Compare two HDF5 files.

    Return True if f1 and f2 are equal, False else. Equality is
    checked with the 'h5diff' external process.
    """

    try:
        out = subprocess.check_output(['h5diff', f1, f2])
    except subprocess.CalledProcessError:
        return False

    if out:
        return False
    return True

def assert_raise(func, arg, msg, except_type=IOError):
    """Assert that func(arg) raises a specified exception containing msg."""
    with pytest.raises(except_type) as error:
        func(arg)
    assert msg in str(error.value)


def remove(filename):
    """Remove the file if it exists."""
    if os.path.exists(filename):
        os.remove(filename)
