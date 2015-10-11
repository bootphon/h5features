"""A setup module for the h5features2 python package"""

from setuptools import setup, find_packages
from codecs import open
from os import path

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='h5features2',
    version='0.1.2',
    license='MIT',

    description='h5features format file handler',
    long_description=long_description,
    url='https://github.com/bootphon/h5features',

    author='LSCP bootphon team',
    author_email='syntheticlearner@gmail.com',

    packages=find_packages(exclude=['doc', 'test']),

    install_requires=[
        #'python >= 2.7',
        'h5py >= 2.3.0',
        'numpy >= 1.8.0',
        'scipy >= 0.13.0',
        'numpydoc'
    ],
)
