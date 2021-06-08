#!/usr/bin/env python
"""Installation script for the h5features Python library"""

import multiprocessing
import os
import pathlib
import platform
import subprocess
import sys
import setuptools
import setuptools.command.build_ext


H5FEATURES_ROOT_DIR = pathlib.Path(__file__).parent
H5FEATURES_BUILD_DIR = H5FEATURES_ROOT_DIR / 'build'
H5FEATURES_VERSION_FILE = H5FEATURES_ROOT_DIR / 'VERSION'
H5FEATURES_VERSION = open(H5FEATURES_VERSION_FILE, 'r').read().strip()


class CMakeExtension(setuptools.Extension):
    def __init__(self, name, sourcedir=''):
        setuptools.Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(setuptools.command.build_ext.build_ext):
    def run(self):
        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: " +
                ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    @staticmethod
    def build_njobs():
        """Number of parallel jobs to use for compilation"""
        if 'BUILD_NJOBS' in os.environ:
            return os.environ['BUILD_NJOBS']
        return multiprocessing.cpu_count()

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(
            self.get_ext_fullpath(ext.name)))

        cmake_args = [
            '-DH5FEATURES_BUILD_PYTHON=ON',
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}']

        if platform.system() == "Windows":
            cmake_args += [
                f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={extdir}']
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args = ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=Release']
            build_args = ['--', f'-j{self.build_njobs()}']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''), self.distribution.get_version())

        if not os.path.exists(H5FEATURES_BUILD_DIR):
            os.makedirs(H5FEATURES_BUILD_DIR)

        # configure
        subprocess.check_call(
            ['cmake', ext.sourcedir] + cmake_args,
            cwd=H5FEATURES_BUILD_DIR, env=env)

        # build
        subprocess.check_call(
            ['cmake', '--build', '.'] + build_args,
            cwd=H5FEATURES_BUILD_DIR)


setuptools.setup(
    name="h5features",
    version=H5FEATURES_VERSION,
    python_requires=">=3.8",
    setup_requires=['cmake>=3.12'],
    install_requires=["numpy"],
    ext_modules=[CMakeExtension('_h5features')],
    cmdclass={'build_ext': CMakeBuild},
    packages=['h5features'],
    package_dir={'': 'python'},
    zip_safe=True)
