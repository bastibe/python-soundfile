#!/usr/bin/env python
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand
from sys import platform
from platform import architecture
import shutil

if platform == 'win32' and architecture()[0] == '32bit':
    shutil.copy2('win/sndfile32.dll', 'win/sndfile.dll')
    sndfile = [('', ['win/sndfile.dll', 'win/sndfile_license'])]
elif platform == 'win32' and architecture()[0] == '64bit':
    shutil.copy2('win/sndfile64.dll', 'win/sndfile.dll')
    sndfile = [('', ['win/sndfile.dll', 'win/sndfile_license'])]
else:
    sndfile = []


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
    version='0.5.0',
    description='An audio library based on libsndfile, CFFI and NumPy',
    author='Bastian Bechtold',
    author_email='basti@bastibe.de',
    url='https://github.com/bastibe/PySoundFile',
    keywords=['audio', 'libsndfile'],
    py_modules=['pysoundfile'],
    data_files=sndfile,
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
    cmdclass = {'test': PyTest},
)
