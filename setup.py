#!/usr/bin/env python

import os
import platform
import setuptools
import setuptools.command.build_ext
import subprocess
import sys


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

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(
            self.get_ext_fullpath(ext.name)))
        cmake_args = [
            '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
            '-DPYTHON_EXECUTABLE=' + sys.executable]

        if platform.system() == "Windows":
            cmake_args += [
                '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_RELEASE={}'.format(extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            build_args = ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=RELEASE']
            build_args = ['--', '-j']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''), self.distribution.get_version())

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # configure
        subprocess.check_call(
            ['cmake', ext.sourcedir] + cmake_args,
            cwd=self.build_temp, env=env)

        # build
        subprocess.check_call(
            ['cmake', '--build', '.'] + build_args,
            cwd=self.build_temp)


setuptools.setup(
    name='h5features',
    setup_requires=['cmake>=3.10'],
    ext_modules=[CMakeExtension('h5features')],
    cmdclass={'build_ext': CMakeBuild}
)
