from distutils.core import setup

setup(
    name='h5features',
    version='0.1.0',
    author='Thomas Schatz',
    packages=[],
    # url='http://pypi.python.org/pypi/h5features/',
    license='LICENSE.txt',
    description='h5features format file handler',
    long_description=open('README.rst').read(),
    install_requires=[
        "python >= 2.7",
        "h5py >= 2.3.0",
        "numpy >= 1.8.0",
        "scipy.sparse >= 0.13.0"
    ],
)
