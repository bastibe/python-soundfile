"""PySoundFile is an audio library based on libsndfile, CFFI and NumPy.

Sound files can be read or written directly using the functions
:func:`read` and :func:`write`.
To read a sound file in a block-wise fashion, use :func:`blocks`.
Alternatively, sound files can be opened as :class:`SoundFile` objects.

For further information, see http://pysoundfile.readthedocs.org/.

"""
__version__ = "0.5.0"

import numpy as _np
import os as _os
from cffi import FFI as _FFI
from os import SEEK_SET, SEEK_CUR, SEEK_END

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


def read(file, frames=-1, start=0, stop=None, dtype='float64', always_2d=True,
         fill_value=None, out=None, samplerate=None, channels=None,
         format=None, subtype=None, endian=None, closefd=True):
    """Provide audio data from a sound file as NumPy array.

    By default, the whole file is read from the beginning, but the
    position to start reading can be specified with `start` and the
    number of frames to read can be specified with `frames`.
    Alternatively, a range can be specified with `start` and `stop`.

    If there is less data left in the file than requested, the rest of
    the frames are filled with `fill_value`.
    If no `fill_value` is specified, a smaller array is returned.

    Parameters
    ----------
    file : str or int or file-like object
        The file to read from.  See :class:`SoundFile` for details.
    frames : int, optional
        The number of frames to read. If `frames` is negative, the whole
        rest of the file is read.  Not allowed if `stop` is given.
    start : int, optional
        Where to start reading.  A negative value counts from the end.
    stop : int, optional
        The index after the last frame to be read.  A negative value
        counts from the end.  Not allowed if `frames` is given.
    dtype : {'float64', 'float32', 'int32', 'int16'}, optional
        Data type of the returned array, by default ``'float64'``.
        Floating point audio data is typically in the range from
        ``-1.0`` to ``1.0``.  Integer data is in the range from
        ``-2**15`` to ``2**15-1`` for ``'int16'`` and from ``-2**31`` to
        ``2**31-1`` for ``'int32'``.

    Returns
    -------
    audiodata : numpy.ndarray or type(out)
        A two-dimensional NumPy array is returned, where the channels
        are stored along the first dimension, i.e. as columns.
        A two-dimensional array is returned even if the sound file has
        only one channel. Use ``always_2d=False`` to return a
        one-dimensional array in this case.

        If `out` was specified, it is returned.  If `out` has more
        frames than available in the file (or if `frames` is smaller
        than the length of `out`) and no `fill_value` is given, then
        only a part of `out` is overwritten and a view containing all
        valid frames is returned.
    samplerate : int
        The sample rate of the audio file.

    Other Parameters
    ----------------
    always_2d : bool, optional
        By default, audio data is always returned as a two-dimensional
        array, even if the audio file has only one channel.
        With ``always_2d=False``, reading a mono sound file will return
        a one-dimensional array.
    fill_value : float, optional
        If more frames are requested than available in the file, the
        rest of the output is be filled with `fill_value`.  If
        `fill_value` is not specified, a smaller array is returned.
    out : numpy.ndarray or subclass, optional
        If `out` is specified, the data is written into the given array
        instead of creating a new array.  In this case, the arguments
        `dtype` and `always_2d` are silently ignored!  If `frames` is
        not given, it is obtained from the length of `out`.
    samplerate, channels, format, subtype, endian, closefd
        See :class:`SoundFile`.

    Examples
    --------
    >>> import pysoundfile as sf
    >>> data, samplerate = sf.read('stereo_file.wav')
    >>> data
    array([[ 0.71329652,  0.06294799],
           [-0.26450912, -0.38874483],
           ...
           [ 0.67398441, -0.11516333]])
    >>> samplerate
    44100

    """
    with SoundFile(file, 'r', samplerate, channels,
                   subtype, endian, format, closefd) as f:
        frames = f._prepare_read(start, stop, frames)
        data = f.read(frames, dtype, always_2d, fill_value, out)
    return data, f.samplerate


def write(data, file, samplerate,
          subtype=None, endian=None, format=None, closefd=True):
    """Write data to a sound file.

    .. note:: If `file` exists, it will be truncated and overwritten!

    Parameters
    ----------
    data : array_like
        The data to write.  Usually two-dimensional (channels x frames),
        but one-dimensional `data` can be used for mono files.
        Only the data types ``'float64'``, ``'float32'``, ``'int32'``
        and ``'int16'`` are supported.

        .. note:: The data type of `data` does **not** select the data
                  type of the written file.
                  Audio data will be converted to the given `subtype`.

    file : str or int or file-like object
        The file to write to.  See :class:`SoundFile` for details.
    samplerate : int
        The sample rate of the audio data.
    subtype : str, optional
        See :func:`default_subtype` for the default value and
        :func:`available_subtypes` for all possible values.

    Other Parameters
    ----------------
    format, endian, closefd
        See :class:`SoundFile`.

    Examples
    --------

    Write 10 frames of random data to a file:

    >>> import numpy as np
    >>> import pysoundfile as sf
    >>> sf.write(np.random.randn(10, 2), 'stereo_file.wav', 44100, 'PCM_24')

    """
    data = _np.asarray(data)
    if data.ndim == 1:
        channels = 1
    else:
        channels = data.shape[1]
    with SoundFile(file, 'w', samplerate, channels,
                   subtype, endian, format, closefd) as f:
        f.write(data)


def blocks(file, blocksize=None, overlap=0, frames=-1, start=0, stop=None,
           dtype='float64', always_2d=True, fill_value=None, out=None,
           samplerate=None, channels=None,
           format=None, subtype=None, endian=None, closefd=True):
    """Return a generator for block-wise reading.

    By default, iteration starts at the beginning and stops at the end
    of the file.  Use `start` to start at a later position and `frames`
    or `stop` to stop earlier.

    If you stop iterating over the generator before it's exhausted,
    the sound file is not closed. This is normally not a problem
    because the file is opened in read-only mode. To close the file
    properly, the generator's ``close()`` method can be called.

    Parameters
    ----------
    file : str or int or file-like object
        The file to read from.  See :class:`SoundFile` for details.
    blocksize : int
        The number of frames to read per block.
        Either this or `out` must be given.
    overlap : int, optional
        The number of frames to rewind between each block.

    Yields
    ------
    numpy.ndarray or type(out)
        Blocks of audio data.
        If `out` was given, and the requested frames are not an integer
        multiple of the length of `out`, and no `fill_value` was given,
        the last block will be a smaller view into `out`.

    Other Parameters
    ----------------
    frames, start, stop
        See :func:`read`.
    dtype : {'float64', 'float32', 'int32', 'int16'}, optional
        See :func:`read`.
    always_2d, fill_value, out
        See :func:`read`.
    samplerate, channels, format, subtype, endian, closefd
        See :class:`SoundFile`.

    Examples
    --------
    >>> import pysoundfile as sf
    >>> for block in sf.blocks('stereo_file.wav', blocksize=1024):
    >>>     pass  # do something with 'block'

    """
    with SoundFile(file, 'r', samplerate, channels,
                   subtype, endian, format, closefd) as f:
        frames = f._prepare_read(start, stop, frames)
        for block in f.blocks(blocksize, overlap, frames,
                              dtype, always_2d, fill_value, out):
            yield block


def available_formats():
    """Return a dictionary of available major formats.

    Examples
    --------
    >>> import pysoundfile as sf
    >>> sf.available_formats()
    {'FLAC': 'FLAC (FLAC Lossless Audio Codec)',
     'OGG': 'OGG (OGG Container format)',
     'WAV': 'WAV (Microsoft)',
     'AIFF': 'AIFF (Apple/SGI)',
     ...
     'WAVEX': 'WAVEX (Microsoft)',
     'RAW': 'RAW (header-less)',
     'MAT5': 'MAT5 (GNU Octave 2.1 / Matlab 5.0)'}

    """
    return dict(_available_formats_helper(_snd.SFC_GET_FORMAT_MAJOR_COUNT,
                                          _snd.SFC_GET_FORMAT_MAJOR))


def available_subtypes(format=None):
    """Return a dictionary of available subtypes.

    Parameters
    ----------
    format : str
        If given, only compatible subtypes are returned.

    Examples
    --------
    >>> import pysoundfile as sf
    >>> sf.available_subtypes('FLAC')
    {'PCM_24': 'Signed 24 bit PCM',
     'PCM_16': 'Signed 16 bit PCM',
     'PCM_S8': 'Signed 8 bit PCM'}

    """
    subtypes = _available_formats_helper(_snd.SFC_GET_FORMAT_SUBTYPE_COUNT,
                                         _snd.SFC_GET_FORMAT_SUBTYPE)
    return dict((subtype, name) for subtype, name in subtypes
                if format is None or check_format(format, subtype))


def check_format(format, subtype=None, endian=None):
    """Check if the combination of format/subtype/endian is valid.

    Examples
    --------
    >>> import pysoundfile as sf
    >>> sf.check_format('WAV', 'PCM_24')
    True
    >>> sf.check_format('FLAC', 'VORBIS')
    False

    """
    try:
        return bool(_format_int(format, subtype, endian))
    except (ValueError, TypeError):
        return False


def default_subtype(format):
    """Return the default subtype for a given format.

    Examples
    --------
    >>> import pysoundfile as sf
    >>> sf.default_subtype('WAV')
    'PCM_16'
    >>> sf.default_subtype('MAT5')
    'DOUBLE'

    """
    return _default_subtypes.get(str(format).upper())


class SoundFile(object):

    """A sound file.

    For more documentation see the __init__() docstring (which is also
    used for the online documentation (http://pysoundfile.readthedocs.org/).

    """

    def __init__(self, file, mode='r', samplerate=None, channels=None,
                 subtype=None, endian=None, format=None, closefd=True):
        """Open a sound file.

        If a file is opened with `mode` ``'r'`` (the default) or
        ``'r+'``, no sample rate, channels or file format need to be
        given because the information is obtained from the file. An
        exception is the ``'RAW'`` data format, which always requires
        these data points.

        File formats consist of three case-insensitive strings:

        * a *major format* which is by default obtained from the
          extension of the file name (if known) and which can be
          forced with the format argument (e.g. ``format='WAVEX'``).
        * a *subtype*, e.g. ``'PCM_24'``. Most major formats have a
          default subtype which is used if no subtype is specified.
        * an *endian-ness*, which doesn't have to be specified at all in
          most cases.

        A :class:`SoundFile` object is a *context manager*, which means
        if used in a "with" statement, :meth:`.close` is automatically
        called when reaching the end of the code block inside the "with"
        statement.

        Parameters
        ----------
        file : str or int or file-like object
            The file to open.  This can be a file name, a file
            descriptor or a Python file object (or a similar object with
            the methods ``read()``/``readinto()``, ``write()``,
            ``seek()`` and ``tell()``).
        mode : {'r', 'r+', 'w', 'w+', 'x', 'x+'}, optional
            Open mode.  Has to begin with one of these three characters:
            ``'r'`` for reading, ``'w'`` for writing (truncates `file`)
            or ``'x'`` for writing (raises an error if `file` already
            exists).  Additionally, it may contain ``'+'`` to open
            `file` for both reading and writing.
            The character ``'b'`` for *binary mode* is implied because
            all sound files have to be opened in this mode.
            If `file` is a file descriptor or a file-like object,
            ``'w'`` doesn't truncate and ``'x'`` doesn't raise an error.
        samplerate : int
            The sample rate of the file.  If `mode` contains ``'r'``,
            this is obtained from the file (except for ``'RAW'`` files).
        channels : int
            The number of channels of the file.
            If `mode` contains ``'r'``, this is obtained from the file
            (except for ``'RAW'`` files).
        subtype : str, sometimes optional
            The subtype of the sound file.  If `mode` contains ``'r'``,
            this is obtained from the file (except for ``'RAW'``
            files), if not, the default value depends on the selected
            `format` (see :func:`default_subtype`).
            See :func:`available_subtypes` for all possible subtypes for
            a given `format`.
        endian : {'FILE', 'LITTLE', 'BIG', 'CPU'}, sometimes optional
            The endian-ness of the sound file.  If `mode` contains
            ``'r'``, this is obtained from the file (except for
            ``'RAW'`` files), if not, the default value is ``'FILE'``,
            which is correct in most cases.
        format : str, sometimes optional
            The major format of the sound file.  If `mode` contains
            ``'r'``, this is obtained from the file (except for
            ``'RAW'`` files), if not, the default value is determined
            from the file extension.  See :func:`available_formats` for
            all possible values.
        closefd : bool, optional
            Whether to close the file descriptor on :meth:`.close`. Only
            applicable if the `file` argument is a file descriptor.

        Examples
        --------
        >>> from pysoundfile import SoundFile

        Open an existing file for reading:

        >>> myfile = SoundFile('existing_file.wav')
        >>> # do something with myfile
        >>> myfile.close()

        Create a new sound file for reading and writing using a with
        statement:

        >>> with SoundFile('new_file.wav', 'x+', 44100, 2) as myfile:
        >>>     # do something with myfile
        >>>     # ...
        >>>     assert not myfile.closed
        >>>     # myfile.close() is called automatically at the end
        >>> assert myfile.closed

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

        if '+' in modes:
            mode_int = _snd.SFM_RDWR
        elif 'r' in modes:
            mode_int = _snd.SFM_READ
        else:
            mode_int = _snd.SFM_WRITE

        old_fmt = format
        self._name = getattr(file, 'name', file)
        if format is None:
            format = str(self.name).rsplit('.', 1)[-1].upper()
            if format not in _formats and 'r' not in modes:
                raise TypeError(
                    "No format specified and unable to get format from "
                    "file extension: %s" % repr(self.name))

        self._info = _ffi.new("SF_INFO*")
        if 'r' not in modes or str(format).upper() == 'RAW':
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
            if _os.path.isfile(file):
                if 'x' in modes:
                    raise OSError("File exists: %s" % repr(file))
                elif modes.issuperset('w+'):
                    # truncate the file, because SFM_RDWR doesn't:
                    _os.close(_os.open(file, _os.O_WRONLY | _os.O_TRUNC))
            self._file = _snd.sf_open(file.encode(), mode_int, self._info)
        elif isinstance(file, int):
            self._file = _snd.sf_open_fd(file, mode_int, self._info, closefd)
        elif all(hasattr(file, a) for a in ('seek', 'read', 'write', 'tell')):
            self._file = _snd.sf_open_virtual(
                self._init_virtual_io(file), mode_int, self._info, _ffi.NULL)
        else:
            raise TypeError("Invalid file: %s" % repr(file))
        self._handle_error()

        if modes.issuperset('r+') and self.seekable():
            # Move write position to 0 (like in Python file objects)
            self.seek(0)

    name = property(lambda self: self._name)
    """The file name of the sound file."""
    mode = property(lambda self: self._mode)
    """The open mode the sound file was opened with."""
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

    def __repr__(self):
        return ('SoundFile("{}", mode="{}", samplerate={}, channels={}, '
                'format="{}")').format(self.name, self.mode, self.samplerate,
                                     self.channels, self.format)

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __setattr__(self, name, value):
        """Write text meta-data in the sound file through properties."""
        if name in _str_types:
            self._check_if_closed()
            data = _ffi.new('char[]', value.encode())
            err = _snd.sf_set_string(self._file, _str_types[name], data)
            self._handle_error_number(err)
        else:
            super(SoundFile, self).__setattr__(name, value)

    def __getattr__(self, name):
        """Read text meta-data in the sound file through properties."""
        if name in _str_types:
            self._check_if_closed()
            data = _snd.sf_get_string(self._file, _str_types[name])
            return _ffi.string(data).decode() if data else ""
        else:
            raise AttributeError("SoundFile has no attribute %s" % repr(name))

    def __len__(self):
        return self._info.frames

    def __getitem__(self, frame):
        # access the file as if it where a Numpy array. The data is
        # returned as numpy array.
        from warnings import warn
        warn('indexing has been deprecated and will be removed in the future',
             Warning)
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
        from warnings import warn
        warn('indexing has been deprecated and will be removed in the future',
             Warning)
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

    def seekable(self):
        """Return True if the file supports seeking."""
        return self._info.seekable == _snd.SF_TRUE

    def seek(self, frames, whence=SEEK_SET):
        """Set the read/write position.

        Parameters
        ----------
        frames : int
            The frame index or offset to seek.
        whence : {SEEK_SET, SEEK_CUR, SEEK_END}, optional
            By default (``whence=SEEK_SET``), `frames` are counted from
            the beginning of the file.
            ``whence=SEEK_CUR`` seeks from the current position
            (positive and negative values are allowed for `frames`).
            ``whence=SEEK_END`` seeks from the end (use negative value
            for `frames`).

        Returns
        -------
        int
            The new absolute read/write position in frames.

        Examples
        --------
        >>> from pysoundfile import SoundFile, SEEK_END
        >>> myfile = SoundFile('stereo_file.wav')

        Seek to the beginning of the file:

        >>> myfile.seek(0)
        0

        Seek to the end of the file:

        >>> myfile.seek(0, SEEK_END)
        44100  # this is the file length

        """
        self._check_if_closed()
        position = _snd.sf_seek(self._file, frames, whence)
        self._handle_error()
        return position

    def tell(self):
        """Return the current read/write position."""
        return self.seek(0, SEEK_CUR)

    def read(self, frames=-1, dtype='float64', always_2d=True,
             fill_value=None, out=None):
        """Read from the file and return data as NumPy array.

        Reads the given number of frames in the given data format
        starting at the current read/write position.  This advances the
        read/write position by the same number of frames.
        By default, all frames from the current read/write position to
        the end of the file are returned.
        Use :meth:`.seek` to move the current read/write position.

        Parameters
        ----------
        frames : int, optional
            The number of frames to read. If ``frames < 0``, the whole
            rest of the file is read.
        dtype : {'float64', 'float32', 'int32', 'int16'}, optional
            See :func:`read`.

        Returns
        -------
        numpy.ndarray or type(out)
            The read data; either a new array or `out` or a view into
            `out`.  See :func:`read` for details.

        Other Parameters
        ----------------
        always_2d, fill_value, out
            See :func:`read`.

        Examples
        --------
        >>> from pysoundfile import SoundFile
        >>> myfile = SoundFile('stereo_file.wav')

        Reading 3 frames from a stereo file:

        >>> myfile.read(3)
        array([[ 0.71329652,  0.06294799],
               [-0.26450912, -0.38874483],
               [ 0.67398441, -0.11516333]])
        >>> myfile.close()

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
        """Write audio data to the file.

        Writes a number of frames at the read/write position to the
        file. This also advances the read/write position by the same
        number of frames and enlarges the file if necessary.

        Parameters
        ----------
        data : array_like
            See :func:`write`.

        """
        # no copy is made if data has already the correct memory layout:
        data = _np.ascontiguousarray(data)

        self._check_array(data)
        written = self._read_or_write('sf_writef_', data, len(data))
        assert written == len(data)

        if self.seekable():
            curr = self.tell()
            self._info.frames = self.seek(0, SEEK_END)
            self.seek(curr, SEEK_SET)
        else:
            self._info.frames += written

    def blocks(self, blocksize=None, overlap=0, frames=-1, dtype='float64',
               always_2d=True, fill_value=None, out=None):
        """Return a generator for block-wise reading.

        By default, the generator yields blocks of the given
        `blocksize` (using a given `overlap`) until the end of the file
        is reached; `frames` can be used to stop earlier.

        Parameters
        ----------
        blocksize : int
            The number of frames to read per block. Either this or `out`
            must be given.
        overlap : int, optional
            The number of frames to rewind between each block.
        frames : int, optional
            The number of frames to read.
            If ``frames < 1``, the file is read until the end.
        dtype : {'float64', 'float32', 'int32', 'int16'}, optional
            See :func:`read`.

        Yields
        ------
        numpy.ndarray or type(out)
            Blocks of audio data. See :func:`blocks` for details.

        Other Parameters
        ----------------
        always_2d, fill_value, out
            See :func:`read`.

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

    def flush(self):
        """Write unwritten data to the file system.

        Data written with :meth:`.write` is not immediately written to
        the file system but buffered in memory to be written at a later
        time.  Calling :meth:`.flush` makes sure that all changes are
        actually written to the file system.

        This has no effect on files opened in read-only mode.

        """
        self._check_if_closed()
        _snd.sf_write_sync(self._file)

    def close(self):
        """Close the file.  Can be called multiple times."""
        if not self.closed:
            # be sure to flush data to disk before closing the file
            self.flush()
            err = _snd.sf_close(self._file)
            self._file = None
            self._handle_error_number(err)

    def _init_virtual_io(self, file):
        """Initialize callback functions for sf_open_virtual()."""
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

    def _handle_error(self):
        """Check the error flag of the SNDFILE* structure."""
        self._check_if_closed()
        err = _snd.sf_error(self._file)
        self._handle_error_number(err)

    def _handle_error_number(self, err):
        """Pretty-print a numerical error code."""
        if err != 0:
            err_str = _snd.sf_error_number(err)
            raise RuntimeError(_ffi.string(err_str).decode())

    def _getAttributeNames(self):
        """Return all attributes used in __setattr__ and __getattr__.

        This is useful for auto-completion (e.g. IPython).

        """
        return _str_types

    def _check_if_closed(self):
        """Check if the file is closed and raise an error if it is.

        This should be used in every method that uses self._file.

        """
        if self.closed:
            raise ValueError("I/O operation on closed file")

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

    def _check_frames(self, frames, fill_value):
        # Check if frames is larger than the remaining frames in the file
        if self.seekable():
            remaining_frames = len(self) - self.tell()
            if frames < 0 or (frames > remaining_frames
                              and fill_value is None):
                frames = remaining_frames
        elif frames < 0:
            raise ValueError("frames must be specified for non-seekable files")
        return frames

    def _check_array(self, array):
        """Do some error checking."""
        if (array.ndim not in (1, 2) or
                array.ndim == 1 and self.channels != 1 or
                array.ndim == 2 and array.shape[1] != self.channels):
            raise ValueError("Invalid shape: %s" % repr(array.shape))

        if array.dtype not in _ffi_types:
            raise ValueError("dtype must be one of %s" %
                             repr([dt.name for dt in _ffi_types]))

    def _create_empty_array(self, frames, always_2d, dtype):
        """Create an empty array with appropriate shape."""
        if always_2d or self.channels > 1:
            shape = frames, self.channels
        else:
            shape = frames,
        return _np.empty(shape, dtype, order='C')

    def _read_or_write(self, funcname, array, frames):
        """Call into libsndfile."""
        self._check_if_closed()

        ffi_type = _ffi_types[array.dtype]
        assert array.flags.c_contiguous
        assert array.dtype.itemsize == _ffi.sizeof(ffi_type)
        assert array.size >= frames * self.channels

        if self.seekable():
            curr = self.tell()
        func = getattr(_snd, funcname + ffi_type)
        ptr = _ffi.cast(ffi_type + '*', array.__array_interface__['data'][0])
        frames = func(self._file, ptr, frames)
        self._handle_error()
        if self.seekable():
            self.seek(curr + frames, SEEK_SET)  # Update read & write position
        return frames

    def _prepare_read(self, start, stop, frames):
        # Seek to start frame and calculate length
        if start != 0 and not self.seekable():
            raise ValueError("start is only allowed for seekable files")
        if frames >= 0 and stop is not None:
            raise TypeError("Only one of {frames, stop} may be used")

        start, stop, _ = slice(start, stop).indices(len(self))
        if stop < start:
            stop = start
        if frames < 0:
            frames = stop - start
        if self.seekable():
            self.seek(start, SEEK_SET)
        return frames


def _format_int(format, subtype, endian):
    """Return numeric ID for given format|subtype|endian combo."""
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


def _format_str(format_int):
    """Return the string representation of a given numeric format."""
    for dictionary in _formats, _subtypes, _endians:
        for k, v in dictionary.items():
            if v == format_int:
                return k
    return hex(format_int)


def _format_info(format_int, format_flag=_snd.SFC_GET_FORMAT_INFO):
    """Return the ID and short description of a given format."""
    format_info = _ffi.new("SF_FORMAT_INFO*")
    format_info.format = format_int
    _snd.sf_command(_ffi.NULL, format_flag, format_info,
                    _ffi.sizeof("SF_FORMAT_INFO"))
    name = format_info.name
    return (_format_str(format_info.format),
            _ffi.string(name).decode() if name else "")


def _available_formats_helper(count_flag, format_flag):
    """Helper for available_formats() and available_subtypes()."""
    count = _ffi.new("int*")
    _snd.sf_command(_ffi.NULL, count_flag, count, _ffi.sizeof("int"))
    for format_int in range(count[0]):
        yield _format_info(format_int, format_flag)
