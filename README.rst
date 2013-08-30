===========
PySoundFile
===========

PySoundFile is an audio library based on libsndfile, CFFI and Numpy

PySoundFile can read and write sound files. File reading/writing is
supported through libsndfile_, which is a free, cross-platform,
open-source library for reading and writing many different sampled
sound file formats that runs on many platforms including Windows, OS
X, and Unix. It is accessed through CFFI_, which is a foreight
function interface for Python calling C code. CFFI is supported for
CPython 2.6+, 3.x and PyPy 2.0+. PySoundFile represents audio data as
NumPy arrays.

.. _libsndfile: http://www.mega-nerd.com/libsndfile/
.. _CFFI: http://cffi.readthedocs.org/

| PySoundFile is BSD licensed.
| (c) 2013, Bastian Bechtold

Prerequisites
-------------

You need to have libsndfile installed in order to use PySoundFile. You
can download libsndfile from its website_. On Windows, you need to
rename the library to "sndfile.dll" and put it into a path reachable
by Python. One way to do that is to put sndfile.dll into the ``lib``
directory in your Python installation.

Usage
-----

Each SoundFile opens one sound file on the disk. This sound file has a
specific samplerate, data format and a set number of channels. Each
sound file can be opened in ``read_mode``, ``write_mode``, or
``read_write_mode``. Note that ``read_write_mode`` is unsupported for
some formats.

All data access uses frames as index. A frame is one discrete
time-step in the sound file. Every frame contains as many samples as
there are channels in the file.

Read/Write Functions
~~~~~~~~~~~~~~~~~~~~

Data can be written to the file using ``write()``, or read from the
file using ``read()``. Every read and write operation starts at a
certain position in the file. Reading N frames will change this
position by N frames as well. Alternatively, ``seek()``, and
``seek_absolute()``, can be used to set the current position to a
frame index offset from the current position, the start of the file,
or the end of the file, respectively.

Here is an example for a program that reads a wave file and copies it
into an ogg-vorbis file:

.. code:: python

    from pysoundfile import SoundFile

    wave = SoundFile('existing_file.wav')
    ogg  = SoundFIle('new_file.ogg', samplerate=wave.samplerate,
                     channels=wave.channels, file_format=ogg_file,
                     open_mode=write_mode)

    data = wave.read(1024)
    while len(data) > 0:
        ogg.write(data)
        data = wave.read(1024)

Sequence Interface
~~~~~~~~~~~~~~~~~~

Alternatively, slices can be used to access data at arbitrary
positions in the file. Note that slices currently only work on frame
indices, not channels.

Here is an example of reading in a whole wave file into a NumPy array:

.. code:: python

    from pysoundfile import SoundFile

    wave = SoundFile('existing_file.wav')[:]

Accessing Text Data
~~~~~~~~~~~~~~~~~~~

In addition to audio data, there are a number of text fields in every
sound file. In particular, you can set a title, a copyright notice, a
software description, the artist name, a comment, a date, the album
name, a license, a tracknumber and a genre. Note however, that not all
of these fields are supported for every file format.
