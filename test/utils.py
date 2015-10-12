"""Provides some utility finctions for testing h5features."""

import os
import pytest

def assert_raise(func, arg, msg, except_type=IOError):
    """Assert that func(arg) raises a specified exception containing msg."""
    with pytest.raises(except_type) as error:
        func(arg)
    assert msg in str(error.value)


def remove(filename):
    """Remove the file if it exists."""
    if os.path.exists(filename):
        os.remove(filename)
