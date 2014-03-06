from cffi import FFI as _FFI
import numpy as _np
import os as _os

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

typedef struct SF_FORMAT_INFO
{
    int         format ;
    const char* name ;
    const char* extension ;
} SF_FORMAT_INFO ;
""")

_M_READ = 0x10
_M_WRITE = 0x20
_M_RDWR = 0x30

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

_SUBMASK  = 0x0000FFFF
_TYPEMASK = 0x0FFF0000
_ENDMASK  = 0x30000000

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

_GET_FORMAT_INFO = 0x1028

class FormatType(int):
    def __repr__(self):
        return _formats.get(self, int.__repr__(self))

class SubtypeType(int):
    def __repr__(self):
        return _subtypes.get(self, int.__repr__(self))

class EndianType(int):
    def __repr__(self):
        return _endians.get(self, int.__repr__(self))

def _add_formats_to_module_namespace(format_dict, format_type):
    for k, v in format_dict.items():
        globals()[v] = format_type(k)

_add_formats_to_module_namespace(_formats, FormatType)
_add_formats_to_module_namespace(_subtypes, SubtypeType)
_add_formats_to_module_namespace(_endians, EndianType)

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
    #'vox': RAW | VOX_ADPCM,
}

_default_subtypes = {
    WAV: PCM_16,
    AIFF: PCM_16,
    AU: PCM_16,
    #RAW:  # subtype must be explicit!
    #PAF:
    #SVX:
    #NIST:
    #VOC:
    #IRCAM:
    #W64:
    MAT4: DOUBLE,
    MAT5: DOUBLE,
    #PVF:
    #XI:
    #HTK:
    #SDS:
    #AVR:
    WAVEX: PCM_16,
    #SD2:
    FLAC: PCM_16,
    CAF: PCM_16,
    #WVE:
    OGG: VORBIS,
    #MPC2K:
    #RF64:
}

_snd_strings = {
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
    channels. Each sound file can be opened with mode 'r', 'w', or 'rw'.
    Note that 'rw' is unsupported for some formats.

    Data can be written to the file using write(), or read from the
    file using read(). Every read and write operation starts at a
    certain position in the file. Reading N frames will change this
    position by N frames as well. Alternatively, seek() and
    seek_absolute() can be used to set the current position to a frame
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

    def __init__(self, name, mode='r', sample_rate=None, channels=None,
                 subtype=None, endian=None, format=None, virtual_io=False):
        """Open a new SoundFile.

        If a file is only opened with mode='r' or mode='rw',
        no sample_rate, channels or file format need to be given. If a
        file is opened with mode='w', you must provide a sample_rate,
        a number of channels, and a file format. An exception is the
        RAW data format, which requires these data points for reading
        as well.

        File formats consist of three parts:
        - one of the file types from snd_types
        - one of the data types from snd_subtypes
        - an endianness from snd_endians
        and can be either a tuple of three strings indicate the keys,
        or an OR'ed together integer of them.

        Since this is somewhat burdensome if you have to do it for
        every new file, you can use one of the commonly used
        pre-defined types wave_file, flac_file, matlab_file or
        ogg_file.

        """
        _avoid_format_types(mode, sample_rate, channels)
        try:
            mode_int = {'r':  _M_READ,
                        'w':  _M_WRITE,
                        'rw': _M_RDWR}[mode]
        except KeyError:
            raise ValueError("invalid mode: " + mode)
        self.mode = mode
        original_format, original_endian = format, endian
        if format is None:
            ext = name.rsplit('.', 1)[-1]
            format = _format_by_extension.get(ext.lower(), 0x0)
        info = _ffi.new("SF_INFO*")
        if mode == 'w' or format == RAW:
            assert sample_rate, \
                "sample_rate must be specified for mode='w' and format=RAW!"
            info.samplerate = sample_rate
            assert channels, \
                "channels must be specified for mode='w' and format=RAW!"
            info.channels = channels
            if subtype is None:
                subtype = _default_subtypes.get(format, 0x0)
            endian = endian or FILE
            format = format | subtype | endian
            assert format, "No format specified!"
            assert format & _TYPEMASK, "Invalid format!"
            assert format & _SUBMASK, "Invalid subtype!"
            assert endian == FILE or format & _ENDMASK, "Invalid endian-ness!"
            info.format = format
            assert _snd.sf_format_check(info), \
                "Invalid combination of format, subtype and endian!"
        else:
            should_be_none = [sample_rate, channels, subtype,
                              original_endian, original_format]
            if should_be_none != [None] * len(should_be_none):
                raise RuntimeError("If mode='r', none of these arguments are "
                                   "allowed: sample_rate, channels, format, "
                                   "subtype, endian")

        if virtual_io:
            fObj = name
            for attr in ('seek', 'read', 'write', 'tell'):
                if not hasattr(fObj, attr):
                    msg = 'File-like object must have: "%s"' % attr
                    raise RuntimeError(msg)
            self._vio = self._init_vio(fObj)
            vio = _ffi.new("SF_VIRTUAL_IO*", self._vio)
            self._vio['vio_cdata'] = vio
            self._file = _snd.sf_open_virtual(vio, mode_int, info,
                                              _ffi.NULL)
        else:
            filename = _ffi.new('char[]', name.encode())
            self._file = _snd.sf_open(filename, mode_int, info)

        self._handle_error()

        self.frames = info.frames
        self.sample_rate = info.samplerate
        self.channels = info.channels
        self.format = FormatType(info.format & _TYPEMASK)
        self.subtype = SubtypeType(info.format & _SUBMASK)
        self.endian = EndianType(info.format & _ENDMASK)
        self.sections = info.sections
        self.seekable = info.seekable == 1

    @property
    def format_string(self):
        return get_format_info(self.format)

    @property
    def subtype_string(self):
        return get_format_info(self.subtype)

    def _init_vio(self, fObj):
        # Define callbacks here, so they can reference fObj / size
        @_ffi.callback("sf_vio_get_filelen")
        def vio_get_filelen(user_data):
            # Streams must set _length or implement __len__
            if hasattr(fObj, '_length'):
                size = fObj._length
            elif not hasattr(fObj, '__len__'):
                old_file_position = fObj.tell()
                fObj.seek(0, _os.SEEK_END)
                size = fObj.tell()
                fObj.seek(old_file_position, _os.SEEK_SET)
            else:
                size = len(fObj)
            return size

        @_ffi.callback("sf_vio_seek")
        def vio_seek(offset, whence, user_data):
            fObj.seek(offset, whence)
            curr = fObj.tell()
            return curr

        @_ffi.callback("sf_vio_read")
        def vio_read(ptr, count, user_data):
            buf = _ffi.buffer(ptr, count)
            data_read = fObj.readinto(buf)
            return data_read

        @_ffi.callback("sf_vio_write")
        def vio_write(ptr, count, user_data):
            buf = _ffi.buffer(ptr)
            data = buf[:]
            length = fObj.write(data)
            return length

        @_ffi.callback("sf_vio_tell")
        def vio_tell(user_data):
            return fObj.tell()

        vio = {
            'get_filelen': vio_get_filelen,
            'seek': vio_seek,
            'read': vio_read,
            'write': vio_write,
            'tell': vio_tell,
        }
        return vio

    def __del__(self):
        # be sure to flush data to disk before closing the file
        if self._file:
            _snd.sf_write_sync(self._file)
            err = _snd.sf_close(self._file)
            self._handle_error_number(err)
            self._file = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        # flush remaining data to disk and close file
        self.__del__()

    def _handle_error(self):
        # this checks the error flag of the SNDFILE* structure
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
        return _snd_strings

    def __setattr__(self, name, value):
        # access text data in the sound file through properties
        if name in _snd_strings:
            if self.mode == 'r':
                raise RuntimeError("Can not change %s of file in read mode" %
                                   name)
            data = _ffi.new('char[]', value.encode())
            err = _snd.sf_set_string(self._file, _snd_strings[name], data)
            self._handle_error_number(err)
        else:
            super(SoundFile, self).__setattr__(name, value)

    def __getattr__(self, name):
        # access text data in the sound file through properties
        if name in _snd_strings:
            data = _snd.sf_get_string(self._file, _snd_strings[name])
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
        curr = self.seek(0)
        self.seek_absolute(start)
        data = self.read(stop - start)
        self.seek_absolute(curr)
        if second_frame:
            return data[(slice(None), second_frame)]
        else:
            return data

    def __setitem__(self, frame, data):
        # access the file as if it where a one-dimensional Numpy
        # array. Data must be in the form (frames x channels).
        # Both open slice bounds and negative values are allowed.
        if self.mode == 'r':
            raise RuntimeError("Can not write to read-only file")
        start, stop = self._get_slice_bounds(frame)
        if stop - start != len(data):
            raise IndexError(
                "Could not fit data of length %i into slice of length %i" %
                (len(data), stop - start))
        curr = self.seek(0)
        self.seek_absolute(start)
        self.write(data)
        self.seek_absolute(curr)
        return data

    def flush(self):
        """Write unwritten data to disk."""
        _snd.sf_write_sync(self._file)

    def seek(self, frames):
        """Set the read position relative to the current position.

        Positive values will fast-forward. Negative values will rewind.

        Returns the new absolute read position in frames.
        """
        return _snd.sf_seek(self._file, frames, _os.SEEK_CUR)

    def seek_absolute(self, frames):
        """Set an absolute read position.

        Positive values will set the read position to the given frame
        index. Negative values will set the read position to the given
        index counted from the end of the file.

        Returns the new absolute read position in frames.
        """
        if frames >= 0:
            return _snd.sf_seek(self._file, frames, _os.SEEK_SET)
        else:
            return _snd.sf_seek(self._file, frames, _os.SEEK_END)

    def read(self, frames=None, dtype='float32'):
        """Read a number of frames from the file.

        Reads the given number of frames in the given data format from
        the current read position. This also advances the read
        position by the same number of frames.
        Use frames=None to read until the end of the file.

        Returns the read data as a (frames x channels) NumPy array.

        If there is not enough data left in the file to read, a
        smaller NumPy array will be returned.

        """
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
        if frames is None:
            curr = self.seek(0)
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
        if self.mode == 'r':
            raise RuntimeError("Can not write to read-only file")
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
        return written

def open(*args, **kwargs):
    return SoundFile(*args, **kwargs)

def read(filename, frames=None, start=None, stop=None, **kwargs):
    # If frames and stop are both specified, frames takes precedence!
    # start and stop accept negative indices.
    read_kwargs = {}
    if 'dtype' in kwargs:
        read_kwargs['dtype'] = kwargs.pop('dtype')
    with open(filename, 'r', **kwargs) as f:
        start, stop, _ = slice(start, stop).indices(f.frames)
        if frames is None:
            frames = max(0, stop - start)
        f.seek_absolute(start)
        data = f.read(frames, **read_kwargs)
    return data, f.sample_rate

def write(data, filename, sample_rate, *args, **kwargs):
    # e.g. write(myarray, 'myfile.wav', 44100, sf.FLOAT)
    _avoid_format_types(sample_rate)
    if data.ndim == 1:
        channels = 1
    elif data.ndim == 2:
        channels = data.shape[1]
    else:
        raise RuntimeError("Only one- and two-dimensional arrays are allowed!")
    frames = data.shape[0]
    with open(filename, 'w', sample_rate, channels, *args, **kwargs) as f:
        written = f.write(data)
    assert frames == written, "Error writing file!"

def get_format_info(format):
    format_info = _ffi.new("struct SF_FORMAT_INFO*")
    format_info.format = format
    _snd.sf_command(_ffi.NULL, _GET_FORMAT_INFO, format_info,
                    _ffi.sizeof("SF_FORMAT_INFO"))
    return _ffi.string(format_info.name).decode() if format_info.name else ""

def _avoid_format_types(*args):
    for arg in args:
        if isinstance(arg, FormatType):
            raise TypeError("Unexpected FormatType!")
        if isinstance(arg, SubtypeType):
            raise TypeError("Unexpected SubtypeType!")
        if isinstance(arg, EndianType):
            raise TypeError("Unexpected EndianType!")
