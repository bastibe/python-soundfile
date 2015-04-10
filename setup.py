#!/usr/bin/env python
import os
from platform import architecture
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

# environment variables for cross-platform package creation
platform = os.environ.get('PYSOUNDFILE_PLATFORM', sys.platform)
architecture0 = os.environ.get('PYSOUNDFILE_ARCHITECTURE', architecture()[0])

if platform == 'darwin':
    libname = 'libsndfile.dylib'
elif platform == 'win32':
    libname = 'libsndfile' + architecture0 + '.dll'
else:
    libname = None

if libname:
    packages = ['pysoundfile_data']
    package_data = {'pysoundfile_data': [libname, 'COPYING']}
else:
    packages = None
    package_data = None


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='PySoundFile',
    version='0.7.0',
    description='An audio library based on libsndfile, CFFI and NumPy',
    author='Bastian Bechtold',
    author_email='basti@bastibe.de',
    url='https://github.com/bastibe/PySoundFile',
    keywords=['audio', 'libsndfile'],
    py_modules=['soundfile'],
    packages=packages,
    package_data=package_data,
    license='BSD 3-Clause License',
    install_requires=['numpy',
                      'cffi>=0.6'],
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Multimedia :: Sound/Audio'
    ],
    long_description=open('README.rst').read(),
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
