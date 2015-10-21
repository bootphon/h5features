# coding: utf-8

"""A setup module for the h5features2 python package"""

from setuptools import setup, find_packages
#from codecs import open
from os import path

# Get the long description from the README file
HERE = path.abspath(path.dirname(__file__))
with open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='h5features2',
    version='0.1.1',
    license='MIT',

    description='h5features format file handler',
    long_description=LONG_DESCRIPTION,
    url='https://github.com/bootphon/h5features',

    author='Thomas Schatz, Roland Thiollière, Mathieu Bernard',
    author_email='mmathieubernardd@gmail.com',

    packages=find_packages(exclude=['docs', 'test']),

    install_requires=[
        #'python >= 2.7',
        'h5py >= 2.3.0',
        'numpy >= 1.8.0',
        'scipy >= 0.13.0',
        'numpydoc'
    ],
)
