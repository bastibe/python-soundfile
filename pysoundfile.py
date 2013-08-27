from cffi import FFI
import numpy as np
import sys

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
samplerate, a number of channels, and a file format. These can not be
changed at runtime.

A SoundFile has methods for reading and writing data to/from the file.
Even though every sound file has a fixed file format, reading and
writing is possible in four different NumPy formats: int16, int32,
float32 and float64.

At the same time, SoundFiles act as container types, so you can use
slices to read or write data as well. Since there is no way of
specifying data formats for slices, the SoundFile will always return
float32 data for those.

PySoundFile is BSD licensed.
(c) 2013, Bastian Bechtold

"""

ffi = FFI()
ffi.cdef("""
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
""")

read_mode = 0x10
write_mode = 0x20
read_write_mode = 0x30

snd_types = {
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
    'RF64':  0x220000  # RF64 WAV file
}

snd_subtypes = {
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

snd_endians = {
    'FILE':   0x00000000, # Default file endian-ness.
    'LITTLE': 0x10000000, # Force little endian-ness.
    'BIG':    0x20000000, # Force big endian-ness.
    'CPU':    0x30000000, # Force CPU endian-ness.
}

wave_file = snd_types['WAV']|snd_subtypes['PCM_16']|snd_endians['FILE']
flac_file = snd_types['FLAC']|snd_subtypes['FLOAT']|snd_endians['FILE']
matlab_file = snd_types['MAT5']|snd_subtypes['DOUBLE']|snd_endians['FILE']
ogg_file = snd_types['OGG']|snd_subtypes['VORBIS']|snd_endians['FILE']

def _decodeformat(format):
    sub_mask  = 0x0000FFFF
    type_mask = 0x0FFF0000
    end_mask  = 0x30000000

    def reverse_dict(d): return {value:key for key, value in d.items()}

    type = reverse_dict(snd_types)[format & type_mask]
    subtype = reverse_dict(snd_subtypes)[format & sub_mask]
    endianness = reverse_dict(snd_endians)[format & end_mask]

    return (type, subtype, endianness)

_snd = ffi.dlopen('sndfile')

class SoundFile(object):

    """SoundFile handles reading and writing to sound files.

    Each SoundFile opens one sound file on the disk. This sound file
    has a specific samplerate, data format and a set number of
    channels. Each sound file can be opened in read_mode, write_mode,
    or read_write_mode. Note that read_write_mode is unsupported for
    some formats.

    Data can be written to the file using write(), or read from the
    file using read(). Every read and write operation starts at a
    certain position in the file. Reading N frames will change this
    position by N frames as well. Alternatively, seek(), seek_start(),
    and seek_end() can be used to set the current position to a frame
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

    def __init__(self, name, samplerate=0, channels=0, format=0,
                 file_mode=read_write_mode):
        """Open a new SoundFile.

        If a file is only opened in read_mode or in read_write_mode,
        no samplerate, channels or file format need to be given. If a
        file is opened in write_mode, you must provide a samplerate, a
        number of channels, and a file format. An exception is the RAW
        data format, which requires these data points for reading as
        well.

        File formats consist of three parts OR'ed together:
        - one of the file types from snd_types
        - one of the data types from snd_subtypes
        - an endianness from snd_endians

        Since this is somewhat burdensome if you have to do it for
        every new file, you can use one of the commonly used
        pre-defined types wave_file, flac_file, matlab_file or
        ogg_file.

        """
        info = ffi.new("SF_INFO*")
        info.samplerate = samplerate
        info.channels = channels
        info.format = format
        filename = ffi.new('char[]', name.encode())
        self._file_mode = file_mode

        self._file = _snd.sf_open(filename, self._file_mode, info)
        self._handle_error()

        self.frames = info.frames
        self.samplerate = info.samplerate
        self.channels = info.channels
        self.format = _decodeformat(info.format)
        self.sections = info.sections
        self.seekable = info.seekable == 1

    def __del__(self):
        # be sure to flush data to disk before closing the file
        _snd.sf_write_sync(self._file)
        err = _snd.sf_close(self._file)
        self._handle_error_number(err)

    def _handle_error(self):
        # this checks the error flag of the SNDFILE* structure
        err = _snd.sf_error(self._file)
        self._handle_error_number(err)

    def _handle_error_number(self, err):
        # pretty-print a numerical error code
        if err != 0:
            err_str = _snd.sf_error_number(err)
            raise RuntimeError(ffi.string(err_str).decode())

    # these strings are used as properties to access text data n the
    # sound file
    _snd_strings = {
        'title': 0x01,
        'copyright': 0x02,
        'software': 0x03,
        'artist': 0x04,
        'comment': 0x05,
        'date': 0x06,
        'album': 0x07,
        'license': 0x08,
        'tracknumber': 0x09,
        'genre': 0x10
    }

    def __setattr__(self, name, value):
        # access text data in the sound file through properties
        if name in self._snd_strings:
            if self._file_mode == read_mode:
                raise RuntimeError("Can not change %s of file in read mode" %
                                   name)
            data = ffi.new('char[]', value.encode())
            err = _snd.sf_set_string(self._file, self._snd_strings[name], data)
            self._handle_error_number(err)
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        # access text data in the sound file through properties
        if name in self._snd_strings:
            data = _snd.sf_get_string(self._file, self._snd_strings[name])
            if data == ffi.NULL:
                return ""
            else:
                return ffi.string(data).decode()
        else:
            raise AttributeError("SoundFile has no attribute %s" % name)

    def __len__(self):
        # strangely, the only way to see the length of a file seems to
        # be to seek to the end. Returns the number of frames in the
        # file.
        curr = self.seek(0)
        length = self.seek_end(0)
        self.seek(curr)
        return(length)

    def __getitem__(self, frame):
        # access the file as if it where a one-dimensional Numpy
        # array. Data must be in the form (frames x channels).
        # Both open slice bounds and negative values are allowed.
        if not isinstance(frame, slice):
            frame = slice(frame, frame+1)
        if frame.start is None:
            frame = slice(0, frame.stop)
        if frame.stop is None:
            frame = slice(frame.start, len(self))
        if frame.start < 0:
            frame = slice(len(self)+frame.start, frame.stop)
        if frame.stop < 0:
            frame = slice(frame.start, len(self)+frame.stop)
        curr = self.seek(0)
        self.seek_start(frame.start)
        data = self.read(frame.stop-frame.start)
        self.seek(curr)
        return data

    def __setitem__(self, frame, data):
        # access the file as if it where a one-dimensional Numpy
        # array. Data must be in the form (frames x channels).
        # Both open slice bounds and negative values are allowed.
        if self._file_mode == read_mode:
            raise RuntimeError("Can not write to read-only file")
        if not isinstance(frame, slice):
            frame = slice(frame, frame+1)
        if frame.start is None:
            frame = slice(0, frame.stop)
        if frame.stop is None:
            frame = slice(frame.start, len(self))
        if frame.start < 0:
            frame = slice(len(self)+frame.start, frame.stop)
        if frame.stop < 0:
            frame = slice(frame.start, len(self)+frame.stop)
        if frame.stop-frame.start != len(data):
            raise IndexError(
                "Could not fit data of length %i into slice of length %i" %
                (len(data), frame.stop-frame.start))
        curr = self.seek(0)
        self.seek_start(frame.start)
        self.write(data)
        self.seek(curr)
        return data

    def seek(self, frames):
        """Set the read position relative to the current position.

        Positive values will fast-forward. Negative values will rewind.

        Returns the new absolute read position in frames.
        """
        return _snd.sf_seek(self._file, frames, 1)

    def seek_absolute(self, frames):
        """Set an absolute read position.

        Positive values will set the read position to the given frame
        index. Negative values will set the read position to the given
        index counted from the end of the file.

        Returns the new absolute read position in frames.
        """
        if frames >= 0:
            return _snd.sf_seek(self._file, frames, 0)
        else:
            return _snd.sf_seek(self._file, frames, 2)

    def read(self, frames, format=np.float32):
        """Read a number of frames from the file.

        Reads the given number of frames in the given data format from
        the current read position. This also advances the read
        position by the same number of frames.

        Returns the read data as a (frames x channels) NumPy array.

        If there is not enough data left in the file to read, a
        smaller NumPy array will be returned.

        """
        formats = {
            np.float64: 'double[]',
            np.float32: 'float[]',
            np.int32: 'int[]',
            np.int16: 'short[]'
        }
        readers = {
            np.float64: _snd.sf_readf_double,
            np.float32: _snd.sf_readf_float,
            np.int32: _snd.sf_readf_int,
            np.int16: _snd.sf_readf_short
        }
        if format not in formats:
            raise ValueError("Can only read int16, int32, float32 and float64")
        data = ffi.new(formats[format], frames*self.channels)
        read = readers[format](self._file, data, frames)
        self._handle_error()
        np_data = np.fromstring(ffi.buffer(data), dtype=format,
                                count=read*self.channels)
        return np.reshape(np_data, (read, self.channels))

    def write(self, data):
        """Write a number of frames to the file.

        Writes a number of frames to the current read position in the
        file. This also advances the read position by the same number
        of frames and enlarges the file if necessary.

        The data must be provided as a (frames x channels) NumPy
        array.

        """
        if self._file_mode == read_mode:
            raise RuntimeError("Can not write to read-only file")
        formats = {
            np.dtype(np.float64): 'double*',
            np.dtype(np.float32): 'float*',
            np.dtype(np.int32): 'int*',
            np.dtype(np.int16): 'short*'
        }
        writers = {
            np.dtype(np.float64): _snd.sf_writef_double,
            np.dtype(np.float32): _snd.sf_writef_float,
            np.dtype(np.int32): _snd.sf_writef_int,
            np.dtype(np.int16): _snd.sf_writef_short
        }
        if data.dtype not in writers:
            raise ValueError("Data must be int16, int32, float32 or float64")
        raw_data = ffi.new('char[]', data.flatten().tostring())
        written = writers[data.dtype](self._file,
                                      ffi.cast(formats[data.dtype], raw_data),
                                      len(data))
        self._handle_error()
        return written
