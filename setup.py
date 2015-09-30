#!/usr/bin/env python
import os
from platform import architecture
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

PYTHON_INTERPRETERS = '.'.join([
    'cp26', 'cp27',
    'cp32', 'cp33', 'cp34', 'cp35',
    'pp27',
    'pp32',
])
MACOSX_VERSIONS = '.'.join([
    'macosx_10_5_x86_64',
    'macosx_10_6_intel',
    'macosx_10_9_intel',
    'macosx_10_9_x86_64',
])

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
    packages = ['_soundfile_data']
    package_data = {'_soundfile_data': [libname, 'COPYING']}
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

cmdclass = {'test': PyTest}

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    pass
else:
    class bdist_wheel_half_pure(bdist_wheel):
        """Create OS-dependent, but Python-independent wheels."""
        def get_tag(self):
            pythons = 'py2.py3.' + PYTHON_INTERPRETERS
            if platform == 'darwin':
                oses = MACOSX_VERSIONS
            elif platform == 'win32':
                if architecture0 == '32bit':
                    oses = 'win32'
                else:
                    oses = 'win_amd64'
            else:
                pythons = 'py2.py3'
                oses = 'any'
            return pythons, 'none', oses

    cmdclass['bdist_wheel'] = bdist_wheel_half_pure

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
    install_requires=['cffi>=0.6'],
    extras_require={'numpy': ['numpy']},
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
        'Topic :: Multimedia :: Sound/Audio',
    ],
    long_description=open('README.rst').read(),
    tests_require=['pytest'],
    cmdclass=cmdclass,
)
