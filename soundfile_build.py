import os
import sys
from cffi import FFI

ffibuilder = FFI()
ffibuilder.set_source("_soundfile", None)
ffibuilder.cdef("""
enum
{
    SF_FORMAT_SUBMASK       = 0x0000FFFF,
    SF_FORMAT_TYPEMASK      = 0x0FFF0000,
    SF_FORMAT_ENDMASK       = 0x30000000
} ;

enum
{
    SFC_GET_LIB_VERSION             = 0x1000,
    SFC_GET_LOG_INFO                = 0x1001,
    SFC_GET_FORMAT_INFO             = 0x1028,

    SFC_GET_FORMAT_MAJOR_COUNT      = 0x1030,
    SFC_GET_FORMAT_MAJOR            = 0x1031,
    SFC_GET_FORMAT_SUBTYPE_COUNT    = 0x1032,
    SFC_GET_FORMAT_SUBTYPE          = 0x1033,
    SFC_FILE_TRUNCATE               = 0x1080,
    SFC_SET_CLIPPING                = 0x10C0,

    SFC_SET_SCALE_FLOAT_INT_READ    = 0x1014,
    SFC_SET_SCALE_INT_FLOAT_WRITE   = 0x1015,
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

/* Note: Data ptr argument types are declared as void* here in order to
         avoid an implicit cast warning. (gh183). */
sf_count_t  sf_readf_short   (SNDFILE *sndfile, void *ptr, sf_count_t frames) ;
sf_count_t  sf_readf_int     (SNDFILE *sndfile, void *ptr, sf_count_t frames) ;
sf_count_t  sf_readf_float   (SNDFILE *sndfile, void *ptr, sf_count_t frames) ;
sf_count_t  sf_readf_double  (SNDFILE *sndfile, void *ptr, sf_count_t frames) ;

sf_count_t  sf_write_short   (SNDFILE *sndfile, short *ptr, sf_count_t items) ;
sf_count_t  sf_write_int     (SNDFILE *sndfile, int *ptr, sf_count_t items) ;
sf_count_t  sf_write_float   (SNDFILE *sndfile, float *ptr, sf_count_t items) ;
sf_count_t  sf_write_double  (SNDFILE *sndfile, double *ptr, sf_count_t items) ;

/* Note: The argument types were changed to void* in order to allow
         writing bytes in SoundFile.buffer_write() */
sf_count_t  sf_writef_short  (SNDFILE *sndfile, void *ptr, sf_count_t frames) ;
sf_count_t  sf_writef_int    (SNDFILE *sndfile, void *ptr, sf_count_t frames) ;
sf_count_t  sf_writef_float  (SNDFILE *sndfile, void *ptr, sf_count_t frames) ;
sf_count_t  sf_writef_double (SNDFILE *sndfile, void *ptr, sf_count_t frames) ;

sf_count_t  sf_read_raw      (SNDFILE *sndfile, void *ptr, sf_count_t bytes) ;
sf_count_t  sf_write_raw     (SNDFILE *sndfile, void *ptr, sf_count_t bytes) ;

const char* sf_get_string    (SNDFILE *sndfile, int str_type) ;
int         sf_set_string    (SNDFILE *sndfile, int str_type, const char* str) ;
const char * sf_version_string (void) ;

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

platform = os.environ.get('PYSOUNDFILE_PLATFORM', sys.platform)
if platform == 'win32':
    ffibuilder.cdef("""
    SNDFILE* sf_wchar_open (const wchar_t *wpath, int mode, SF_INFO *sfinfo) ;
    """)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
