python-soundfile
================

|version| |python| |status| |license|

|contributors| |downloads|

The `soundfile <https://github.com/bastibe/python-soundfile>`__ module is an audio
library based on libsndfile, CFFI and NumPy. Full documentation is
available on https://python-soundfile.readthedocs.io/.

The ``soundfile`` module can read and write sound files. File reading/writing is
supported through `libsndfile <http://www.mega-nerd.com/libsndfile/>`__,
which is a free, cross-platform, open-source (LGPL) library for reading
and writing many different sampled sound file formats that runs on many
platforms including Windows, OS X, and Unix. It is accessed through
`CFFI <https://cffi.readthedocs.io/>`__, which is a foreign function
interface for Python calling C code. CFFI is supported for CPython 2.6+,
3.x and PyPy 2.0+. The ``soundfile`` module represents audio data as NumPy arrays.

| python-soundfile is BSD licensed (BSD 3-Clause License).
| (c) 2013, Bastian Bechtold


|open-issues| |closed-issues| |open-prs| |closed-prs|

.. |contributors| image:: https://img.shields.io/github/contributors/bastibe/python-soundfile.svg
.. |version| image:: https://img.shields.io/pypi/v/soundfile.svg
.. |python| image:: https://img.shields.io/pypi/pyversions/soundfile.svg
.. |license| image:: https://img.shields.io/github/license/bastibe/python-soundfile.svg
.. |downloads| image:: https://img.shields.io/pypi/dm/soundfile.svg
.. |open-issues| image:: https://img.shields.io/github/issues/bastibe/python-soundfile.svg
.. |closed-issues| image:: https://img.shields.io/github/issues-closed/bastibe/python-soundfile.svg
.. |open-prs| image:: https://img.shields.io/github/issues-pr/bastibe/python-soundfile.svg
.. |closed-prs| image:: https://img.shields.io/github/issues-pr-closed/bastibe/python-soundfile.svg
.. |status| image:: https://img.shields.io/pypi/status/soundfile.svg

Breaking Changes
----------------

The ``soundfile`` module has evolved rapidly during the last few releases. Most
notably, we changed the import name from ``import pysoundfile`` to
``import soundfile`` in 0.7. In 0.6, we cleaned up many small
inconsistencies, particularly in the the ordering and naming of
function arguments and the removal of the indexing interface.

In 0.8.0, we changed the default value of ``always_2d`` from ``True``
to ``False``. Also, the order of arguments of the ``write`` function
changed from ``write(data, file, ...)`` to ``write(file, data, ...)``.

In 0.9.0, we changed the ``ctype`` arguments of the ``buffer_*``
methods to ``dtype``, using the Numpy ``dtype`` notation. The old
``ctype`` arguments still work, but are now officially deprecated.

In 0.11.0 switched from cffi ABI mode to API mode
Installation
------------

The ``soundfile`` module depends on the Python packages CFFI and NumPy, and the
system library libsndfile.

In a modern Python, you can use ``pip install soundfile`` to download
and install the latest release of the ``soundfile`` module and its dependencies.
On Windows and OS X, this will also install the library libsndfile.
On Linux, you need to install libsndfile using your distribution's
package manager, for example ``sudo apt-get install libsndfile1``.

If you are running on an unusual platform or if you are using an older
version of Python, you might need to install NumPy and CFFI separately,
for example using the Anaconda_ package manager or the `Unofficial Windows
Binaries for Python Extension Packages <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_.

.. _Anaconda: https://www.continuum.io/downloads

Error Reporting
---------------

In case of API usage errors the ``soundfile`` module raises the usual `ValueError` or `TypeError`.

For other errors `SoundFileError` is raised (used to be `RuntimeError`).
Particularly, a `LibsndfileError` subclass of this exception is raised on
errors reported by the libsndfile library. In that case the exception object
provides the libsndfile internal error code in the `LibsndfileError.code` attribute and the raw
libsndfile error message in the `LibsndfileError.error_string` attribute.

Read/Write Functions
--------------------

Data can be written to the file using `soundfile.write()`, or read from
the file using `soundfile.read()`. The ``soundfile`` module can open all file formats
that `libsndfile supports
<http://www.mega-nerd.com/libsndfile/#Features>`__, for example WAV,
FLAC, OGG and MAT files (see `Known Issues <https://github.com/bastibe/python-soundfile#known-issues>`__ below about writing OGG files).

Here is an example for a program that reads a wave file and copies it
into an FLAC file:

.. code:: python

    import soundfile as sf

    data, samplerate = sf.read('existing_file.wav')
    sf.write('new_file.flac', data, samplerate)

Block Processing
----------------

Sound files can also be read in short, optionally overlapping blocks
with `soundfile.blocks()`.
For example, this calculates the signal level for each block of a long
file:

.. code:: python

   import numpy as np
   import soundfile as sf

   rms = [np.sqrt(np.mean(block**2)) for block in
          sf.blocks('myfile.wav', blocksize=1024, overlap=512)]

``SoundFile`` Objects
---------------------

Sound files can also be opened as `SoundFile` objects. Every
`SoundFile` has a specific sample rate, data format and a set number of
channels.

If a file is opened, it is kept open for as long as the `SoundFile`
object exists. The file closes when the object is garbage collected,
but you should use the `SoundFile.close()` method or the
context manager to close the file explicitly:

.. code:: python

   import soundfile as sf

   with sf.SoundFile('myfile.wav', 'r+') as f:
       while f.tell() < f.frames:
           pos = f.tell()
           data = f.read(1024)
           f.seek(pos)
           f.write(data*2)

All data access uses frames as index. A frame is one discrete time-step
in the sound file. Every frame contains as many samples as there are
channels in the file.

RAW Files
---------

`soundfile.read()` can usually auto-detect the file type of sound files. This
is not possible for RAW files, though:

.. code:: python

   import soundfile as sf

   data, samplerate = sf.read('myfile.raw', channels=1, samplerate=44100,
                              subtype='FLOAT')

Note that on x86, this defaults to ``endian='LITTLE'``. If you are
reading big endian data (mostly old PowerPC/6800-based files), you
have to set ``endian='BIG'`` accordingly.

You can write RAW files in a similar way, but be advised that in most
cases, a more expressive format is better and should be used instead.

Virtual IO
----------

If you have an open file-like object, `soundfile.read()` can open it just like
regular files:

.. code:: python

    import soundfile as sf
    with open('filename.flac', 'rb') as f:
        data, samplerate = sf.read(f)

Here is an example using an HTTP request:

.. code:: python

    import io
    import soundfile as sf
    from urllib.request import urlopen

    url = "http://tinyurl.com/shepard-risset"
    data, samplerate = sf.read(io.BytesIO(urlopen(url).read()))

Note that the above example only works with Python 3.x.
For Python 2.x support, replace the third line with:

.. code:: python

    from urllib2 import urlopen

Known Issues
------------

Writing to OGG files can result in empty files with certain versions of libsndfile. See `#130 <https://github.com/bastibe/python-soundfile/issues/130>`__ for news on this issue.

If using a Buildroot style system, Python has trouble locating ``libsndfile.so`` file, which causes python-soundfile to not be loaded. This is apparently a bug in `python <https://bugs.python.org/issue13508>`__. For the time being, in ``soundfile.py``, you can remove the call to ``_find_library`` and hardcode the location of the ``libsndfile.so`` in ``_ffi.dlopen``. See `#258 <https://github.com/bastibe/python-soundfile/issues/258>`__ for discussion on this issue.

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
    - Added global `read()`, `write()`, `blocks()` convenience
      functions.
    - Documentation overhaul and hosting on readthedocs.
    - Added ``'x'`` open mode.
    - Added `tell()` method.
    - Added ``__repr__()`` method.

2015-04-12 V0.7.0 Bastian Bechtold:
    Again, thanks to Matthias Geier for all of his hard work, but also
    Nils Werner and Whistler7 for their many suggestions and help.

    - Renamed ``import pysoundfile`` to ``import soundfile``.
    - Installation through pip wheels that contain the necessary
      libraries for OS X and Windows.
    - Removed ``exclusive_creation`` argument to `write()`.
    - Added `truncate()` method.

2015-10-20 V0.8.0 Bastian Bechtold:
    Again, Matthias Geier contributed a whole lot of hard work to this
    release.

    - Changed the default value of ``always_2d`` from ``True`` to
      ``False``.
    - Numpy is now optional, and only loaded for ``read`` and
      ``write``.
    - Added `SoundFile.buffer_read()` and
      `SoundFile.buffer_read_into()` and `SoundFile.buffer_write()`,
      which read/write raw data without involving Numpy.
    - Added `info()` function that returns metadata of a sound file.
    - Changed the argument order of the `write()` function from
      ``write(data, file, ...)`` to ``write(file, data, ...)``

    And many more minor bug fixes.

2017-02-02 V0.9.0 Bastian Bechtold:
    Thank you, Matthias Geier, Tomas Garcia, and Todd, for contributions
    for this release.

    - Adds support for ALAC files.
    - Adds new member ``__libsndfile_version__``
    - Adds number of frames to ``info`` class
    - Adds ``dtype`` argument to ``buffer_*`` methods
    - Deprecates ``ctype`` argument to ``buffer_*`` methods
    - Adds official support for Python 3.6

    And some minor bug fixes.

2017-11-12 V0.10.0 Bastian Bechtold:
    Thank you, Matthias Geier, Toni Barth, Jon Peirce, Till Hoffmann,
    and Tomas Garcia, for contributions to this release.

    - Should now work with cx_freeze.
    - Several documentation fixes in the README.
    - Removes deprecated ``ctype`` argument in favor of ``dtype`` in ``buffer_*()``.
    - Adds `SoundFile.frames` in favor of now-deprecated ``__len__()``.
    - Improves performance of `blocks()` and `SoundFile.blocks()`.
    - Improves import time by using CFFI's out of line mode.
    - Adds a build script for building distributions.
