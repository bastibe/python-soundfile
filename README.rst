PySoundFile
===========

PySoundFile is an audio library based on libsndfile, CFFI and Numpy

PySoundFile can read and write sound files. File reading/writing is
supported through `libsndfile <http://www.mega-nerd.com/libsndfile/>`__,
which is a free, cross-platform, open-source library for reading and
writing many different sampled sound file formats that runs on many
platforms including Windows, OS X, and Unix. It is accessed through
`CFFI <http://cffi.readthedocs.org/>`__, which is a foreign function
interface for Python calling C code. CFFI is supported for CPython 2.6+,
3.x and PyPy 2.0+. PySoundFile represents audio data as NumPy arrays.

| PySoundFile is BSD licensed.
| (c) 2013, Bastian Bechtold

Installation
------------

On the Python side, you need to have CFFI and Numpy in order to use
PySoundFile. Additionally, You need the library libsndfile installed on
your computer. On Unix, use your package manager to install libsndfile.
Then just install PySoundFile using pip or ``python setup.py install``.

If you are running Windows, I recommend using
`WinPython <http://winpython.github.io/>`__ or some similar
distribution. This should set you up with Numpy. However, you also need
CFFI and it's dependency, PyCParser. A good place to get these are the
`Unofficial Windows Binaries for
Python <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`__. Having installed
those, you can download the Windows installers for PySoundFile:

| `PySoundFile-0.5.0.win-amd64-py2.7 <https://github.com/bastibe/PySoundFile/releases/download/0.5.0/PySoundFile-0.5.0.win-amd64-py2.7.exe>`__
| `PySoundFile-0.5.0.win-amd64-py3.3 <https://github.com/bastibe/PySoundFile/releases/download/0.5.0/PySoundFile-0.5.0.win-amd64-py3.3.exe>`__
| `PySoundFile-0.5.0.win32-py2.7 <https://github.com/bastibe/PySoundFile/releases/download/0.5.0/PySoundFile-0.5.0.win32-py2.7.exe>`__
| `PySoundFile-0.5.0.win32-py3.3 <https://github.com/bastibe/PySoundFile/releases/download/0.5.0/PySoundFile-0.5.0.win32-py3.3.exe>`__

Usage
-----

Each SoundFile can either open a sound file on the disk, or a file-like
object (using ``libsndfile``'s `virtual file
interface <http://www.mega-nerd.com/libsndfile/api.html#open_virtual>`__).
Every sound file has a specific samplerate, data format and a set number
of channels.

You can read and write any file that
`libsndfile <http://www.mega-nerd.com/libsndfile/#Features>`__ can
open. This includes Microsoft WAV, OGG, FLAC and Matlab MAT files.

If a file on disk is opened, it is kept open for as long as the
SoundFile object exists and closes automatically when it goes out of
scope. Alternatively, the SoundFile object can be used as a context
manager, which closes the file when it exits.

All data access uses frames as index. A frame is one discrete time-step
in the sound file. Every frame contains as many samples as there are
channels in the file.

Read/Write Functions
~~~~~~~~~~~~~~~~~~~~

Data can be written to the file using ``write()``, or read from the
file using ``read()``.

Here is an example for a program that reads a wave file and copies it
into an ogg-vorbis file:

.. code:: python

    import pysoundfile as sf

    data, samplerate = sf.read('existing_file.wav')
    sf.write(data, 'new_file.ogg', samplerate=samplerate)

Virtual IO
~~~~~~~~~~

If you have an open file-like object, you can use something similar to
this to decode it:

.. code:: python

    from pysoundfile import SoundFile
    with SoundFile('filename.flac', 'rb') as fObj:
        data, samplerate = sf.read(fObj)

Here is an example using an HTTP request:

.. code:: python

    from io import BytesIO
    import pysoundfile as sf
    import requests

    fObj = BytesIO()
    response = requests.get('http://www.example.com/my.flac', stream=True)
    for data in response.iter_content(4096):
        if data:
            fObj.write(data)
    fObj.seek(0)
    data, samplerate = sf.read(fObj)

Accessing Text Data
~~~~~~~~~~~~~~~~~~~

In addition to audio data, there are a number of text fields in every
sound file. In particular, you can set a title, a copyright notice, a
software description, the artist name, a comment, a date, the album
name, a license, a tracknumber and a genre. Note however, that not all
of these fields are supported for every file format.

News
----

2013-08-27 V0.1.0 Bastian Bechtold:
    Initial prototype. A simple wrapper for libsndfile in Python

2013-08-30 V0.2.0 Bastian Bechtold:
    Bugfixes and more consistency with PySoundCard

2013-08-30 V0.2.1 Bastian Bechtold:
    Bugfixes

2013-09-27 V0.3.0 Bastian Bechtold:
    Added binary installer for Windows, and context manager

2013-11-06 V0.3.1 Bastian Bechtold:
    Switched from distutils to setuptools for easier installation

2013-11-29 V0.4.0 Bastian Bechtold:
    Thanks to David Blewett, now with Virtual IO!

2013-12-08 V0.4.1 Bastian Bechtold:
    Thanks to Xidorn Quan, FLAC files are not float32 any more.

2014-02-26 V0.5.0 Bastian Bechtold:
    Thanks to Matthias Geier, improved seeking.
