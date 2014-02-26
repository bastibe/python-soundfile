#!/usr/bin/env python
from setuptools import setup
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
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Multimedia :: Sound/Audio'
    ],
    long_description='''
    PySoundFile can read and write sound files.

    PySoundFile can read and write sound files. File reading/writing is
    supported through libsndfile_, which is a free, cross-platform,
    open-source library for reading and writing many different sampled
    sound file formats that runs on many platforms including Windows, OS
    X, and Unix. It is accessed through CFFI_, which is a foreight
    function interface for Python calling C code. CFFI is supported for
    CPython 2.6+, 3.x and PyPy 2.0+. PySoundFile represents audio data as
    NumPy arrays.

    You must have libsndfile installed in order to use PySoundFile.

    .. _libsndfile: http://www.mega-nerd.com/libsndfile/
    .. _CFFI: http://cffi.readthedocs.org/

    Note that you need to have libsndfile installed in order to use
    PySoundFile. On Windows, you need to rename the library to
    "sndfile.dll".

    ''')
