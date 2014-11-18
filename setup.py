#!/usr/bin/env python
import setuptools
from setuptools import setup
from sys import platform
from platform import architecture
import shutil


setup(
    name='PySoundFile',
    version='0.5.0',
    description='An audio library based on libsndfile, CFFI and NumPy',
    author='Bastian Bechtold',
    author_email='basti@bastibe.de',
    url='https://github.com/bastibe/PySoundFile',
    keywords=['audio', 'libsndfile'],
    packages=setuptools.find_packages(),
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
    long_description=open('README.rst').read(),
    zip_safe=False,
    include_package_data=True,
    package_data={'pysoundfile': [
        'pysoundfile/win/sndfile32.dll',
        'pysoundfile/win/sndfile64.dll',
        'pysoundfile/win/sndfile_license']
    },
)
