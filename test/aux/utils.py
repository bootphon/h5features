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
"""Provides some utility finctions for testing h5features."""

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
