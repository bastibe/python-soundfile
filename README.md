PySoundFile
===========

PySoundFile is an audio library based on libsndfile, CFFI and Numpy

PySoundFile can read and write sound files. File reading/writing is
supported through [libsndfile][], which is a free, cross-platform,
open-source library for reading and writing many different sampled
sound file formats that runs on many platforms including Windows, OS
X, and Unix. It is accessed through [CFFI][], which is a foreight
function interface for Python calling C code. CFFI is supported for
CPython 2.6+, 3.x and PyPy 2.0+. PySoundFile represents audio data as
NumPy arrays.

[libsndfile]: http://www.mega-nerd.com/libsndfile/
[CFFI]: http://cffi.readthedocs.org/

PySoundFile is BSD licensed.  
(c) 2013, Bastian Bechtold

Installation
------------

On the Python side, you need to have CFFI and Numpy in order to use
PySoundCard. Additionally, You need the library PortAudio installed on
your computer. On Unix, use your package manager to install PortAudio.
Then just install PySoundCard using pip or `python setup.py install`.

If you are running Windows, I recommend using [WinPython][] or some
similar distribution. This should set you up with Numpy. However, you
also need CFFI and it's dependency, PyCParser. A good place to get
these are the [Unofficial Windows Binaries for Python][pybuilds].
Having installed those, you can download the Windows installers for
PySoundFile:

[PySoundFile-0.3.win-amd64-py2.7](https://github.com/bastibe/PySoundFile/raw/master/dist/PySoundFile-0.3.win-amd64-py2.7.exe)  
[PySoundFile-0.3.win-amd64-py3.3](https://github.com/bastibe/PySoundFile/raw/master/dist/PySoundFile-0.3.win-amd64-py3.3.exe)  
[PySoundFile-0.3.win32-py2.7](https://github.com/bastibe/PySoundFile/raw/master/dist/PySoundFile-0.3.win32-py2.7.exe)  
[PySoundFile-0.3.win32-py3.3](https://github.com/bastibe/PySoundFile/raw/master/dist/PySoundFile-0.3.win32-py3.3.exe)

[WinPython]: https://code.google.com/p/winpython/
[pybuilds]: http://www.lfd.uci.edu/~gohlke/pythonlibs/


Usage
-----

Each SoundFile can either open one sound file on the disk, or an
open file-like object (using `libsndfile`'s [virtual file interface][vio]).
This sound file has a specific samplerate, data format and a set
number of channels. Each sound file can be opened in `read_mode`,
`write_mode`, or `read_write_mode`. Note that `read_write_mode`
is unsupported for some formats.

All data access uses frames as index. A frame is one discrete
time-step in the sound file. Every frame contains as many samples as
there are channels in the file.

[vio]: http://www.mega-nerd.com/libsndfile/api.html#open_virtual

### Virtual IO

If you have an open file-like object, you can use something
similar to this to decode it:

```python
from io import BytesIO
from pysoundfile import SoundFile
fObj = BytesIO(open('filename.flac', 'rb').read())
flac = SoundFile(fObj, virtual_io=True)
```

Here is an example using an HTTP request:
```python
from io import BytesIO
from pysoundfile import SoundFile
import requests

fObj = BytesIO()
response = requests.get('http://www.example.com/my.flac', stream=True)
for data in response.iter_content(4096):
    if data:
        fObj.write(data)
fObj.seek(0)
flac = SoundFile(fObj, virtual_io=True)
```

### Read/Write Functions

Data can be written to the file using `write()`, or read from the
file using `read()`. Every read and write operation starts at a
certain position in the file. Reading N frames will change this
position by N frames as well. Alternatively, `seek()`, and
`seek_absolute()`, can be used to set the current position to a
frame index offset from the current position, the start of the file,
or the end of the file, respectively.

Here is an example for a program that reads a wave file and copies it
into an ogg-vorbis file:

```python

    from pysoundfile import SoundFile

    wave = SoundFile('existing_file.wav')
    ogg  = SoundFile('new_file.ogg', sample_rate=wave.samplerate,
                     channels=wave.channels, format=ogg_file,
                     mode=write_mode)

    data = wave.read(1024)
    while len(data) > 0:
        ogg.write(data)
        data = wave.read(1024)
```

### Sequence Interface

Alternatively, slices can be used to access data at arbitrary
positions in the file. Note that slices currently only work on frame
indices, not channels.

Here is an example of reading in a whole wave file into a NumPy array:

```python

    from pysoundfile import SoundFile

    wave = SoundFile('existing_file.wav')[:]
```

### Accessing Text Data

In addition to audio data, there are a number of text fields in every
sound file. In particular, you can set a title, a copyright notice, a
software description, the artist name, a comment, a date, the album
name, a license, a tracknumber and a genre. Note however, that not all
of these fields are supported for every file format.
