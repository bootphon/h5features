# coding: utf-8
'''
h5features

Note that "python setup.py test" invokes pytest on the package. With appropriately
configured setup.cfg, this will check both xxx_test modules and docstrings.

Copyright 2015, Mathieu Bernard.
Licensed under GPLv3.
'''
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

# This is a plug-in for setuptools that will invoke py.test
# when you run python setup.py test
class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, because outside the required eggs aren't loaded yet
        import pytest
        sys.exit(pytest.main(self.test_args))

version = "1.1.0"

setup(name='h5features',
      version=version,
      description='h5features format file handler',
      long_description=open('README.rst').read(),
      classifiers=[
          # See from http://pypi.python.org/pypi?%3Aaction=list_classifiers
          'Development Status :: 1 - Planning',
          'Programming Language :: Python'
      ],
      keywords='HDF5 h5py features',
      author='Thomas Schatz, Roland Thiolliere, Mathieu Bernard',
      author_email='mmathieubernardd@gmail.com',
      url='https://github.com/mmmaat/h5features',
      license='GPLv3',
      packages=find_packages(exclude=['test']),
      include_package_data=True,
      zip_safe=False,
      tests_require=['pytest'],
      cmdclass={'test': PyTest},
      install_requires=[
        #'python >= 2.7',
        'h5py >= 2.3.0',
        'numpy >= 1.8.0',
        'scipy >= 0.13.0',
        'numpydoc'
      ],
  )
