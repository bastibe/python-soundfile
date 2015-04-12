PySoundFile
===========

`PySoundFile <https://github.com/bastibe/PySoundFile>`__ is an audio
library based on libsndfile, CFFI and Numpy. Full documentation is
available on http://pysoundfile.readthedocs.org/.

PySoundFile can read and write sound files. File reading/writing is
supported through `libsndfile <http://www.mega-nerd.com/libsndfile/>`__,
which is a free, cross-platform, open-source (LGPL) library for reading
and writing many different sampled sound file formats that runs on many
platforms including Windows, OS X, and Unix. It is accessed through
`CFFI <http://cffi.readthedocs.org/>`__, which is a foreign function
interface for Python calling C code. CFFI is supported for CPython 2.6+,
3.x and PyPy 2.0+. PySoundFile represents audio data as NumPy arrays.

| PySoundFile is BSD licensed (BSD 3-Clause License).
| (c) 2013, Bastian Bechtold


Breaking Changes
----------------

PySoundFile has evolved rapidly during the last few releases. Most
notably, we changed the import name from ``import pysoundfile`` to
``import soundfile`` in 0.7. In 0.6, we cleaned up many small
inconsistencies, particularly in the the ordering and naming of
function arguments and the removal of the indexing interface.

Installation
------------

PySoundFile depends on the Python packages CFFI and Numpy, and the
system library libsndfile.

To install the Python dependencies, I recommend using the `Anaconda
<http://continuum.io/downloads#34>`__ Distribution of Python. Anaconda
provides the ``conda`` package manager, which will install all
dependencies using ``conda install cffi numpy`` (conda is also
independently available on pip).

You will also need to install `libsndfile
<http://www.mega-nerd.com/libsndfile/>`__. On Windows, libsndfile is
included in the binary installers (see below). On OS X, `homebrew
<http://www.mega-nerd.com/libsndfile/>`__ can install libsndfile using
``brew install libsndfile``. On Linux, use your distribution's package
manager, for example ``sudo apt-get install libsndfile``.

With CFFI, Numpy, and libsndfile installed, you can use `pip
<http://pip.readthedocs.org/en/latest/installing.html>`__ to install
`PySoundFile <https://pypi.python.org/pypi/PySoundFile/0.6.0>`__ with
``pip install pysoundfile`` or ``pip install pysoundfile --user`` if you
don't have administrator privileges. If you are running Windows you
should download the Windows installers for PySoundFile instead (which
also include libsndfile):

| `PySoundFile-0.6.0.win-amd64-py2.7 <https://github.com/bastibe/PySoundFile/releases/download/0.6.0/PySoundFile-0.6.0.win-amd64-py2.7.exe>`__
| `PySoundFile-0.6.0.win-amd64-py3.4 <https://github.com/bastibe/PySoundFile/releases/download/0.6.0/PySoundFile-0.6.0.win-amd64-py3.4.exe>`__
| `PySoundFile-0.6.0.win32-py2.7 <https://github.com/bastibe/PySoundFile/releases/download/0.6.0/PySoundFile-0.6.0.win32-py2.7.exe>`__
| `PySoundFile-0.6.0.win32-py3.4 <https://github.com/bastibe/PySoundFile/releases/download/0.6.0/PySoundFile-0.6.0.win32-py3.4.exe>`__

Read/Write Functions
--------------------

Data can be written to the file using ``write()``, or read from the file
using ``read()``. PySoundFile can open all file formats that `libsndfile
supports <http://www.mega-nerd.com/libsndfile/#Features>`__, for example
WAV, FLAC, OGG and MAT files.

Here is an example for a program that reads a wave file and copies it
into an ogg-vorbis file:

.. code:: python

    import soundfile as sf

    data, samplerate = sf.read('existing_file.wav')
    sf.write(data, 'new_file.ogg', samplerate=samplerate)

Block Processing
----------------

Sound files can also be read in short, optionally overlapping blocks.
For example, this calculates the signal level for each block of a long
file:

.. code:: python

   import numpy as np
   import soundfile as sf

   rms = [np.sqrt(np.mean(block**2)) for block in
          sf.blocks('myfile.wav', blocksize=1024, overlap=512)]

SoundFile Objects
-----------------

Sound files can also be opened as SoundFile objects. Every SoundFile
has a specific sample rate, data format and a set number of channels.

If a file is opened, it is kept open for as long as the SoundFile
object exists. The file closes when the object is garbage collected,
but you should use the ``close()`` method or the context manager to
close the file explicitly:

.. code:: python

   import soundfile as sf

   with sf.SoundFile('myfile.wav', 'rw') as f:
       while f.tell() < len(f):
           pos = f.tell()
           data = f.read(1024)
           f.seek(pos)
           f.write(data*2)

All data access uses frames as index. A frame is one discrete time-step
in the sound file. Every frame contains as many samples as there are
channels in the file.

RAW Files
---------

Pysoundfile can usually auto-detect the file type of sound files. This
is not possible for RAW files, though. This is a useful idiom for
opening RAW files without having to provide all the format for every
file:

.. code:: python

   import soundfile as sf

   format = {'format':'RAW', 'subtype':'FLOAT', 'endian':'FILE'}
   data = sf.read('myfile.raw', dtype='float32', **format)
   sf.write(data, 'otherfile.raw', **format)

Virtual IO
----------

If you have an open file-like object, Pysoundfile can open it just like
regular files:

.. code:: python

    import soundfile as sf
    with open('filename.flac', 'rb') as f:
        data, samplerate = sf.read(f)

Here is an example using an HTTP request:

.. code:: python

    from io import BytesIO
    import soundfile as sf
    import requests

    f = BytesIO()
    response = requests.get('http://www.example.com/my.flac', stream=True)
    for data in response.iter_content(4096):
        if data:
            f.write(data)
    f.seek(0)
    data, samplerate = sf.read(f)

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
    Thanks to Matthias Geier, improved seeking and a flush() method.

2015-01-19 V0.6.0 Bastian Bechtold:
    A big, big thank you to Matthias Geier, who did most of the work!

    - Switched to ``float64`` as default data type.
    - Function arguments changed for consistency.
    - Added unit tests.
    - Added global ``read()``, ``write()``, ``blocks()`` convenience
      functions.
    - Documentation overhaul and hosting on readthedocs.
    - Added ``'x'`` open mode.
    - Added ``tell()`` method.
    - Added ``__repr__()`` method.

2015-04-xx V0.7.0 Bastian Bechtold:
    Again, thanks to Matthias Geier for all of his hard work, but also
    Nils Werner and Whistler7 for their many suggestions and help.

    - Renamed ``import pysoundfile`` to ``import soundfile``.
    - Installation through pip wheels that contain the necessary
      libraries for OS X and Windows.
    - Removed ``exclusive_creation`` argument to ``write``.
    - Added ``truncate()`` method.
