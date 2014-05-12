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
float64 data for those.

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

_FALSE = 0
_TRUE  = 1

_SUBMASK  = 0x0000FFFF
_TYPEMASK = 0x0FFF0000
_ENDMASK  = 0x30000000

_GET_FORMAT_INFO          = 0x1028
_GET_FORMAT_MAJOR_COUNT   = 0x1030
_GET_FORMAT_MAJOR         = 0x1031
_GET_FORMAT_SUBTYPE_COUNT = 0x1032
_GET_FORMAT_SUBTYPE       = 0x1033

_open_modes = {
    'r':  0x10,
    'w':  0x20,
    'rw': 0x30,
}

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
    'WAV':   0x010000, # Microsoft WAV format (little endian default).
    'AIFF':  0x020000, # Apple/SGI AIFF format (big endian).
    'AU':    0x030000, # Sun/NeXT AU format (big endian).
    'RAW':   0x040000, # RAW PCM data.
    'PAF':   0x050000, # Ensoniq PARIS file format.
    'SVX':   0x060000, # Amiga IFF / SVX8 / SV16 format.
    'NIST':  0x070000, # Sphere NIST format.
    'VOC':   0x080000, # VOC files.
    'IRCAM': 0x0A0000, # Berkeley/IRCAM/CARL
    'W64':   0x0B0000, # Sonic Foundry's 64 bit RIFF/WAV
    'MAT4':  0x0C0000, # Matlab (tm) V4.2 / GNU Octave 2.0
    'MAT5':  0x0D0000, # Matlab (tm) V5.0 / GNU Octave 2.1
    'PVF':   0x0E0000, # Portable Voice Format
    'XI':    0x0F0000, # Fasttracker 2 Extended Instrument
    'HTK':   0x100000, # HMM Tool Kit format
    'SDS':   0x110000, # Midi Sample Dump Standard
    'AVR':   0x120000, # Audio Visual Research
    'WAVEX': 0x130000, # MS WAVE with WAVEFORMATEX
    'SD2':   0x160000, # Sound Designer 2
    'FLAC':  0x170000, # FLAC lossless file format
    'CAF':   0x180000, # Core Audio File format
    'WVE':   0x190000, # Psion WVE format
    'OGG':   0x200000, # Xiph OGG container
    'MPC2K': 0x210000, # Akai MPC 2000 sampler
    'RF64':  0x220000, # RF64 WAV file
}

_subtypes = {
    'PCM_S8':    0x0001, # Signed 8 bit data
    'PCM_16':    0x0002, # Signed 16 bit data
    'PCM_24':    0x0003, # Signed 24 bit data
    'PCM_32':    0x0004, # Signed 32 bit data
    'PCM_U8':    0x0005, # Unsigned 8 bit data (WAV and RAW only)
    'FLOAT':     0x0006, # 32 bit float data
    'DOUBLE':    0x0007, # 64 bit float data
    'ULAW':      0x0010, # U-Law encoded.
    'ALAW':      0x0011, # A-Law encoded.
    'IMA_ADPCM': 0x0012, # IMA ADPCM.
    'MS_ADPCM':  0x0013, # Microsoft ADPCM.
    'GSM610':    0x0020, # GSM 6.10 encoding.
    'VOX_ADPCM': 0x0021, # OKI / Dialogix ADPCM
    'G721_32':   0x0030, # 32kbs G721 ADPCM encoding.
    'G723_24':   0x0031, # 24kbs G723 ADPCM encoding.
    'G723_40':   0x0032, # 40kbs G723 ADPCM encoding.
    'DWVW_12':   0x0040, # 12 bit Delta Width Variable Word encoding.
    'DWVW_16':   0x0041, # 16 bit Delta Width Variable Word encoding.
    'DWVW_24':   0x0042, # 24 bit Delta Width Variable Word encoding.
    'DWVW_N':    0x0043, # N bit Delta Width Variable Word encoding.
    'DPCM_8':    0x0050, # 8 bit differential PCM (XI only)
    'DPCM_16':   0x0051, # 16 bit differential PCM (XI only)
    'VORBIS':    0x0060, # Xiph Vorbis encoding.
}

_endians = {
    'FILE':   0x00000000, # Default file endian-ness.
    'LITTLE': 0x10000000, # Force little endian-ness.
    'BIG':    0x20000000, # Force big endian-ness.
    'CPU':    0x30000000, # Force CPU endian-ness.
}

# libsndfile doesn't specify default subtypes, these are somehow arbitrary:
_default_subtypes = {
    'WAV':   'PCM_16',
    'AIFF':  'PCM_16',
    'AU':    'PCM_16',
    #'RAW':  # subtype must be explicit!
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
    has a specific samplerate, data format and a set number of
    channels. Each sound file can be opened with one of the modes
    'r'/'w'/'rw'. Note that 'rw' is unsupported for some formats.

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
    file as a float64 NumPy array is in fact SoundFile('filename')[:].

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

    def __init__(self, file, mode='r', sample_rate=None, channels=None,
                 subtype=None, endian=None, format=None, closefd=True):
        """Open a new SoundFile.

        If a file is opened with mode 'r' (the default) or 'rw',
        no sample_rate, channels or file format need to be given. If a
        file is opened with mode 'w', you must provide a sample_rate,
        a number of channels, and a file format. An exception is the
        RAW data format, which requires these data points for reading
        as well.

        File formats consist of three case-insensitive strings:
         - a "major format" which is by default obtained from the
           extension of the file name (if known) and which can be
           forced with the format argument (e.g. format='WAVEX').
         - a "subtype", e.g. 'PCM_24'. Most major formats have a default
           subtype which is used if no subtype is specified.
         - an "endian-ness": 'FILE' (default), 'LITTLE', 'BIG' or 'CPU'.
           In most cases this doesn't have to be specified.

        The functions available_formats() and available_subtypes() can
        be used to obtain a list of all avaliable major formats and
        subtypes, respectively.

        """
        try:
            self._mode = mode
            mode_int = _open_modes[self._mode]
        except KeyError:
            raise ValueError("Invalid mode: %s" % repr(mode))

        original_format = format
        if format is None:
            filename = getattr(file, 'name', file)
            format = str(filename).rsplit('.', 1)[-1].upper()
            if self.mode == 'w' and format not in _formats:
                raise TypeError(
                    "No format specified and unable to get format from "
                    "file extension: %s" % repr(filename))

        self._info = _ffi.new("SF_INFO*")
        if self.mode == 'w' or str(format).upper() == 'RAW':
            if sample_rate is None:
                raise TypeError("sample_rate must be specified")
            self._info.samplerate = sample_rate
            if channels is None:
                raise TypeError("channels must be specified")
            self._info.channels = channels
            self._info.format = _format_int(format, subtype, endian)
        else:
            if [sample_rate, channels, original_format, subtype, endian] != \
                    [None] * 5:
                raise TypeError("Only allowed if mode='w' or format='RAW': "
                                "sample_rate, channels, "
                                "format, subtype, endian")

        self._name = file
        if isinstance(file, str):
            file = _ffi.new('char[]', file.encode())
            self._file = _snd.sf_open(file, mode_int, self._info)
        elif isinstance(file, int):
            self._file = _snd.sf_open_fd(file, mode_int, self._info, closefd)
        else:
            # Note: readinto() is not checked
            for attr in ('seek', 'read', 'write', 'tell'):
                if not hasattr(file, attr):
                    raise RuntimeError(
                        "file must be a filename, a file descriptor or "
                        "a file-like object with the methods "
                        "'seek()', 'read()', 'write()' and 'tell()'")
            # Note: the callback functions in _vio must be kept alive!
            self._vio = self._init_vio(file)
            vio = _ffi.new("SF_VIRTUAL_IO*", self._vio)
            self._file = _snd.sf_open_virtual(vio, mode_int, self._info,
                                              _ffi.NULL)
            self._name = str(file)

        self._handle_error()

    name = property(lambda self: self._name)
    mode = property(lambda self: self._mode)
    frames = property(lambda self: self._info.frames)
    sample_rate = property(lambda self: self._info.samplerate)
    channels = property(lambda self: self._info.channels)
    format = property(lambda self: _format_str(self._info.format & _TYPEMASK))
    subtype = property(lambda self: _format_str(self._info.format & _SUBMASK))
    endian = property(lambda self: _format_str(self._info.format & _ENDMASK))
    format_info = property(
        lambda self: _format_info(self._info.format & _TYPEMASK)[1])
    subtype_info = property(
        lambda self: _format_info(self._info.format & _SUBMASK)[1])
    sections = property(lambda self: self._info.sections)
    seekable = property(lambda self: self._info.seekable == _TRUE)
    closed = property(lambda self: self._file is None)

    # avoid confusion if something goes wrong before assigning self._file:
    _file = None

    def _init_vio(self, file):
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
                data_read = len(data)
                buf = _ffi.buffer(ptr, data_read)
                buf[0:data_read] = data
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
            if self.mode == 'r':
                raise RuntimeError("Can not change %s of file in read mode" %
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
        curr = self.seek(0, SEEK_CUR, 'r')
        self.seek(start, SEEK_SET, 'r')
        data = self.read(stop - start)
        self.seek(curr, SEEK_SET, 'r')
        if second_frame:
            return data[(slice(None), second_frame)]
        else:
            return data

    def __setitem__(self, frame, data):
        # access the file as if it where a one-dimensional Numpy
        # array. Data must be in the form (frames x channels).
        # Both open slice bounds and negative values are allowed.
        if self.mode == 'r':
            raise RuntimeError("Cannot write to file opened in read mode")
        start, stop = self._get_slice_bounds(frame)
        if stop - start != len(data):
            raise IndexError(
                "Could not fit data of length %i into slice of length %i" %
                (len(data), stop - start))
        curr = self.seek(0, SEEK_CUR, 'w')
        self.seek(start, SEEK_SET, 'w')
        self.write(data)
        self.seek(curr, SEEK_SET, 'w')
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

    def seek(self, frames, whence=SEEK_SET, which=None):
        """Set the read and/or write position.

        By default (whence=SEEK_SET), frames are counted from the
        beginning of the file. SEEK_CUR seeks from the current position
        (positive and negative values are allowed).
        SEEK_END seeks from the end (use negative values).

        If the file is opened in 'rw' mode, both read and write position
        are set to the same value by default.
        Use which='r' or which='w' to set only the read position or the
        write position, respectively.

        To set the read/write position to the beginning of the file,
        use seek(0), to set it to right after the last frame,
        e.g. for appending new data, use seek(0, SEEK_END).

        Returns the new absolute read position in frames or a negative
        value on error.

        """
        self._check_if_closed()
        if which in ('r', 'w'):
            whence |= _open_modes[which]
        elif which is not None:
            raise ValueError("Invalid which: %s" % repr(which))
        return _snd.sf_seek(self._file, frames, whence)

    def read(self, frames=-1, dtype='float64', always_2d=True,
             fill_value=None, out=None):
        """Read a number of frames from the file.

        Reads the given number of frames in the given data format from
        the current read position. This also advances the read
        position by the same number of frames.
        Use frames=-1 to read until the end of the file.

        By default, a two-dimensional array is returned even if the
        sound file has only one channel. Use always_2d=False to return
        a one-dimensional array in this case.

        If there is less data left in the file than requested, a
        shorter array is returned. Use fill_value to always return the
        given number of frames and fill all remaining frames with
        fill_value.

        If out is given as a numpy array, the data is written into
        that array. If there is not enough data left in the file to
        fill the array, the rest of the frames are ignored and a
        smaller view to the array is returned. Use fill_value to fill
        the rest of the array and always return the full-length array.

        """

        self._check_if_closed()
        if self.mode == 'w':
            raise RuntimeError("Cannot read from file opened in write mode")

        remaining_frames = self.frames - self.seek(0, SEEK_CUR, 'r')

        if frames < 0:
            frames = remaining_frames
        if frames > remaining_frames and fill_value is None:
            frames = remaining_frames

        if out is None:
            if always_2d or self.channels > 1:
                out = _np.empty((frames, self.channels), dtype)
            else:
                out = _np.empty(frames, dtype)

        self._check_frames_and_channels(out)

        frames_to_read = min(len(out), remaining_frames)

        ffi_type = _ffi_types[out.dtype]
        reader = getattr(_snd, 'sf_readf_' + ffi_type)
        ptr = _ffi.cast(ffi_type + '*', out.ctypes.data)
        read_frames = reader(self._file, ptr, frames_to_read)
        self._handle_error()
        assert read_frames == frames_to_read

        if frames_to_read == len(out):
            return out
        elif fill_value is None:
            return out[:frames_to_read]
        else:
            out[frames_to_read:] = fill_value
            return out

    def write(self, data):
        """Write a number of frames to the file.

        Writes a number of frames to the current write position in the
        file. This also advances the write position by the same number
        of frames and enlarges the file if necessary.

        The data must be provided as a (frames x channels) NumPy
        array or as one-dimensional array for mono signals.

        """
        self._check_if_closed()
        if self.mode == 'r':
            raise RuntimeError("Cannot write to file opened in read mode")

        data = _np.ascontiguousarray(data)

        self._check_frames_and_channels(data)

        ffi_type = _ffi_types[data.dtype]
        writer = getattr(_snd, 'sf_writef_' + ffi_type)
        ptr = _ffi.cast(ffi_type + '*', data.ctypes.data)
        written = writer(self._file, ptr, len(data))
        self._handle_error()
        assert written == len(data)

        curr = self.seek(0, SEEK_CUR, 'w')
        self._info.frames = self.seek(0, SEEK_END, 'w')
        self.seek(curr, SEEK_SET, 'w')

    def _check_frames_and_channels(self, data):
        """Error if data is not compatible with the shape of the sound file.

        """
        if data.dtype not in _ffi_types:
            raise ValueError("data.dtype must be one of %s" %
                             repr([dt.name for dt in _ffi_types]))

        if not data.flags.c_contiguous:
            raise ValueError("data must be c_contiguous")

        if data.ndim not in (1, 2):
            raise ValueError("data must be one- or two-dimensional")
        elif data.ndim == 1 and self.channels != 1:
            raise ValueError("data must have 2 dimensions for non-mono signals")
        elif data.ndim == 2 and data.shape[1] != self.channels:
            raise ValueError("two-dimensional data must have %i columns" %
                             self.channels)


def open(*args, **kwargs):
    """Return a new SoundFile object.

    Takes the same arguments as SoundFile.__init__().

    """
    return SoundFile(*args, **kwargs)


def read(file, frames=-1, start=None, stop=None, **kwargs):
    """Read a sound file and return its contents as NumPy array.

    The number of frames to read can be specified with frames, the
    position to start reading can be specified with start.
    By default, the whole file is read from the beginning.
    Alternatively, a range can be specified with start and stop.
    Both start and stop accept negative indices to specify positions
    relative to the end of the file.

    The keyword arguments out, dtype, fill_value, channels_first and
    always_2d are forwarded to SoundFile.read().
    All further arguments are forwarded to SoundFile.__init__().

    """
    from inspect import getargspec

    if frames >= 0 and stop is not None:
        raise RuntimeError("Only one of (frames, stop) may be used")

    read_kwargs = {}
    for arg in getargspec(SoundFile.read).args:
        if arg in kwargs:
            read_kwargs[arg] = kwargs.pop(arg)
    with SoundFile(file, 'r', **kwargs) as f:
        start, stop, _ = slice(start, stop).indices(f.frames)
        f.seek(start, SEEK_SET)
        data = f.read(frames, **read_kwargs)
    return data, f.sample_rate


def write(data, file, sample_rate, *args, **kwargs):
    """Write data from a NumPy array into a sound file.

    If file exists, it will be overwritten!

    If data is one-dimensional, a mono file is written.
    For two-dimensional data, the columns are interpreted as channels by
    default. Use channels_first=False to interpret the rows as channels.
    All further arguments are forwarded to SoundFile.__init__().

    Example usage:

        import pysoundfile as sf
        sf.write(myarray, 'myfile.wav', 44100, 'PCM_24')

    """
    data = _np.asarray(data)
    if data.ndim == 1:
        channels = 1
    else:
        channels = data.shape[1]
    with SoundFile(file, 'w', sample_rate, channels, *args, **kwargs) as f:
        f.write(data)


def default_subtype(format):
    """Return default subtype for given format."""
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
    if _snd.sf_format_check(info) == _FALSE:
        raise ValueError(
            "Invalid combination of format, subtype and endian")
    return result


def format_check(format, subtype=None, endian=None):
    """Check if the combination of format/subtype/endian is valid."""
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


def _format_info(format_int, format_flag=_GET_FORMAT_INFO):
    # Return the ID and short description of a given format.
    format_info = _ffi.new("struct SF_FORMAT_INFO*")
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
    """Return a dictionary of available major formats."""
    return dict(_available_formats_helper(_GET_FORMAT_MAJOR_COUNT,
                                          _GET_FORMAT_MAJOR))


def available_subtypes(format=None):
    """Return a dictionary of available subtypes.

    If format is specified, only compatible subtypes are returned.

    """
    subtypes = _available_formats_helper(_GET_FORMAT_SUBTYPE_COUNT,
                                         _GET_FORMAT_SUBTYPE)
    return dict((subtype, name) for subtype, name in subtypes
                if format is None or format_check(format, subtype))
