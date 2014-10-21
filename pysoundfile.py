"""PySoundFile is an audio library based on libsndfile, CFFI and Numpy

PySoundFile can read and write sound files. File reading/writing is
supported through libsndfile_, which is a free, cross-platform,
open-source library for reading and writing many different sampled
sound file formats that runs on many platforms including Windows, OS
X, and Unix. It is accessed through CFFI_, which is a foreign function
interface for Python calling C code. CFFI is supported for CPython
2.6+, 3.x and PyPy 2.0+. PySoundFile represents audio data as NumPy
arrays.

.. _libsndfile: http://www.mega-nerd.com/libsndfile/
.. _CFFI: http://cffi.readthedocs.org/

Sound files can be read or written directly using the functions
:func:`pysoundfile.read`, :func:`pysoundfile.write`, and
:func:`pysoundfile.blocks`.

Alternatively, every sound file can be opened as a SoundFile object
using either the :func:`pysoundfile.SoundFile` constructor, or the
:func:`pysoundfile.open` function. SoundFile objects can be created
for reading, writing, or both. Each SoundFile object has a samplerate,
a number of channels, and a file format. These can not be changed at
runtime.

A SoundFile object has methods for reading and writing data to/from
the file. Even though every sound file has a fixed file format,
reading and writing is possible in four different NumPy formats:
``int16``, ``int32``, ``float32`` and ``float64``. By default,
``float64`` is used.

At the same time, SoundFile objects act as sequence types, so you can
use slices to read or write data as well. Since there is no way of
specifying data formats for slices, the SoundFile will always return
float64 data for those.

Note that you need to have libsndfile installed in order to use
PySoundFile. The Windows installers come with libsndfile already.

PySoundFile is BSD licensed. (c) 2013, Bastian Bechtold

"""

__version__ = "0.5.0"

import numpy as _np
from cffi import FFI as _FFI
from os import SEEK_SET, SEEK_CUR, SEEK_END

try:
    import builtins as _builtins
except ImportError:
    import __builtin__ as _builtins  # for Python < 3.0

_ffi = _FFI()
_ffi.cdef("""
enum
{
    SF_FORMAT_SUBMASK       = 0x0000FFFF,
    SF_FORMAT_TYPEMASK      = 0x0FFF0000,
    SF_FORMAT_ENDMASK       = 0x30000000
} ;

enum
{
    SFC_GET_FORMAT_INFO             = 0x1028,

    SFC_GET_FORMAT_MAJOR_COUNT      = 0x1030,
    SFC_GET_FORMAT_MAJOR            = 0x1031,
    SFC_GET_FORMAT_SUBTYPE_COUNT    = 0x1032,
    SFC_GET_FORMAT_SUBTYPE          = 0x1033,
} ;

enum
{
    SF_FALSE    = 0,
    SF_TRUE     = 1,

    /* Modes for opening files. */
    SFM_READ    = 0x10,
    SFM_WRITE   = 0x20,
    SFM_RDWR    = 0x30,
} ;

typedef int64_t sf_count_t ;

typedef struct SNDFILE_tag SNDFILE ;

typedef struct SF_INFO
{
    sf_count_t frames ;        /* Used to be called samples.  Changed to avoid confusion. */
    int        samplerate ;
    int        channels ;
    int        format ;
    int        sections ;
    int        seekable ;
} SF_INFO ;

SNDFILE*    sf_open          (const char *path, int mode, SF_INFO *sfinfo) ;
int         sf_format_check  (const SF_INFO *info) ;

sf_count_t  sf_seek          (SNDFILE *sndfile, sf_count_t frames, int whence) ;

int         sf_command       (SNDFILE *sndfile, int cmd, void *data, int datasize) ;

int         sf_error         (SNDFILE *sndfile) ;
const char* sf_strerror      (SNDFILE *sndfile) ;
const char* sf_error_number  (int errnum) ;

int         sf_perror        (SNDFILE *sndfile) ;
int         sf_error_str     (SNDFILE *sndfile, char* str, size_t len) ;

int         sf_close         (SNDFILE *sndfile) ;
void        sf_write_sync    (SNDFILE *sndfile) ;

sf_count_t  sf_read_short    (SNDFILE *sndfile, short *ptr, sf_count_t items) ;
sf_count_t  sf_read_int      (SNDFILE *sndfile, int *ptr, sf_count_t items) ;
sf_count_t  sf_read_float    (SNDFILE *sndfile, float *ptr, sf_count_t items) ;
sf_count_t  sf_read_double   (SNDFILE *sndfile, double *ptr, sf_count_t items) ;

sf_count_t  sf_readf_short   (SNDFILE *sndfile, short *ptr, sf_count_t frames) ;
sf_count_t  sf_readf_int     (SNDFILE *sndfile, int *ptr, sf_count_t frames) ;
sf_count_t  sf_readf_float   (SNDFILE *sndfile, float *ptr, sf_count_t frames) ;
sf_count_t  sf_readf_double  (SNDFILE *sndfile, double *ptr, sf_count_t frames) ;

sf_count_t  sf_write_short   (SNDFILE *sndfile, short *ptr, sf_count_t items) ;
sf_count_t  sf_write_int     (SNDFILE *sndfile, int *ptr, sf_count_t items) ;
sf_count_t  sf_write_float   (SNDFILE *sndfile, float *ptr, sf_count_t items) ;
sf_count_t  sf_write_double  (SNDFILE *sndfile, double *ptr, sf_count_t items) ;

sf_count_t  sf_writef_short  (SNDFILE *sndfile, short *ptr, sf_count_t frames) ;
sf_count_t  sf_writef_int    (SNDFILE *sndfile, int *ptr, sf_count_t frames) ;
sf_count_t  sf_writef_float  (SNDFILE *sndfile, float *ptr, sf_count_t frames) ;
sf_count_t  sf_writef_double (SNDFILE *sndfile, double *ptr, sf_count_t frames) ;

sf_count_t  sf_read_raw      (SNDFILE *sndfile, void *ptr, sf_count_t bytes) ;
sf_count_t  sf_write_raw     (SNDFILE *sndfile, void *ptr, sf_count_t bytes) ;

const char* sf_get_string    (SNDFILE *sndfile, int str_type) ;
int         sf_set_string    (SNDFILE *sndfile, int str_type, const char* str) ;

typedef sf_count_t  (*sf_vio_get_filelen) (void *user_data) ;
typedef sf_count_t  (*sf_vio_seek)        (sf_count_t offset, int whence, void *user_data) ;
typedef sf_count_t  (*sf_vio_read)        (void *ptr, sf_count_t count, void *user_data) ;
typedef sf_count_t  (*sf_vio_write)       (const void *ptr, sf_count_t count, void *user_data) ;
typedef sf_count_t  (*sf_vio_tell)        (void *user_data) ;

typedef struct SF_VIRTUAL_IO
{    sf_count_t  (*get_filelen) (void *user_data) ;
     sf_count_t  (*seek)        (sf_count_t offset, int whence, void *user_data) ;
     sf_count_t  (*read)        (void *ptr, sf_count_t count, void *user_data) ;
     sf_count_t  (*write)       (const void *ptr, sf_count_t count, void *user_data) ;
     sf_count_t  (*tell)        (void *user_data) ;
} SF_VIRTUAL_IO ;

SNDFILE*    sf_open_virtual   (SF_VIRTUAL_IO *sfvirtual, int mode, SF_INFO *sfinfo, void *user_data) ;
SNDFILE*    sf_open_fd        (int fd, int mode, SF_INFO *sfinfo, int close_desc) ;

typedef struct SF_FORMAT_INFO
{
    int         format ;
    const char* name ;
    const char* extension ;
} SF_FORMAT_INFO ;
""")

_str_types = {
    'title':       0x01,
    'copyright':   0x02,
    'software':    0x03,
    'artist':      0x04,
    'comment':     0x05,
    'date':        0x06,
    'album':       0x07,
    'license':     0x08,
    'tracknumber': 0x09,
    'genre':       0x10,
}

_formats = {
    'WAV':   0x010000,  # Microsoft WAV format (little endian default).
    'AIFF':  0x020000,  # Apple/SGI AIFF format (big endian).
    'AU':    0x030000,  # Sun/NeXT AU format (big endian).
    'RAW':   0x040000,  # RAW PCM data.
    'PAF':   0x050000,  # Ensoniq PARIS file format.
    'SVX':   0x060000,  # Amiga IFF / SVX8 / SV16 format.
    'NIST':  0x070000,  # Sphere NIST format.
    'VOC':   0x080000,  # VOC files.
    'IRCAM': 0x0A0000,  # Berkeley/IRCAM/CARL
    'W64':   0x0B0000,  # Sonic Foundry's 64 bit RIFF/WAV
    'MAT4':  0x0C0000,  # Matlab (tm) V4.2 / GNU Octave 2.0
    'MAT5':  0x0D0000,  # Matlab (tm) V5.0 / GNU Octave 2.1
    'PVF':   0x0E0000,  # Portable Voice Format
    'XI':    0x0F0000,  # Fasttracker 2 Extended Instrument
    'HTK':   0x100000,  # HMM Tool Kit format
    'SDS':   0x110000,  # Midi Sample Dump Standard
    'AVR':   0x120000,  # Audio Visual Research
    'WAVEX': 0x130000,  # MS WAVE with WAVEFORMATEX
    'SD2':   0x160000,  # Sound Designer 2
    'FLAC':  0x170000,  # FLAC lossless file format
    'CAF':   0x180000,  # Core Audio File format
    'WVE':   0x190000,  # Psion WVE format
    'OGG':   0x200000,  # Xiph OGG container
    'MPC2K': 0x210000,  # Akai MPC 2000 sampler
    'RF64':  0x220000,  # RF64 WAV file
}

_subtypes = {
    'PCM_S8':    0x0001,  # Signed 8 bit data
    'PCM_16':    0x0002,  # Signed 16 bit data
    'PCM_24':    0x0003,  # Signed 24 bit data
    'PCM_32':    0x0004,  # Signed 32 bit data
    'PCM_U8':    0x0005,  # Unsigned 8 bit data (WAV and RAW only)
    'FLOAT':     0x0006,  # 32 bit float data
    'DOUBLE':    0x0007,  # 64 bit float data
    'ULAW':      0x0010,  # U-Law encoded.
    'ALAW':      0x0011,  # A-Law encoded.
    'IMA_ADPCM': 0x0012,  # IMA ADPCM.
    'MS_ADPCM':  0x0013,  # Microsoft ADPCM.
    'GSM610':    0x0020,  # GSM 6.10 encoding.
    'VOX_ADPCM': 0x0021,  # OKI / Dialogix ADPCM
    'G721_32':   0x0030,  # 32kbs G721 ADPCM encoding.
    'G723_24':   0x0031,  # 24kbs G723 ADPCM encoding.
    'G723_40':   0x0032,  # 40kbs G723 ADPCM encoding.
    'DWVW_12':   0x0040,  # 12 bit Delta Width Variable Word encoding.
    'DWVW_16':   0x0041,  # 16 bit Delta Width Variable Word encoding.
    'DWVW_24':   0x0042,  # 24 bit Delta Width Variable Word encoding.
    'DWVW_N':    0x0043,  # N bit Delta Width Variable Word encoding.
    'DPCM_8':    0x0050,  # 8 bit differential PCM (XI only)
    'DPCM_16':   0x0051,  # 16 bit differential PCM (XI only)
    'VORBIS':    0x0060,  # Xiph Vorbis encoding.
}

_endians = {
    'FILE':   0x00000000,  # Default file endian-ness.
    'LITTLE': 0x10000000,  # Force little endian-ness.
    'BIG':    0x20000000,  # Force big endian-ness.
    'CPU':    0x30000000,  # Force CPU endian-ness.
}

# libsndfile doesn't specify default subtypes, these are somehow arbitrary:
_default_subtypes = {
    'WAV':   'PCM_16',
    'AIFF':  'PCM_16',
    'AU':    'PCM_16',
    # 'RAW':  # subtype must be explicit!
    'PAF':   'PCM_16',
    'SVX':   'PCM_16',
    'NIST':  'PCM_16',
    'VOC':   'PCM_16',
    'IRCAM': 'PCM_16',
    'W64':   'PCM_16',
    'MAT4':  'DOUBLE',
    'MAT5':  'DOUBLE',
    'PVF':   'PCM_16',
    'XI':    'DPCM_16',
    'HTK':   'PCM_16',
    'SDS':   'PCM_16',
    'AVR':   'PCM_16',
    'WAVEX': 'PCM_16',
    'SD2':   'PCM_16',
    'FLAC':  'PCM_16',
    'CAF':   'PCM_16',
    'WVE':   'ALAW',
    'OGG':   'VORBIS',
    'MPC2K': 'PCM_16',
    'RF64':  'PCM_16',
}

_ffi_types = {
    _np.dtype('float64'): 'double',
    _np.dtype('float32'): 'float',
    _np.dtype('int32'): 'int',
    _np.dtype('int16'): 'short'
}

_snd = _ffi.dlopen('sndfile')


class SoundFile(object):

    """SoundFile handles reading and writing to sound files.

    Each SoundFile opens one sound file on the disk. This sound file
    has a specific samplerate, data format and a number of channels.
    Each sound file can be opened for reading, for writing or both.
    Note that the latter is unsupported by libsndfile for some
    formats.

    Data can be written to the file using
    :func:`pysoundfile.SoundFile.write`, or read from the file using
    :func:`pysoundfile.SoundFile.read`. Every read or write operation
    starts at a certain position in the file called the read/write
    pointer. Reading or writing a number of frames will advance the
    read/write pointer by the same number of frames. Alternatively,
    :func:`pysoundfile.SoundFile.seek` can be used to set the
    read/write pointer.

    All data access uses frames as index. A frame is one discrete
    time-step in the sound file. Every frame contains as many samples
    as there are channels in the file.

    SoundFile also supports indexing to access data at arbitrary
    positions in the file. Note that indexing always reads all
    channels of a given frame range, even if only single channels are
    accessed.

    In addition to audio data, there are a number of text fields in
    every sound file. In particular, you can set a title, a copyright
    notice, a software description, the artist name, a comment, a
    date, the album name, a license, a tracknumber and a genre. Not
    all of these fields are supported for every file format, though.

    """

    def __init__(self, file, mode='r', samplerate=None, channels=None,
                 subtype=None, endian=None, format=None, closefd=True):
        """Open a sound file.

        If a file is opened with mode ``'r'`` (the default) or
        ``'r+'``, no samplerate, channels or file format need to be
        given. If a file is opened with another mode, you must provide
        a samplerate, a number of channels, and a file format. An
        exception is the RAW data format, which requires these data
        points for reading as well as writing.

        File formats consist of three case-insensitive strings:

        * a *major format* which is by default obtained from the
          extension of the file name (if known) and which can be
          forced with the format argument (e.g. ``format='WAVEX'``).
        * a *subtype*, e.g. ``'PCM_24'``. Most major formats have a
          default subtype which is used if no subtype is specified.
        * an *endian-ness*, which doesn't have to be specified at all in
          most cases.

        The functions :func:`pysoundfile.available_formats` and
        :func:`pysoundfile.available_subtypes()` can be used to obtain
        a list of all avaliable major formats and subtypes,
        respectively.

        Parameters
        ----------
        file : A filename or a ``file`` object or file descriptor
            The file to open.
        mode : {'r', 'r+', 'w', 'w+', 'x', 'x+'}, optional
            Open file mode. ``'r'`` for reading, ``'w'`` for writing
            (truncates), ``'x'`` for writing (but fail if already
            existing), and in every case, ``'+'`` for reading and
            writing.
        samplerate : int, sometimes optional
            The samplerate of the file. Not necessary in ``'r'`` and
            ``'r+'`` mode. Always necessary in ``'RAW'`` format.
        channels : int, sometimes optional
            The number of channels of the file. Not necessary in
            ``'r'`` and ``'r+'`` mode. Always necessary in ``'RAW'``
            format.
        subtype : str, optional
            The subtype of the sound file. Not necessary in ``'r'``
            and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
            If not given, all formats except for ``'RAW'`` will use
            their default subtype. See
            :func:`pysoundfile.available_subtypes` for all possible
            values.
        endian : {'FILE', 'LITTLE', 'BIG', 'CPU'}, optional
            The endianness of the sound file. Not necessary in ``'r'``
            and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
            By default, this is set to ``'FILE'``, which is correct in
            most cases.
        format : str, optional
            The format of the sound file. Not necessary in ``'r'`` and
            ``'r+'`` mode. Always necessary in ``'RAW'`` format or
            when no file extension is given. If not given, this will
            be determined based on the file extension. See
            :func:`pysoundfile.available_formats` for all possible
            values.
        closefd : bool, optional
           Whether to close the file descriptor on destruction. Only
           applicable to file descriptors.

        Examples
        --------
        Create a new sound file for reading and writing:

        >>> soundFile = sf.SoundFile('new_file.wav', 'x+', 44100, 2)

        Open an existing file for reading:

        >>> soundFile = sf.SoundFile('existing_file.wav')

        """
        if mode is None:
            mode = getattr(file, 'mode', None)
        if not isinstance(mode, str):
            raise TypeError("Invalid mode: %s" % repr(mode))
        modes = set(mode)
        if modes.difference('xrwb+') or len(mode) > len(modes):
            raise ValueError("Invalid mode: %s" % repr(mode))
        if len(modes.intersection('xrw')) != 1:
            raise ValueError("mode must contain exactly one of 'xrw'")
        self._mode = mode

        if '+' in mode:
            mode_int = _snd.SFM_RDWR
        elif 'r' in mode:
            mode_int = _snd.SFM_READ
        else:
            mode_int = _snd.SFM_WRITE

        old_fmt = format
        self._name = getattr(file, 'name', file)
        if format is None:
            format = str(self.name).rsplit('.', 1)[-1].upper()
            if format not in _formats and 'r' not in mode:
                raise TypeError(
                    "No format specified and unable to get format from "
                    "file extension: %s" % repr(self.name))

        self._info = _ffi.new("SF_INFO*")
        if 'r' not in mode or str(format).upper() == 'RAW':
            if samplerate is None:
                raise TypeError("samplerate must be specified")
            self._info.samplerate = samplerate
            if channels is None:
                raise TypeError("channels must be specified")
            self._info.channels = channels
            self._info.format = _format_int(format, subtype, endian)
        else:
            if any(arg is not None for arg in (samplerate, channels, old_fmt,
                                               subtype, endian)):
                raise TypeError(
                    "Not allowed for existing files (except 'RAW'): "
                    "samplerate, channels, format, subtype, endian")

        if not closefd and not isinstance(file, int):
            raise ValueError("closefd=False only allowed for file descriptors")

        if isinstance(file, str):
            if 'b' not in mode:
                mode += 'b'
            file = self._filestream = _builtins.open(file, mode, buffering=0)

        if isinstance(file, int):
            self._file = _snd.sf_open_fd(file, mode_int, self._info, closefd)
        elif all(hasattr(file, a) for a in ('seek', 'read', 'write', 'tell')):
            self._file = _snd.sf_open_virtual(
                self._init_virtual_io(file), mode_int, self._info, _ffi.NULL)
        else:
            raise TypeError("Invalid file: %s" % repr(file))
        self._handle_error()

        if modes.issuperset('r+') and self.seekable():
            # Move write pointer to 0 (like in Python file objects)
            self.seek(0)

    name = property(lambda self: self._name)
    """The file name of the sound file."""
    mode = property(lambda self: self._mode)
    """The open mode the sound file was opened with."""
    frames = property(lambda self: self._info.frames)
    """The number of frames in the sound file."""
    samplerate = property(lambda self: self._info.samplerate)
    """The sample rate of the sound file."""
    channels = property(lambda self: self._info.channels)
    """The number of channels in the sound file."""
    format = property(
        lambda self: _format_str(self._info.format & _snd.SF_FORMAT_TYPEMASK))
    """The major format of the sound file."""
    subtype = property(
        lambda self: _format_str(self._info.format & _snd.SF_FORMAT_SUBMASK))
    """The subtype of data in the the sound file."""
    endian = property(
        lambda self: _format_str(self._info.format & _snd.SF_FORMAT_ENDMASK))
    """The endian-ness of the data in the sound file."""
    format_info = property(
        lambda self: _format_info(self._info.format &
                                  _snd.SF_FORMAT_TYPEMASK)[1])
    """A description of the major format of the sound file."""
    subtype_info = property(
        lambda self: _format_info(self._info.format &
                                  _snd.SF_FORMAT_SUBMASK)[1])
    """A description of the subtype of the sound file."""
    sections = property(lambda self: self._info.sections)
    """The number of sections of the sound file."""
    closed = property(lambda self: self._file is None)
    """Whether the sound file is closed or not."""

    # avoid confusion if something goes wrong before assigning self._file:
    _file = None
    _filestream = None

    def seekable(self):
        """Return True if the file supports seeking.

        Examples
        --------
        >>> soundFile = sf.open('stereo_file.wav')
        >>> soundFile.seekable()
        True

        >>> soundFile = sf.open('new_file.flac', 'w', 44100, 1)
        >>> soundFile.seekable()
        False

        """
        return self._info.seekable == _snd.SF_TRUE

    def _init_virtual_io(self, file):
        @_ffi.callback("sf_vio_get_filelen")
        def vio_get_filelen(user_data):
            # first try __len__(), if not available fall back to seek()/tell()
            try:
                size = len(file)
            except TypeError:
                curr = file.tell()
                file.seek(0, SEEK_END)
                size = file.tell()
                file.seek(curr, SEEK_SET)
            return size

        @_ffi.callback("sf_vio_seek")
        def vio_seek(offset, whence, user_data):
            file.seek(offset, whence)
            return file.tell()

        @_ffi.callback("sf_vio_read")
        def vio_read(ptr, count, user_data):
            # first try readinto(), if not available fall back to read()
            try:
                buf = _ffi.buffer(ptr, count)
                data_read = file.readinto(buf)
            except AttributeError:
                data = file.read(count)
                data_read = len(data)
                buf = _ffi.buffer(ptr, data_read)
                buf[0:data_read] = data
            return data_read

        @_ffi.callback("sf_vio_write")
        def vio_write(ptr, count, user_data):
            buf = _ffi.buffer(ptr, count)
            data = buf[:]
            written = file.write(data)
            # write() returns None for file objects in Python <= 2.7:
            if written is None:
                written = count
            return written

        @_ffi.callback("sf_vio_tell")
        def vio_tell(user_data):
            return file.tell()

        # Note: the callback functions must be kept alive!
        self._virtual_io = {'get_filelen': vio_get_filelen,
                            'seek': vio_seek,
                            'read': vio_read,
                            'write': vio_write,
                            'tell': vio_tell}

        return _ffi.new("SF_VIRTUAL_IO*", self._virtual_io)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _handle_error(self):
        # this checks the error flag of the SNDFILE* structure
        self._check_if_closed()
        err = _snd.sf_error(self._file)
        self._handle_error_number(err)

    def _handle_error_number(self, err):
        # pretty-print a numerical error code
        if err != 0:
            err_str = _snd.sf_error_number(err)
            raise RuntimeError(_ffi.string(err_str).decode())

    def _getAttributeNames(self):
        # return all possible attributes used in __setattr__ and __getattr__.
        # This is useful for auto-completion (e.g. IPython)
        return _str_types

    def _check_if_closed(self):
        # check if the file is closed and raise an error if it is.
        # This should be used in every method that tries to access self._file.
        if self.closed:
            raise ValueError("I/O operation on closed file")

    def __setattr__(self, name, value):
        # access text data in the sound file through properties
        if name in _str_types:
            self._check_if_closed()
            data = _ffi.new('char[]', value.encode())
            err = _snd.sf_set_string(self._file, _str_types[name], data)
            self._handle_error_number(err)
        else:
            super(SoundFile, self).__setattr__(name, value)

    def __getattr__(self, name):
        # access text data in the sound file through properties
        if name in _str_types:
            self._check_if_closed()
            data = _snd.sf_get_string(self._file, _str_types[name])
            return _ffi.string(data).decode() if data else ""
        else:
            raise AttributeError("SoundFile has no attribute %s" % repr(name))

    def __len__(self):
        return self.frames

    def _get_slice_bounds(self, frame):
        # get start and stop index from slice, asserting step==1
        if not isinstance(frame, slice):
            frame = slice(frame, frame + 1)
        start, stop, step = frame.indices(len(self))
        if step != 1:
            raise RuntimeError("Step size must be 1")
        if start > stop:
            stop = start
        return start, stop

    def __getitem__(self, frame):
        # access the file as if it where a Numpy array. The data is
        # returned as numpy array.
        second_frame = None
        if isinstance(frame, tuple):
            if len(frame) > 2:
                raise AttributeError(
                    "SoundFile can only be accessed in one or two dimensions")
            frame, second_frame = frame
        start, stop = self._get_slice_bounds(frame)
        curr = self.seek(0, SEEK_CUR)
        self.seek(start, SEEK_SET)
        data = self.read(stop - start)
        self.seek(curr, SEEK_SET)
        if second_frame:
            return data[(slice(None), second_frame)]
        else:
            return data

    def __setitem__(self, frame, data):
        # access the file as if it where a one-dimensional Numpy
        # array. Data must be in the form (frames x channels).
        # Both open slice bounds and negative values are allowed.
        start, stop = self._get_slice_bounds(frame)
        if stop - start != len(data):
            raise IndexError(
                "Could not fit data of length %i into slice of length %i" %
                (len(data), stop - start))
        curr = self.seek(0, SEEK_CUR)
        self.seek(start, SEEK_SET)
        self.write(data)
        self.seek(curr, SEEK_SET)
        return data

    def flush(self):
        """Write unwritten data to disk.

        Examples
        --------
        Create a new file:

        >>> soundFile = sf.open('new_file.wav', 'w', 44100, 2)
        >>> soundFile.write(np.random.randn(10, 2))
        >>> soundFile.flush()

        It is now guaranteed safe to read the new file from another
        program:

        >>> sf.read('stereo_file.wav')

        """
        self._check_if_closed()
        _snd.sf_write_sync(self._file)

    def close(self):
        """Close the file. Can be called multiple times.

        Examples
        --------
        >>> soundFile = sf.open('stereo_file.wav')
        >>> soundFile.close()
        >>> soundFile.read()  # this will fail!

        """
        if not self.closed:
            # be sure to flush data to disk before closing the file
            self.flush()
            err = _snd.sf_close(self._file)
            self._file = None
            if self._filestream:
                self._filestream.close()
            self._handle_error_number(err)

    def seek(self, frames, whence=SEEK_SET):
        """Set the read/write pointer.

        By default (``whence=SEEK_SET``), ``frames`` are counted from
        the beginning of the file. ``SEEK_CUR`` seeks from the current
        position (positive and negative values are allowed).
        ``SEEK_END`` seeks from the end (use negative values).

        Parameters
        ----------
        frames : int
            The frame index or offset to seek.
        whence : {SEEK_SET, SEEK_CUR, SEEK_END}, optional
            Whether to seek from the beginning of the file, the
            current read/write pointer, or the end of the file.

        Returns
        -------
        int
            The new absolute read/write position in frames, or a
            negative value on error.

        Examples
        --------
        >>> soundFile = sf.open('stereo_file.wav')

        Seek to the beginning of the file:

        >>> soundFile.seek(0)
        0

        Seek to the end of the file:

        >>> soundFile.seek(0, sf.SEEK_END)
        44100  # this is the file length

        """
        self._check_if_closed()
        position = _snd.sf_seek(self._file, frames, whence)
        self._handle_error()
        return position

    def _check_array(self, array):
        # Do some error checking
        if (array.ndim not in (1, 2) or
                array.ndim == 1 and self.channels != 1 or
                array.ndim == 2 and array.shape[1] != self.channels):
            raise ValueError("Invalid shape: %s" % repr(array.shape))

        if array.dtype not in _ffi_types:
            raise ValueError("dtype must be one of %s" %
                             repr([dt.name for dt in _ffi_types]))

    def _create_empty_array(self, frames, always_2d, dtype):
        # Create an empty array with appropriate shape
        if always_2d or self.channels > 1:
            shape = frames, self.channels
        else:
            shape = frames,
        return _np.empty(shape, dtype, order='C')

    def _read_or_write(self, funcname, array, frames):
        # Call into libsndfile
        self._check_if_closed()

        ffi_type = _ffi_types[array.dtype]
        assert array.flags.c_contiguous
        assert array.dtype.itemsize == _ffi.sizeof(ffi_type)
        assert array.size >= frames * self.channels

        if self.seekable():
            curr = self.seek(0, SEEK_CUR)
        func = getattr(_snd, funcname + ffi_type)
        ptr = _ffi.cast(ffi_type + '*', array.ctypes.data)
        frames = func(self._file, ptr, frames)
        self._handle_error()
        if self.seekable():
            self.seek(curr + frames, SEEK_SET)  # Update read & write position
        return frames

    def _check_frames(self, frames, fill_value):
        # Check if frames is larger than the remaining frames in the file
        if self.seekable():
            remaining_frames = self.frames - self.seek(0, SEEK_CUR)
            if frames < 0 or (frames > remaining_frames
                              and fill_value is None):
                frames = remaining_frames
        elif frames < 0:
            raise ValueError("frames must be specified for non-seekable files")
        return frames

    def read(self, frames=-1, dtype='float64', always_2d=True,
             fill_value=None, out=None):
        """Read from the file.

        Reads the given number of ``frames`` in the given data format
        from the current read/write position. This advances the
        read/write position by the same number of frames. Use
        ``frames=-1`` to read until the end of the file.

        A two-dimensional NumPy array is returned, where the channels
        are stored along the first dimension, i.e. as columns. A
        two-dimensional array is returned even if the sound file has
        only one channel. Use ``always_2d=False`` to return a
        one-dimensional array in this case.

        If ``out`` is specified, the data is written into the given
        NumPy array. In this case, the arguments ``dtype`` and
        ``always_2d`` are silently ignored!

        If there is less data left in the file than requested, the
        rest of the frames are filled with ``fill_value``. If
        ``fill_value=None``, a smaller array is returned. If ``out``
        is given, only a part of it is overwritten and a view
        containing all valid frames is returned.

        Parameters
        ----------
        frames : int, optional
            The number of frames to read. If ``-1``, the whole rest of
            the file is read.
        dtype : {'float64', 'float32', 'int32', 'int16'}, optional
            The data type to read. Floating point data is always in
            the range -1..1, and integer data is always in the range
            ``INT16_MIN``..``INT16_MAX`` or
            ``INT32_MIN``..``INT32_MAX``.
        always_2d : bool, optional
            Whether to always return a 2D array. If ``False``, single
            channel reads will return 1D arrays.
        fill_value : float, optional
            If given and more frames were requested than available in
            the file, the rest of the output will be filled with
            ``fill_value``.
        out : ndarray, optional
            If given, the data will be read into this ``ndarray``
            instead of creating a new ``ndarray``.

        Returns
        -------
        numpy.ndarray
            The read data; either a new array or ``out``. If more
            frames were requested than available in the file and
            ``out`` was given, this will be a view into ``out``.

        Examples
        --------
        >>> soundFile = sf.open('stereo_file.wav')

        Reading 3 frames from a stereo file:

        >>> soundFile.read(3)
        array([[ 0.71329652,  1.06294799],
               [-1.26450912, -0.38874483],
               [ 0.67398441, -1.11516333]])  # random

        """
        if out is None:
            frames = self._check_frames(frames, fill_value)
            out = self._create_empty_array(frames, always_2d, dtype)
        else:
            if frames < 0 or frames > len(out):
                frames = len(out)
            if not out.flags.c_contiguous:
                raise ValueError("out must be C-contiguous")

        self._check_array(out)
        frames = self._read_or_write('sf_readf_', out, frames)

        if len(out) > frames:
            if fill_value is None:
                out = out[:frames]
            else:
                out[frames:] = fill_value

        return out

    def write(self, data):
        """Write a number of frames to the file.

        Writes a number of frames at the read/write position to the
        file. This also advances the read/write position by the same
        number of frames and enlarges the file if necessary.

        Parameters
        ----------
        data : ndarray
            The data to write. Must be ``float64``, ``float32``,
            ``int32``, or ``int16``. Regardless of data type, the data
            will be written in the sound file's native file format.
            Must be (channels x frames) or a 1D-array for mono files.

        Examples
        --------
        >>> soundFile = sf.open('stereo_file.wav')

        Write 10 frames of random data to the file:

        >>> soundFile.write(np.random.randn(10, 2))

        """
        # no copy is made if data has already the correct memory layout:
        data = _np.ascontiguousarray(data)

        self._check_array(data)
        written = self._read_or_write('sf_writef_', data, len(data))
        assert written == len(data)

        if self.seekable():
            curr = self.seek(0, SEEK_CUR)
            self._info.frames = self.seek(0, SEEK_END)
            self.seek(curr, SEEK_SET)
        else:
            self._info.frames += written

    def blocks(self, blocksize=None, overlap=0, frames=-1, dtype='float64',
               always_2d=True, fill_value=None, out=None):
        """Return a generator for block-wise processing.

        By default, the generator returns blocks of the given
        ``blocksize`` until the end of the file is reached, ``frames``
        can be used to stop earlier.

        ``overlap`` can be used to rewind a certain number of frames
        between blocks.

        If ``fill_value`` is not specified, the last block may be
        smaller than ``blocksize``.

        Parameters
        ----------
        blocksize : int
            The number of frames to read per block. Either this or
            ``out`` must be given.
        overlap : int
            The number of frames to rewind between each block.
        frames : int
            The maximum number of frames to read. This can be used
            with the read/write pointer to read only part of a file.
        dtype : {'float64', 'float32', 'int32', 'int16'}, optional
            The data type to read. Floating point data is always in
            the range -1..1, and integer data is always in the range
            ``INT16_MIN``..``INT16_MAX`` or
            ``INT32_MIN``..``INT32_MAX``.
        always_2d : bool, optional
            Whether to always return a 2D array. If ``False``, single
            channel reads will return 1D arrays.
        fill_value : float, optional
            If given and more frames were requested than available in
            the file, the rest of the output will be filled with
            ``fill_value``.
        out : ndarray, optional
            If given, the data will be read into this ``ndarray``
            instead of creating a new ``ndarray``.

        Returns
        -------
        generator
            A generator that returns blocks of data; each block is
            either a new ndarray or ``out``. If ``out`` was given, and
            the remaining frames are not cleanly divisible by
            ``blocksize``, the last block will be a view into ``out``.

        Examples
        --------
        >>> soundFile = sf.open('stereo_file.wav')

        Read the whole file block by block of 1024 frames each:

        >>> for block in soundFile.blocks(1024):
        >>>     pass  # do something with `block`

        """
        if 'r' not in self.mode and '+' not in self.mode:
            raise RuntimeError("blocks() is not allowed in write-only mode")

        if overlap != 0 and not self.seekable():
            raise ValueError("overlap is only allowed for seekable files")

        if out is None:
            if blocksize is None:
                raise TypeError("One of {blocksize, out} must be specified")
        else:
            if blocksize is not None:
                raise TypeError(
                    "Only one of {blocksize, out} may be specified")
            blocksize = len(out)

        frames = self._check_frames(frames, fill_value)
        while frames > 0:
            if frames < blocksize:
                if fill_value is not None and out is None:
                    out = self._create_empty_array(blocksize, always_2d, dtype)
                blocksize = frames
            block = self.read(blocksize, dtype, always_2d, fill_value, out)
            frames -= blocksize
            if frames > 0 and self.seekable():
                self.seek(-overlap, SEEK_CUR)
                frames += overlap
            yield block

    def _prepare_read(self, start, stop, frames):
        # Seek to start frame and calculate length
        if start != 0 and not self.seekable():
            raise ValueError("start is only allowed for seekable files")
        if frames >= 0 and stop is not None:
            raise TypeError("Only one of {frames, stop} may be used")

        start, stop, _ = slice(start, stop).indices(self.frames)
        if stop < start:
            stop = start
        if frames < 0:
            frames = stop - start
        if self.seekable():
            self.seek(start, SEEK_SET)
        return frames


def open(file, mode='r', samplerate=None, channels=None,
         subtype=None, endian=None, format=None, closefd=True):
    return SoundFile(file, mode, samplerate, channels,
                     subtype, endian, format, closefd)

open.__doc__ = SoundFile.__init__.__doc__.replace('sf.SoundFile(', 'sf.open(')


def read(file, samplerate=None, channels=None, subtype=None, endian=None,
         format=None, closefd=True, start=0, stop=None, frames=-1,
         dtype='float64', always_2d=True, fill_value=None, out=None):
    """Read a sound file and return its contents as NumPy array.

    The number of frames to read can be specified with ``frames``, the
    position to start reading can be specified with ``start``. By
    default, the whole file is read from the beginning. Alternatively,
    a range can be specified with ``start`` and ``stop``. Both
    ``start`` and ``stop`` accept negative indices to specify
    positions relative to the end of the file.

    A two-dimensional NumPy array is returned, where the channels are
    stored along the first dimension, i.e. as columns. A
    two-dimensional array is returned even if the sound file has only
    one channel. Use ``always_2d=False`` to return a one-dimensional
    array in this case.

    If ``out`` is specified, the data is written into the given NumPy
    array. In this case, the arguments ``frames``, ``dtype`` and
    ``always_2d`` are silently ignored!

    If there is less data left in the file than requested, the rest of
    the frames are filled with ``fill_value``. If ``fill_value=None``,
    a smaller array is returned. If ``out`` is given, only a part of
    it is overwritten and a view containing all valid frames is
    returned.

    The keyword arguments ``samplerate``, ``channels``, ``format``,
    ``subtype`` and endian are only needed for ``'RAW'`` files. See
    :func:`pysoundfile.open` for details.

    Parameters
    ----------
    file : A filename or a ``file`` object or file descriptor
        The file to open.
    samplerate : int, sometimes optional
        The samplerate of the file. Not necessary in ``'r'`` and
        ``'r+'`` mode. Always necessary in ``'RAW'`` format.
    channels : int, sometimes optional
        The number of channels of the file. Not necessary in
        ``'r'`` and ``'r+'`` mode. Always necessary in ``'RAW'``
        format.
    subtype : str, optional
        The subtype of the sound file. Not necessary in ``'r'``
        and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
        If not given, all formats except for ``'RAW'`` will use
        their default subtype. See
        :func:`pysoundfile.available_subtypes` for all possible
        values.
    endian : {'FILE', 'LITTLE', 'BIG', 'CPU'}, optional
        The endianness of the sound file. Not necessary in ``'r'``
        and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
        By default, this is set to ``'FILE'``, which is correct in
        most cases.
    format : str, optional
        The format of the sound file. Not necessary in ``'r'`` and
        ``'r+'`` mode. Always necessary in ``'RAW'`` format or
        when no file extension is given. If not given, this will
        be determined based on the file extension. See
        :func:`pysoundfile.available_formats` for all possible
        values.
    closefd : bool, optional
        Whether to close the file descriptor on destruction. Only
        applicable to file descriptors.
    start : int, optional
        Where to start reading. Only two of ``start``, ``stop``, and
        ``frames`` can be given.
    stop : int, optional
        Where to stop reading. Only two of ``start``, ``stop``, and
        ``frames`` can be given. Ignored if ``None``.
    frames : int, optional
        The number of frames to read. If ``-1``, the whole rest of the
        file is read. Only two of ``start``, ``stop``, and ``frames``
        can be given.
    dtype : {'float64', 'float32', 'int32', 'int16'}, optional
        The data type to read. Floating point data is typically in
        the range -1..1, and integer data is always in the range
        ``-2**15``..``2**15-1`` for ``int16`` or
        ``-2**31``..``2**31-1`` for ``int32``.
    always_2d : bool, optional
        Whether to always return a 2D array. If ``False``, single
        channel reads will return 1D arrays.
    fill_value : float, optional
        If given and more frames were requested than available in
        the file, the rest of the output will be filled with
        ``fill_value``.
    out : ndarray, optional
        If given, the data will be read into this ``ndarray``
        instead of creating a new ``ndarray``.

    Returns
    -------
    ndarray
        The read data; either a new ndarray or ``out``. If more
        frames were requested than available in the file and
        ``out`` was given, this will be a view into ``out``.

    Examples
    --------
    Reading 3 frames from a stereo file:

    >>> sf.read('stereo_file.wav', 3)
    array([[ 0.71329652,  1.06294799],
           [-1.26450912, -0.38874483],
           [ 0.67398441, -1.11516333]])  # random

    """
    with SoundFile(file, 'r', samplerate, channels,
                   subtype, endian, format, closefd) as f:
        frames = f._prepare_read(start, stop, frames)
        data = f.read(frames, dtype, always_2d, fill_value, out)
    return data, f.samplerate


def write(data, file, samplerate,
          subtype=None, endian=None, format=None, closefd=True):
    """Write data from a NumPy array into a sound file.

    If ``file`` exists, it will be overwritten!

    If ``data`` is one-dimensional, a mono file is written. For
    two-dimensional ``data``, the columns are interpreted as channels.

    All further arguments are forwarded to :func:`pysoundfile.open`.

    Parameters
    ----------
    data : ndarray
        The data to write. Must be ``float64``, ``float32``,
        ``int32``, or ``int16``. Regardless of data type, the data
        will be written in the sound file's native file format.
        Must be (channels x frames) or a 1D-array for mono files.
    file : A filename or a ``file`` object or file descriptor
        The file to open.
    samplerate : int, sometimes optional
        The samplerate of the file. Not necessary in ``'r'`` and
        ``'r+'`` mode. Always necessary in ``'RAW'`` format.
    subtype : str, optional
        The subtype of the sound file. Not necessary in ``'r'``
        and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
        If not given, all formats except for ``'RAW'`` will use
        their default subtype. See
        :func:`pysoundfile.available_subtypes` for all possible
        values.
    endian : {'FILE', 'LITTLE', 'BIG', 'CPU'}, optional
        The endianness of the sound file. Not necessary in ``'r'``
        and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
        By default, this is set to ``'FILE'``, which is correct in
        most cases.
    format : str, optional
        The format of the sound file. Not necessary in ``'r'`` and
        ``'r+'`` mode. Always necessary in ``'RAW'`` format or
        when no file extension is given. If not given, this will
        be determined based on the file extension. See
        :func:`pysoundfile.available_formats` for all possible
        values.
    closefd : bool, optional
       Whether to close the file descriptor on destruction. Only
       applicable to file descriptors.

    Examples
    --------

    Write 10 frames of random data to a file:

    >>> sf.write(np.random.randn(10, 2), 'stereo_file.wav', 44100, 'PCM_24')

    """
    data = _np.asarray(data)
    if data.ndim == 1:
        channels = 1
    else:
        channels = data.shape[1]
    with open(file, 'w', samplerate, channels,
              subtype, endian, format, closefd) as f:
        f.write(data)


def blocks(file, samplerate=None, channels=None,
           subtype=None, endian=None, format=None, closefd=True,
           blocksize=None, overlap=0, start=0, stop=None, frames=-1,
           dtype='float64', always_2d=True, fill_value=None, out=None):
    """Return a generator for block-wise processing.

    All keyword arguments of :func:`pysoundfile.SoundFile.blocks` are
    allowed. All further arguments are forwarded to
    :func:`pysoundfile.open`.

    By default, iteration stops at the end of the file. Use ``frames``
    or ``stop`` to stop earlier.

    If you stop iterating over the generator before it's exhausted,
    the sound file is not closed. This is normally not a problem
    because the file is opened in read-only mode. To close the file
    properly, the generator's ``close()`` method can be called.

    Parameters
    ----------
    file : A filename or a ``file`` object or file descriptor
        The file to open.
    samplerate : int, sometimes optional
        The samplerate of the file. Not necessary in ``'r'`` and
        ``'r+'`` mode. Always necessary in ``'RAW'`` format.
    channels : int, sometimes optional
        The number of channels of the file. Not necessary in
        ``'r'`` and ``'r+'`` mode. Always necessary in ``'RAW'``
        format.
    subtype : str, optional
        The subtype of the sound file. Not necessary in ``'r'``
        and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
        If not given, all formats except for ``'RAW'`` will use
        their default subtype. See
        :func:`pysoundfile.available_subtypes` for all possible
        values.
    endian : {'FILE', 'LITTLE', 'BIG', 'CPU'}, optional
        The endianness of the sound file. Not necessary in ``'r'``
        and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
        By default, this is set to ``'FILE'``, which is correct in
        most cases.
    format : str, optional
        The format of the sound file. Not necessary in ``'r'`` and
        ``'r+'`` mode. Always necessary in ``'RAW'`` format or
        when no file extension is given. If not given, this will
        be determined based on the file extension. See
        :func:`pysoundfile.available_formats` for all possible
        values.
    closefd : bool, optional
        Whether to close the file descriptor on destruction. Only
        applicable to file descriptors.
    blocksize : int
        The number of frames to read per block. Either this or ``out``
        must be given.
    overlap : int, optional
        The number of frames to rewind between each block.
    start : int, optional
        Where to start reading. Only two of ``start``, ``stop``, and
        ``frames`` can be given.
    stop : int, optional
        Where to stop reading. Only two of ``start``, ``stop``, and
        ``frames`` can be given. Ignored if ``None``.
    frames : int, optional
        The number of frames to read. If ``-1``, the whole rest of the
        file is read. Only two of ``start``, ``stop``, and ``frames``
        can be given.
    dtype : {'float64', 'float32', 'int32', 'int16'}, optional
        The data type to read. Floating point data is always in
        the range -1..1, and integer data is always in the range
        ``INT16_MIN``..``INT16_MAX`` or
        ``INT32_MIN``..``INT32_MAX``.
    always_2d : bool, optional
        Whether to always return a 2D array. If ``False``, single
        channel reads will return 1D arrays.
    fill_value : float, optional
        If given and more frames were requested than available in
        the file, the rest of the output will be filled with
        ``fill_value``.
    out : ndarray, optional
        If given, the data will be read into this ``ndarray``
        instead of creating a new ``ndarray``.

    Returns
    -------
    generator
        A generator that returns blocks of data; each block is
        either a new ndarray or ``out``. If ``out`` was given, and
        the remaining frames are not cleanly divisible by
        ``blocksize``, the last block will be a view into ``out``.

    Examples
    --------

    Read the whole file block by block of 1024 frames each:

    >>> for block in sf.blocks('stereo_file.wav', blocksize=1024):
    >>>     pass  # do something with `block`
    """
    with open(file, 'r', samplerate, channels,
              subtype, endian, format, closefd) as f:
        frames = f._prepare_read(start, stop, frames)
        for block in f.blocks(blocksize, overlap, frames,
                              dtype, always_2d, fill_value, out):
            yield block


def default_subtype(format):
    """Return the default subtype for a given format.

    Parameters
    ----------
    format : str
        The name of a format.

    Returns
    -------
    str
        The name of a subtype appropriate for ``format``.

    Examples
    --------
    >>> sf.default_subtype('WAV')
    'PCM_16'

    >>> sf.default_subtype('MAT5')
    'DOUBLE'
    """
    return _default_subtypes.get(str(format).upper())


def _format_int(format, subtype, endian):
    # Return numeric format ID for given format|subtype|endian combo
    try:
        result = _formats[str(format).upper()]
    except KeyError:
        raise ValueError("Invalid format string: %s" % repr(format))
    if subtype is None:
        subtype = default_subtype(format)
        if subtype is None:
            raise TypeError(
                "No default subtype for major format %s" % repr(format))
    try:
        result |= _subtypes[str(subtype).upper()]
    except KeyError:
        raise ValueError("Invalid subtype string: %s" % repr(subtype))
    try:
        result |= _endians[str(endian).upper()
                           if endian is not None else 'FILE']
    except KeyError:
        raise ValueError("Invalid endian-ness: %s" % repr(endian))

    info = _ffi.new("SF_INFO*")
    info.format = result
    info.channels = 1
    if _snd.sf_format_check(info) == _snd.SF_FALSE:
        raise ValueError(
            "Invalid combination of format, subtype and endian")
    return result


def format_check(format, subtype=None, endian=None):
    """Check if the combination of format/subtype/endian is valid.

    Parameters
    ----------
    format : str, optional
        The format of the sound file. Not necessary in ``'r'`` and
        ``'r+'`` mode. Always necessary in ``'RAW'`` format or
        when no file extension is given. If not given, this will
        be determined based on the file extension. See
        :func:`pysoundfile.available_formats` for all possible
        values.
    subtype : str, optional
        The subtype of the sound file. Not necessary in ``'r'``
        and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
        If not given, all formats except for ``'RAW'`` will use
        their default subtype. See
        :func:`pysoundfile.available_subtypes` for all possible
        values.
    endian : {'FILE', 'LITTLE', 'BIG', 'CPU'}, optional
        The endianness of the sound file. Not necessary in ``'r'``
        and ``'r+'`` mode. Always necessary in ``'RAW'`` format.
        By default, this is set to ``'FILE'``, which is correct in
        most cases.

    Returns
    -------
    bool
        Whether this combination is valid or not.

    Examples
    --------
    >>> sf.format_check('WAV', 'INT_16')
    True

    >>> sf.format_check('FLAC', 'VORBIS')
    False

    """
    try:
        return bool(_format_int(format, subtype, endian))
    except (ValueError, TypeError):
        return False


def _format_str(format_int):
    # Return the string representation of a given numeric format
    for dictionary in _formats, _subtypes, _endians:
        for k, v in dictionary.items():
            if v == format_int:
                return k
    return hex(format_int)


def _format_info(format_int, format_flag=_snd.SFC_GET_FORMAT_INFO):
    # Return the ID and short description of a given format.
    format_info = _ffi.new("SF_FORMAT_INFO*")
    format_info.format = format_int
    _snd.sf_command(_ffi.NULL, format_flag, format_info,
                    _ffi.sizeof("SF_FORMAT_INFO"))
    name = format_info.name
    return (_format_str(format_info.format),
            _ffi.string(name).decode() if name else "")


def _available_formats_helper(count_flag, format_flag):
    # Generator function used in available_formats() and available_subtypes()
    count = _ffi.new("int*")
    _snd.sf_command(_ffi.NULL, count_flag, count, _ffi.sizeof("int"))
    for format_int in range(count[0]):
        yield _format_info(format_int, format_flag)


def available_formats():
    """Return a dictionary of available major formats.

    Returns
    -------
    dict
        A dictionary of all available major formats, with the internal
        short name as keys, and a longer description as values.

    Examples
    --------
    >>> sf.available_formats()
    {'FLAC': 'FLAC (FLAC Lossless Audio Codec)',
     'WAV': 'WAV (Microsoft)',
     'MAT5': 'MAT5 (GNU Octave 2.1 / Matlab 5.0)',
     ... }

    """
    return dict(_available_formats_helper(_snd.SFC_GET_FORMAT_MAJOR_COUNT,
                                          _snd.SFC_GET_FORMAT_MAJOR))


def available_subtypes(format=None):
    """Return a dictionary of available subtypes.

    Parameters
    ----------
    format : str
        If given, only compatible subtypes are returned.

    Returns
    -------
    dict
        A dictionary of all available or compatible subtypes, with the
        internal short names as keys, and a longer description as
        values.

    Examples
    --------
    >>> sf.available_subtypes('FLAC')
    {'PCM_24': 'Signed 24 bit PCM',
     'PCM_S8': 'Signed 8 bit PCM',
     'PCM_16': 'Signed 16 bit PCM'}

    """
    subtypes = _available_formats_helper(_snd.SFC_GET_FORMAT_SUBTYPE_COUNT,
                                         _snd.SFC_GET_FORMAT_SUBTYPE)
    return dict((subtype, name) for subtype, name in subtypes
                if format is None or format_check(format, subtype))
