# Copyright 2014-2016 Thomas Schatz, Mathieu Bernard, Roland Thiolliere
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
"""Setup script for the h5features package"""

import os
from setuptools import setup, find_packages

VERSION = '1.1.0'

# On Reads The Docs we don't install any package
ON_RTD = os.environ.get('READTHEDOCS', None) == 'True'
REQUIREMENTS = [] if ON_RTD else [
    'h5py >= 2.3.0',
    'numpy >= 1.8.0',
    'scipy >= 0.13.0',
]

setup(
    name='h5features',
    version=VERSION,
    description='efficient storage of large features data',
    long_description=open('README.rst').read(),
    keywords='HDF5 h5py features read write',
    author='Thomas Schatz, Mathieu Bernard, Roland Thiolliere',
    author_email='mmathieubernardd@gmail.com',
    url='https://github.com/bootphon/h5features',
    license='GPLv3',
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
)
