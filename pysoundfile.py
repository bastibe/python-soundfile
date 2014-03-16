import numpy as _np
from cffi import FFI as _FFI
from os import SEEK_SET, SEEK_CUR, SEEK_END

"""PySoundFile is an audio library based on libsndfile, CFFI and Numpy

PySoundFile can read and write sound files. File reading/writing is
supported through libsndfile[1], which is a free, cross-platform,
open-source library for reading and writing many different sampled
sound file formats that runs on many platforms including Windows, OS
X, and Unix. It is accessed through CFFI[2], which is a foreight
function interface for Python calling C code. CFFI is supported for
CPython 2.6+, 3.x and PyPy 2.0+. PySoundFile represents audio data as
NumPy arrays.

[1]: http://www.mega-nerd.com/libsndfile/
[2]: http://cffi.readthedocs.org/

Every sound file is represented as a SoundFile object. SoundFiles can
be created for reading, writing, or both. Each SoundFile has a
sample_rate, a number of channels, and a file format. These can not be
changed at runtime.

A SoundFile has methods for reading and writing data to/from the file.
Even though every sound file has a fixed file format, reading and
writing is possible in four different NumPy formats: int16, int32,
float32 and float64.

At the same time, SoundFiles act as sequence types, so you can use
slices to read or write data as well. Since there is no way of
specifying data formats for slices, the SoundFile will always return
float32 data for those.

Note that you need to have libsndfile installed in order to use
PySoundFile. On Windows, you need to rename the library to
"sndfile.dll".

PySoundFile is BSD licensed.
(c) 2013, Bastian Bechtold

"""

_ffi = _FFI()
_ffi.cdef("""
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

_open_modes = {
    0x10: 'READ',
    0x20: 'WRITE',
    0x30: 'RDWR'
}

_formats = {
    0x010000: 'WAV',    # Microsoft WAV format (little endian default).
    0x020000: 'AIFF',   # Apple/SGI AIFF format (big endian).
    0x030000: 'AU',     # Sun/NeXT AU format (big endian).
    0x040000: 'RAW',    # RAW PCM data.
    0x050000: 'PAF',    # Ensoniq PARIS file format.
    0x060000: 'SVX',    # Amiga IFF / SVX8 / SV16 format.
    0x070000: 'NIST',   # Sphere NIST format.
    0x080000: 'VOC',    # VOC files.
    0x0A0000: 'IRCAM',  # Berkeley/IRCAM/CARL
    0x0B0000: 'W64',    # Sonic Foundry's 64 bit RIFF/WAV
    0x0C0000: 'MAT4',   # Matlab (tm) V4.2 / GNU Octave 2.0
    0x0D0000: 'MAT5',   # Matlab (tm) V5.0 / GNU Octave 2.1
    0x0E0000: 'PVF',    # Portable Voice Format
    0x0F0000: 'XI',     # Fasttracker 2 Extended Instrument
    0x100000: 'HTK',    # HMM Tool Kit format
    0x110000: 'SDS',    # Midi Sample Dump Standard
    0x120000: 'AVR',    # Audio Visual Research
    0x130000: 'WAVEX',  # MS WAVE with WAVEFORMATEX
    0x160000: 'SD2',    # Sound Designer 2
    0x170000: 'FLAC',   # FLAC lossless file format
    0x180000: 'CAF',    # Core Audio File format
    0x190000: 'WVE',    # Psion WVE format
    0x200000: 'OGG',    # Xiph OGG container
    0x210000: 'MPC2K',  # Akai MPC 2000 sampler
    0x220000: 'RF64',   # RF64 WAV file
}

_subtypes = {
    0x0001: 'PCM_S8',     # Signed 8 bit data
    0x0002: 'PCM_16',     # Signed 16 bit data
    0x0003: 'PCM_24',     # Signed 24 bit data
    0x0004: 'PCM_32',     # Signed 32 bit data
    0x0005: 'PCM_U8',     # Unsigned 8 bit data (WAV and RAW only)
    0x0006: 'FLOAT',      # 32 bit float data
    0x0007: 'DOUBLE',     # 64 bit float data
    0x0010: 'ULAW',       # U-Law encoded.
    0x0011: 'ALAW',       # A-Law encoded.
    0x0012: 'IMA_ADPCM',  # IMA ADPCM.
    0x0013: 'MS_ADPCM',   # Microsoft ADPCM.
    0x0020: 'GSM610',     # GSM 6.10 encoding.
    0x0021: 'VOX_ADPCM',  # OKI / Dialogix ADPCM
    0x0030: 'G721_32',    # 32kbs G721 ADPCM encoding.
    0x0031: 'G723_24',    # 24kbs G723 ADPCM encoding.
    0x0032: 'G723_40',    # 40kbs G723 ADPCM encoding.
    0x0040: 'DWVW_12',    # 12 bit Delta Width Variable Word encoding.
    0x0041: 'DWVW_16',    # 16 bit Delta Width Variable Word encoding.
    0x0042: 'DWVW_24',    # 24 bit Delta Width Variable Word encoding.
    0x0043: 'DWVW_N',     # N bit Delta Width Variable Word encoding.
    0x0050: 'DPCM_8',     # 8 bit differential PCM (XI only)
    0x0051: 'DPCM_16',    # 16 bit differential PCM (XI only)
    0x0060: 'VORBIS',     # Xiph Vorbis encoding.
}

_endians = {
    0x00000000: 'FILE',    # Default file endian-ness.
    0x10000000: 'LITTLE',  # Force little endian-ness.
    0x20000000: 'BIG',     # Force big endian-ness.
    0x30000000: 'CPU',     # Force CPU endian-ness.
}

_SUBMASK =  0x0000FFFF
_TYPEMASK = 0x0FFF0000
_ENDMASK =  0x30000000

_TITLE       = 0x01
_COPYRIGHT   = 0x02
_SOFTWARE    = 0x03
_ARTIST      = 0x04
_COMMENT     = 0x05
_DATE        = 0x06
_ALBUM       = 0x07
_LICENSE     = 0x08
_TRACKNUMBER = 0x09
_GENRE       = 0x10

_GET_FORMAT_INFO          = 0x1028
_GET_FORMAT_MAJOR_COUNT   = 0x1030
_GET_FORMAT_MAJOR         = 0x1031
_GET_FORMAT_SUBTYPE_COUNT = 0x1032
_GET_FORMAT_SUBTYPE       = 0x1033

class _ModeType(int):
    def __repr__(self):
        return _open_modes.get(self, int.__repr__(self))
    __str__ = __repr__

class _FormatType(int):
    def __repr__(self):
        return _formats.get(self, int.__repr__(self))
    __str__ = __repr__

class _SubtypeType(int):
    def __repr__(self):
        return _subtypes.get(self, int.__repr__(self))
    __str__ = __repr__

class _EndianType(int):
    def __repr__(self):
        return _endians.get(self, int.__repr__(self))
    __str__ = __repr__

def _add_constants_to_module_namespace(constants_dict, constants_type):
    for k, v in constants_dict.items():
        globals()[v] = constants_type(k)

_add_constants_to_module_namespace(_open_modes, _ModeType)
_add_constants_to_module_namespace(_formats, _FormatType)
_add_constants_to_module_namespace(_subtypes, _SubtypeType)
_add_constants_to_module_namespace(_endians, _EndianType)

_format_by_extension = {
    'wav': WAV,
    'aif': AIFF,
    'aiff': AIFF,
    'aifc': AIFF | FLOAT,
    'au': AU,
    'raw': RAW,
    'paf': PAF,
    'svx': SVX,
    'nist': NIST,
    'voc': VOC,
    'ircam': IRCAM,
    'w64': W64,
    'mat4': MAT4,
    'mat': MAT5,
    'pvf': PVF,
    'xi': XI,
    'htk': HTK,
    'sds': SDS,
    'avr': AVR,
    'wavex': WAVEX,
    'sd2': SD2,
    'flac': FLAC,
    'caf': CAF,
    'wve': WVE,
    'ogg': OGG,
    'oga': OGG,
    'mpc2k': MPC2K,
    'rf64': RF64,
    'vox': RAW | VOX_ADPCM,
}

# see http://www.mega-nerd.com/libsndfile/ for supported subtypes
_default_subtypes = {
    WAV: PCM_16,
    AIFF: PCM_16,
    AU: PCM_16,
    #RAW:  # subtype must be explicit!
    PAF: PCM_16,
    SVX: PCM_16,
    NIST: PCM_16,
    VOC: PCM_16,
    IRCAM: PCM_16,
    W64: PCM_16,
    MAT4: DOUBLE,
    MAT5: DOUBLE,
    PVF: PCM_16,
    XI: DPCM_16,
    HTK: PCM_16,
    #SDS:
    #AVR:
    WAVEX: PCM_16,
    SD2: PCM_16,
    FLAC: PCM_16,
    CAF: PCM_16,
    #WVE:
    OGG: VORBIS,
    #MPC2K:
    #RF64:
}

_str_types = {
    'title': _TITLE,
    'copyright': _COPYRIGHT,
    'software': _SOFTWARE,
    'artist': _ARTIST,
    'comment': _COMMENT,
    'date': _DATE,
    'album': _ALBUM,
    'license': _LICENSE,
    'tracknumber': _TRACKNUMBER,
    'genre': _GENRE
}

_snd = _ffi.dlopen('sndfile')


class SoundFile(object):

    """SoundFile handles reading and writing to sound files.

    Each SoundFile opens one sound file on the disk. This sound file
    has a specific samplerate, data format and a set number of
    channels. Each sound file can be opened with one of the modes
    READ/WRITE/RDWR. Note that RDWR is unsupported for some formats.

    Data can be written to the file using write(), or read from the
    file using read(). Every read and write operation starts at a
    certain position in the file. Reading N frames will change this
    position by N frames as well. Alternatively, seek()
    can be used to set the current position to a frame
    index offset from the current position, the start of the file, or
    the end of the file, respectively.

    Alternatively, slices can be used to access data at arbitrary
    positions in the file. Note that slices currently only work on
    frame indices, not channels. The quickest way to read in a whole
    file as a float32 NumPy array is in fact SoundFile('filename')[:].

    All data access uses frames as index. A frame is one discrete
    time-step in the sound file. Every frame contains as many samples
    as there are channels in the file.

    In addition to audio data, there are a number of text fields in
    every sound file. In particular, you can set a title, a copyright
    notice, a software description, the artist name, a comment, a
    date, the album name, a license, a tracknumber and a genre. Note
    however, that not all of these fields are supported for every file
    format.

    """

    def __init__(self, file, mode=READ, sample_rate=None, channels=None,
                 subtype=None, endian=None, format=None, closefd=True):
        """Open a new SoundFile.

        If a file is opened with mode READ (the default) or RDWR,
        no sample_rate, channels or file format need to be given. If a
        file is opened with mode WRITE, you must provide a sample_rate,
        a number of channels, and a file format. An exception is the
        RAW data format, which requires these data points for reading
        as well.

        Instead of the library constants READ/WRITE/RDWR you can also
        use the (case-insensitive) strings 'r'/'w'/'rw' or
        'READ'/'WRITE'/'RDWR'.

        File formats consist of three parts:
         - a "major format" which is by default obtained from the
           extension of the file name (if known) and which can be
           forced with the format argument (e.g. format=WAVEX).
         - a "subtype", e.g. PCM_24. Most major formats have a default
           subtype which is used if no subtype is specified.
         - an endian-ness: FILE (default), LITTLE, BIG or CPU.
           In most cases this doesn't have to be specified.

        The functions available_formats() and available_subtypes() can
        be used to obtain a list of all avaliable major formats and
        subtypes, respectively.

        """
        assert _raise_error_if_format_type(file, sample_rate, channels)

        if isinstance(mode, str):
            try:
                mode = {'read':  READ,  'r':  READ,
                        'write': WRITE, 'w':  WRITE,
                        'rdwr':  RDWR,  'rw': RDWR}[mode.lower()]
            except KeyError:
                pass
        if not isinstance(mode, _ModeType):
            raise ValueError("Invalid mode: %s" % repr(mode))

        original_format, original_endian = format, endian
        if format is None:
            ext = getattr(file, 'name', file if isinstance(file, str) else ""
                          ).rsplit('.', 1)[-1]
            format = _format_by_extension.get(ext.lower(), 0x0)

        self._info = _ffi.new("SF_INFO*")
        if mode == WRITE or format == RAW:
            assert sample_rate, \
                "sample_rate must be specified for mode=WRITE and format=RAW!"
            self._info.samplerate = sample_rate
            assert channels, \
                "channels must be specified for mode=WRITE and format=RAW!"
            self._info.channels = channels

            def convert_if_string(var, dictionary):
                if isinstance(var, str):
                    for k, v in dictionary.items():
                        if var.upper() == v:
                            var = k
                            break
                    else:
                        raise ValueError("Invalid argument: %s" % repr(var))
                return var

            format = convert_if_string(format, _formats)
            subtype = convert_if_string(subtype, _subtypes)
            endian = convert_if_string(endian, _endians)

            if subtype is None:
                subtype = _default_subtypes.get(format, 0x0)
            endian = endian or FILE
            format = format | subtype | endian
            assert format, "No format specified!"
            assert format & _TYPEMASK, "Invalid format!"
            assert format & _SUBMASK, "Invalid subtype!"
            assert endian == FILE or format & _ENDMASK, "Invalid endian-ness!"
            self._info.format = format
            assert _snd.sf_format_check(self._info), \
                "Invalid combination of format, subtype and endian!"
        else:
            assert [sample_rate, channels, subtype, original_endian,
                    original_format] == [None] * 5, \
                "Only allowed if mode=WRITE or format=RAW: sample_rate, " \
                "channels, format, subtype, endian"

        self._name = file
        if isinstance(file, str):
            file = _ffi.new('char[]', file.encode())
            self._file = _snd.sf_open(file, mode, self._info)
        elif isinstance(file, int):
            self._file = _snd.sf_open_fd(file, mode, self._info, closefd)
        else:
            for attr in ('seek', 'read', 'write', 'tell'):
                if not hasattr(file, attr):
                    msg = "file must be a filename, a file descriptor or " \
                          "a file-like object with the methods " \
                          "'seek()', 'read()', 'write()' and 'tell()'!"
                    raise RuntimeError(msg)
            # Note: the callback functions in _vio must be kept alive!
            self._vio = self._init_vio(file)
            vio = _ffi.new("SF_VIRTUAL_IO*", self._vio)
            self._file = _snd.sf_open_virtual(vio, mode, self._info, _ffi.NULL)
            self._name = str(file)

        self._handle_error()
        self._mode = mode

    name = property(lambda self: self._name)
    mode = property(lambda self: self._mode)
    frames = property(lambda self: self._info.frames)
    sample_rate = property(lambda self: self._info.samplerate)
    channels = property(lambda self: self._info.channels)
    format = property(lambda self: _FormatType(self._info.format & _TYPEMASK))
    subtype = property(lambda self: _SubtypeType(self._info.format & _SUBMASK))
    endian = property(lambda self: _EndianType(self._info.format & _ENDMASK))
    format_string = property(lambda self: get_format_string(self.format))
    subtype_string = property(lambda self: get_format_string(self.subtype))
    sections = property(lambda self: self._info.sections)
    seekable = property(lambda self: self._info.seekable == 1)
    closed = property(lambda self: self._file is None)

    # avoid confusion if something goes wrong before assigning self._file:
    _file = None

    def _init_vio(self, file):
        # Define callbacks here, so they can reference file / size
        @_ffi.callback("sf_vio_get_filelen")
        def vio_get_filelen(user_data):
            # Streams must set _length or implement __len__
            if hasattr(file, '_length'):
                size = file._length
            elif not hasattr(file, '__len__'):
                old_file_position = file.tell()
                file.seek(0, SEEK_END)
                size = file.tell()
                file.seek(old_file_position, SEEK_SET)
            else:
                size = len(file)
            return size

        @_ffi.callback("sf_vio_seek")
        def vio_seek(offset, whence, user_data):
            file.seek(offset, whence)
            curr = file.tell()
            return curr

        @_ffi.callback("sf_vio_read")
        def vio_read(ptr, count, user_data):
            # first try readinto(), if not available fall back to read()
            try:
                buf = _ffi.buffer(ptr, count)
                data_read = file.readinto(buf)
            except AttributeError:
                data = file.read(count)
                buf = _ffi.buffer(ptr, len(data))
                buf[0:len(data)] = data
                data_read = len(data)
            return data_read

        @_ffi.callback("sf_vio_write")
        def vio_write(ptr, count, user_data):
            buf = _ffi.buffer(ptr, count)
            data = buf[:]
            length = file.write(data)
            return length

        @_ffi.callback("sf_vio_tell")
        def vio_tell(user_data):
            return file.tell()

        return {'get_filelen': vio_get_filelen,
                'seek': vio_seek,
                'read': vio_read,
                'write': vio_write,
                'tell': vio_tell}

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
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
            raise ValueError("I/O operation on closed file!")

    def __setattr__(self, name, value):
        # access text data in the sound file through properties
        if name in _str_types:
            self._check_if_closed()
            if self.mode == READ:
                raise RuntimeError("Can not change %s of file in READ mode" %
                                   name)
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
            if data == _ffi.NULL:
                return ""
            else:
                return _ffi.string(data).decode()
        else:
            raise AttributeError("SoundFile has no attribute %s" % name)

    def __len__(self):
        return self.frames

    def _get_slice_bounds(self, frame):
        # get start and stop index from slice, asserting step==1
        if not isinstance(frame, slice):
            frame = slice(frame, frame + 1)
        start, stop, step = frame.indices(len(self))
        if step != 1:
            raise RuntimeError("Step size must be 1!")
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
        curr = self.seek(0, SEEK_CUR | READ)
        self.seek(start, SEEK_SET | READ)
        data = self.read(stop - start)
        self.seek(curr, SEEK_SET | READ)
        if second_frame:
            return data[(slice(None), second_frame)]
        else:
            return data

    def __setitem__(self, frame, data):
        # access the file as if it where a one-dimensional Numpy
        # array. Data must be in the form (frames x channels).
        # Both open slice bounds and negative values are allowed.
        if self.mode == READ:
            raise RuntimeError("Cannot write to file opened in READ mode!")
        start, stop = self._get_slice_bounds(frame)
        if stop - start != len(data):
            raise IndexError(
                "Could not fit data of length %i into slice of length %i" %
                (len(data), stop - start))
        curr = self.seek(0, SEEK_CUR | WRITE)
        self.seek(start, SEEK_SET | WRITE)
        self.write(data)
        self.seek(curr, SEEK_SET | WRITE)
        return data

    def flush(self):
        """Write unwritten data to disk."""
        self._check_if_closed()
        _snd.sf_write_sync(self._file)

    def close(self):
        """Close the file. Can be called multiple times."""
        if not self.closed:
            # be sure to flush data to disk before closing the file
            self.flush()
            err = _snd.sf_close(self._file)
            self._file = None
            self._handle_error_number(err)

    def seek(self, frames, whence=SEEK_SET):
        """Set the read and/or write position.

        By default (whence=SEEK_SET), frames are counted from the
        beginning of the file. SEEK_CUR seeks from the current position
        (positive and negative values are allowed).
        SEEK_END seeks from the end (use negative values).

        In RDWR mode, the whence argument can be combined (using
        logical or) with READ or WRITE in order to set only the read
        or write position, respectively (e.g. SEEK_SET | WRITE).

        To set the read/write position to the beginning of the file,
        use seek(0), to set it to right after the last frame,
        e.g. for appending new data, use seek(0, SEEK_END).

        Returns the new absolute read position in frames or a negative
        value on error.
        """
        self._check_if_closed()
        return _snd.sf_seek(self._file, frames, whence)

    def read(self, frames=-1, dtype='float32'):
        """Read a number of frames from the file.

        Reads the given number of frames in the given data format from
        the current read position. This also advances the read
        position by the same number of frames.
        Use frames=-1 to read until the end of the file.

        Returns the read data as a (frames x channels) NumPy array.

        If there is not enough data left in the file to read, a
        smaller NumPy array will be returned.

        """
        self._check_if_closed()
        if self.mode == WRITE:
            raise RuntimeError("Cannot read from file opened in WRITE mode!")
        formats = {
            _np.float64: 'double[]',
            _np.float32: 'float[]',
            _np.int32: 'int[]',
            _np.int16: 'short[]'
        }
        readers = {
            _np.float64: _snd.sf_readf_double,
            _np.float32: _snd.sf_readf_float,
            _np.int32: _snd.sf_readf_int,
            _np.int16: _snd.sf_readf_short
        }
        dtype = _np.dtype(dtype)
        if dtype.type not in formats:
            raise ValueError("Can only read int16, int32, float32 and float64")
        if frames < 0:
            curr = self.seek(0, SEEK_CUR | READ)
            frames = self.frames - curr
        data = _ffi.new(formats[dtype.type], frames*self.channels)
        read = readers[dtype.type](self._file, data, frames)
        self._handle_error()
        np_data = _np.frombuffer(_ffi.buffer(data), dtype=dtype,
                                 count=read*self.channels)
        return _np.reshape(np_data, (read, self.channels))

    def write(self, data):
        """Write a number of frames to the file.

        Writes a number of frames to the current read position in the
        file. This also advances the read position by the same number
        of frames and enlarges the file if necessary.

        The data must be provided as a (frames x channels) NumPy
        array.

        """
        self._check_if_closed()
        if self.mode == READ:
            raise RuntimeError("Cannot write to file opened in READ mode!")
        formats = {
            _np.float64: 'double*',
            _np.float32: 'float*',
            _np.int32: 'int*',
            _np.int16: 'short*'
        }
        writers = {
            _np.float64: _snd.sf_writef_double,
            _np.float32: _snd.sf_writef_float,
            _np.int32: _snd.sf_writef_int,
            _np.int16: _snd.sf_writef_short
        }
        if data.dtype.type not in writers:
            raise ValueError("Data must be int16, int32, float32 or float64")
        raw_data = _ffi.new('char[]', data.flatten().tostring())
        written = writers[data.dtype.type](self._file,
                                      _ffi.cast(
                                          formats[data.dtype.type], raw_data),
                                      len(data))
        self._handle_error()

        curr = self.seek(0, SEEK_CUR | WRITE)
        self._info.frames = self.seek(0, SEEK_END | WRITE)
        self.seek(curr, SEEK_SET | WRITE)

        return written


def _get_format_info(format, format_flag=_GET_FORMAT_INFO, format_type=int):
    # Return the ID and name of a given format.
    format_info = _ffi.new("struct SF_FORMAT_INFO*")
    format_info.format = format
    _snd.sf_command(_ffi.NULL, format_flag, format_info,
                    _ffi.sizeof("SF_FORMAT_INFO"))
    return (format_type(format_info.format),
            _ffi.string(format_info.name).decode() if format_info.name else "")


def _available_formats_helper(count_flag, format_flag, format_type=int):
    def get_count():
        count = _ffi.new("int*")
        _snd.sf_command(_ffi.NULL, count_flag, count, _ffi.sizeof("int"))
        return count[0]

    return [_get_format_info(f, format_flag, format_type)
            for f in range(get_count())]


def available_formats():
    """Return a list of available major formats."""
    return _available_formats_helper(_GET_FORMAT_MAJOR_COUNT,
                                     _GET_FORMAT_MAJOR, _FormatType)


def available_subtypes():
    """Return a list of available subtypes."""
    return _available_formats_helper(_GET_FORMAT_SUBTYPE_COUNT,
                                     _GET_FORMAT_SUBTYPE, _SubtypeType)


def get_format_string(format):
    """Return the name of a given major format or subtype."""
    return _get_format_info(format)[1]


def _raise_error_if_format_type(*args):
    # raise error if one of the arguments has one of the format types.
    # For use in assertions to prevent accidentally passing soundfile formats
    # where numeric values are expected (esp. when using positional arguments).
    format_types = (_FormatType, _SubtypeType, _EndianType)
    for arg in args:
        if isinstance(arg, format_types):
            raise TypeError("%s is not allowed here!" % repr(arg))
    return True
