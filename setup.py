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

VERSION = open('VERSION').read().strip()

HERE = os.path.dirname(os.path.abspath(__file__))

# On Reads The Docs we don't install any package
ON_RTD = os.environ.get('READTHEDOCS', None) == 'True'
REQUIREMENTS = (
    [] if ON_RTD else open('requirements.txt').read().strip().split())

setup(
    name='h5features',
    version=VERSION,
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    zip_safe=True,
    install_requires=REQUIREMENTS,

    # install the convert2h5features script
    entry_points={'console_scripts': [
        'convert2h5features = h5features.convert2h5features:main']},

    # metadata for upload to PyPI
    author='Thomas Schatz, Mathieu Bernard, Roland Thiolliere',
    author_email='mathieu.a.bernard@inria.fr',
    description='efficient storage of large features data',
    keywords='HDF5 h5py features read write',
    url='https://github.com/bootphon/h5features',
    license='GPLv3',
    long_description=open(os.path.join(HERE, 'README.rst')).read(),
    long_description_content_type='text/x-rst'
)
