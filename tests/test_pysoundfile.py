import soundfile as sf
import numpy as np
import os
import io
import shutil
import pytest
import cffi
import sys

data_stereo = np.array([[1.0,  -1.0],
                        [0.75, -0.75],
                        [0.5,  -0.5],
                        [0.25, -0.25]])
data_mono = np.array([0, 1, 2, -2, -1], dtype='int16')

filename_stereo = 'tests/stereo.wav'
filename_mono = 'tests/mono.wav'
filename_raw = 'tests/mono.raw'
filename_new = 'tests/delme.please'


open_variants = 'name', 'fd', 'obj'


xfail_from_buffer = pytest.mark.xfail(cffi.__version_info__ < (0, 9),
                                      reason="from_buffer() since CFFI 0.9")


def _file_existing(request, filename, fdarg, objarg=None):
    if request.param == 'name':
        return filename
    elif request.param == 'fd':
        fd = os.open(filename, fdarg)

        def finalizer():
            with pytest.raises(OSError):
                os.close(fd)

        request.addfinalizer(finalizer)
        return fd
    elif request.param == 'obj':
        obj = open(filename, objarg, buffering=False)
        request.addfinalizer(obj.close)
        return obj


def _file_new(request, fdarg, objarg=None):
    filename = filename_new
    request.addfinalizer(lambda: os.remove(filename))
    return _file_existing(request, filename, fdarg, objarg)


def _file_copy(request, filename, fdarg, objarg=None):
    shutil.copy(filename, filename_new)
    request.addfinalizer(lambda: os.remove(filename_new))
    return _file_existing(request, filename_new, fdarg, objarg)


@pytest.fixture(params=open_variants)
def file_stereo_r(request):
    return _file_existing(request, filename_stereo, os.O_RDONLY, 'rb')


@pytest.fixture(params=open_variants)
def file_mono_r(request):
    return _file_existing(request, filename_mono, os.O_RDONLY, 'rb')


@pytest.fixture(params=open_variants)
def file_w(request):
    return _file_new(request, os.O_CREAT | os.O_WRONLY, 'wb')


@pytest.fixture(params=open_variants)
def file_stereo_rplus(request):
    return _file_copy(request, filename_stereo, os.O_RDWR, 'r+b')


@pytest.fixture(params=['obj'])
def file_obj_stereo_rplus(request):
    return _file_copy(request, filename_stereo, os.O_RDWR, 'r+b')


@pytest.fixture(params=['obj'])
def file_obj_w(request):
    return _file_new(request, os.O_CREAT | os.O_WRONLY, 'wb')


@pytest.fixture(params=open_variants)
def file_wplus(request):
    return _file_new(request, os.O_CREAT | os.O_RDWR, 'w+b')


@pytest.yield_fixture
def file_inmemory():
    with io.BytesIO() as f:
        yield f


@pytest.yield_fixture
def sf_stereo_r(file_stereo_r):
    with sf.SoundFile(file_stereo_r) as f:
        yield f


@pytest.yield_fixture
def sf_stereo_w(file_w):
    with sf.SoundFile(file_w, 'w', 44100, 2, format='WAV') as f:
        yield f


@pytest.yield_fixture
def sf_stereo_rplus(file_stereo_rplus):
    with sf.SoundFile(file_stereo_rplus, 'r+') as f:
        yield f


@pytest.yield_fixture
def sf_stereo_wplus(file_wplus):
    with sf.SoundFile(file_wplus, 'w+', 44100, 2,
                      format='WAV', subtype='FLOAT') as f:
        yield f


# -----------------------------------------------------------------------------
# Test read() function
# -----------------------------------------------------------------------------


def test_if_read_returns_float64_data(file_stereo_r):
    data, fs = sf.read(file_stereo_r)
    assert fs == 44100
    assert np.all(data == data_stereo)
    assert data.dtype == np.float64


def test_read_float32(file_stereo_r):
    data, fs = sf.read(file_stereo_r, dtype='float32')
    assert np.all(data == data_stereo)
    assert data.dtype == np.float32


def test_read_int16(file_mono_r):
    data, fs = sf.read(file_mono_r, dtype='int16')
    assert np.all(data == data_mono)
    assert data.dtype == np.int16


def test_read_int32(file_mono_r):
    data, fs = sf.read(file_mono_r, dtype='int32')
    assert np.all(data // 2**16 == data_mono)
    assert data.dtype == np.int32


def test_read_into_out(file_stereo_r):
    out = np.empty((3, 2), dtype='float64')
    data, fs = sf.read(file_stereo_r, out=out)
    assert data is out
    assert np.all(data == data_stereo[:3])


def test_if_read_into_malformed_out_fails(file_stereo_r):
    out = np.empty((2, 3), dtype='float64')
    with pytest.raises(ValueError):
        sf.read(file_stereo_r, out=out)


def test_if_read_into_out_with_too_many_dimensions_fails(file_stereo_r):
    out = np.empty((3, 2, 1), dtype='float64')
    with pytest.raises(ValueError):
        sf.read(file_stereo_r, out=out)


def test_if_read_into_zero_len_out_works(file_stereo_r):
    out = np.empty((0, 2), dtype='float64')
    data, fs = sf.read(file_stereo_r, out=out)
    assert data is out
    assert len(out) == 0


def test_read_into_non_contiguous_out(file_stereo_r):
    out = np.empty(data_stereo.shape[::-1], dtype='float64')
    if getattr(sys, 'pypy_version_info', (999,)) < (2, 6):
        # The test for C-contiguous doesn't work with PyPy 2.5.0
        sf.read(file_stereo_r, out=out.T)
    else:
        with pytest.raises(ValueError) as excinfo:
            sf.read(file_stereo_r, out=out.T)
        assert "C-contiguous" in str(excinfo.value)


def test_read_into_out_with_invalid_dtype(file_stereo_r):
    out = np.empty((3, 2), dtype='int64')
    with pytest.raises(TypeError) as excinfo:
        sf.read(file_stereo_r, out=out)
    assert "dtype must be one of" in str(excinfo.value)


def test_read_mono(file_mono_r):
    data, fs = sf.read(file_mono_r, dtype='int16')
    assert data.ndim == 1
    assert np.all(data == data_mono)


def test_if_read_mono_with_always2d_returns_2d_array(file_mono_r):
    data, fs = sf.read(file_mono_r, dtype='int16', always_2d=True)
    assert data.ndim == 2
    assert np.all(data == data_mono.reshape(-1, 1))


def test_read_mono_into_1d_out(file_mono_r):
    out = np.empty(len(data_mono), dtype='int16')
    data, fs = sf.read(file_mono_r, out=out)
    assert data is out
    assert np.all(data == data_mono)


def test_read_mono_into_2d_out(file_mono_r):
    out = np.empty((len(data_mono), 1), dtype='int16')
    data, fs = sf.read(file_mono_r, out=out)
    assert data is out
    assert np.all(data == data_mono.reshape(-1, 1))


def test_read_non_existing_file():
    with pytest.raises(RuntimeError) as excinfo:
        sf.read("i_do_not_exist.wav")
    assert "Error opening 'i_do_not_exist.wav'" in str(excinfo.value)


# -----------------------------------------------------------------------------
# Test write() function
# -----------------------------------------------------------------------------

# The read() function is tested above, we assume here that it is working.

@pytest.mark.parametrize("data", [data_mono, data_stereo])
def test_write_function(data, file_w):
    sf.write(file_w, data, 44100, format='WAV')
    data, fs = sf.read(filename_new, dtype='int16')
    assert fs == 44100
    assert np.all(data == data)


@pytest.mark.parametrize("filename", ["wav", ".wav", "wav.py"])
def test_write_with_unknown_extension(filename):
    with pytest.raises(TypeError) as excinfo:
        sf.write(filename, [0.0], 44100)
    assert "file extension" in str(excinfo.value)


# -----------------------------------------------------------------------------
# Test blocks() function
# -----------------------------------------------------------------------------


def assert_equal_list_of_arrays(list1, list2):
    """Helper function to assert equality of all list items."""
    for item1, item2 in zip(list1, list2):
        assert np.all(item1 == item2)


def test_blocks_without_blocksize():
    with pytest.raises(TypeError):
        list(sf.blocks(filename_stereo))


def test_blocks_full_last_block(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=2))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:2], data_stereo[2:4]])


def test_blocks_partial_last_block(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=3))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:3], data_stereo[3:4]])


def test_blocks_fill_last_block(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=3, fill_value=0))
    last_block = np.row_stack((data_stereo[3:4], np.zeros((2, 2))))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:3], last_block])


def test_blocks_with_overlap(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=3, overlap=2))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:3], data_stereo[1:4]])


def test_blocks_with_start(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=2, start=2))
    assert_equal_list_of_arrays(blocks, [data_stereo[2:4]])


def test_blocks_with_stop(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=2, stop=2))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:2]])

    with pytest.raises(TypeError):
        list(sf.blocks(filename_stereo, blocksize=2, frames=2, stop=2))


def test_blocks_with_too_large_start(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=2, start=666))
    assert_equal_list_of_arrays(blocks, [[]])


def test_blocks_with_too_large_stop(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=3, stop=666))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:3], data_stereo[3:4]])


def test_blocks_with_negative_start_and_stop(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=2, start=-2, stop=-1))
    assert_equal_list_of_arrays(blocks, [data_stereo[-2:-1]])


def test_blocks_with_stop_smaller_than_start(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=2, start=2, stop=1))
    assert blocks == []


def test_blocks_with_frames(file_stereo_r):
    blocks = list(sf.blocks(file_stereo_r, blocksize=2, frames=3))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:2], data_stereo[2:3]])


def test_blocks_with_frames_and_fill_value(file_stereo_r):
    blocks = list(
        sf.blocks(file_stereo_r, blocksize=2, frames=3, fill_value=0))
    last_block = np.row_stack((data_stereo[2:3], np.zeros((1, 2))))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:2], last_block])


def test_blocks_with_out(file_stereo_r):
    out = np.empty((3, 2))
    blocks = list(sf.blocks(file_stereo_r, out=out))
    assert blocks[0] is out
    # First frame was overwritten by second block:
    assert np.all(blocks[0] == [[0.25, -0.25], [0.75, -0.75], [0.5, -0.5]])
    assert blocks[1].base is out
    assert np.all(blocks[1] == [[0.25, -0.25]])

    with pytest.raises(TypeError):
        list(sf.blocks(filename_stereo, blocksize=3, out=out))


def test_blocks_mono():
    blocks = list(sf.blocks(filename_mono, blocksize=3, dtype='int16',
                            fill_value=0))
    assert_equal_list_of_arrays(blocks, [[0, 1, 2], [-2, -1, 0]])


def test_blocks_rplus(sf_stereo_rplus):
    blocks = list(sf_stereo_rplus.blocks(blocksize=2))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:2], data_stereo[2:4]])


def test_blocks_wplus(sf_stereo_wplus):
    """There is nothing to yield in a 'w+' file."""
    blocks = list(sf_stereo_wplus.blocks(blocksize=2, frames=666))
    assert blocks == []


def test_blocks_write(sf_stereo_w):
    with pytest.raises(RuntimeError):
        list(sf_stereo_w.blocks(blocksize=2))


# -----------------------------------------------------------------------------
# Test SoundFile.__init__()
# -----------------------------------------------------------------------------


def test_open_bytes_filename():
    with sf.SoundFile(filename_stereo.encode()) as f:
        assert np.all(f.read() == data_stereo)


def test_open_with_invalid_file():
    with pytest.raises(TypeError) as excinfo:
        sf.SoundFile(3.1415)
    assert "Invalid file" in str(excinfo.value)


def test_open_with_invalid_mode():
    with pytest.raises(TypeError) as excinfo:
        sf.SoundFile(filename_stereo, 42)
    assert "Invalid mode: 42" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        sf.SoundFile(filename_stereo, 'rr')
    assert "Invalid mode: 'rr'" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        sf.SoundFile(filename_stereo, 'rw')
    assert "exactly one of 'xrw'" in str(excinfo.value)


def test_open_with_more_invalid_arguments():
    with pytest.raises(TypeError) as excinfo:
        sf.SoundFile(filename_new, 'w', 3.1415, 2, format='WAV')
    assert "integer" in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        sf.SoundFile(filename_new, 'w', 44100, 3.1415, format='WAV')
    assert "integer" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        sf.SoundFile(filename_new, 'w', 44100, 2, format='WAF')
    assert "Unknown format" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        sf.SoundFile(filename_new, 'w', 44100, 2, 'PCM16', format='WAV')
    assert "Unknown subtype" in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        sf.SoundFile(filename_new, 'w', 44100, 2, 666, format='WAV')
    assert "Invalid subtype" in str(excinfo.value)
    with pytest.raises(ValueError) as excinfo:
        sf.SoundFile(filename_new, 'w', 44100, 2, endian='BOTH', format='WAV')
    assert "Unknown endian-ness" in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        sf.SoundFile(filename_new, 'w', 44100, 2, endian=True, format='WAV')
    assert "Invalid endian-ness" in str(excinfo.value)


def test_open_r_and_rplus_with_too_many_arguments():
    for mode in 'r', 'r+':
        with pytest.raises(TypeError) as excinfo:
            sf.SoundFile(filename_stereo, mode, samplerate=44100)
        assert "Not allowed" in str(excinfo.value)
        with pytest.raises(TypeError) as excinfo:
            sf.SoundFile(filename_stereo, mode, channels=2)
        assert "Not allowed" in str(excinfo.value)
        with pytest.raises(TypeError) as excinfo:
            sf.SoundFile(filename_stereo, mode, format='WAV')
        assert "Not allowed" in str(excinfo.value)
        with pytest.raises(TypeError) as excinfo:
            sf.SoundFile(filename_stereo, mode, subtype='FLOAT')
        assert "Not allowed" in str(excinfo.value)
        with pytest.raises(TypeError) as excinfo:
            sf.SoundFile(filename_stereo, mode, endian='FILE')
        assert "Not allowed" in str(excinfo.value)


def test_open_w_and_wplus_with_too_few_arguments():
    for mode in 'w', 'w+':
        with pytest.raises(TypeError) as excinfo:
            sf.SoundFile(filename_new, mode, samplerate=44100, channels=2)
        assert "No format specified" in str(excinfo.value)
        with pytest.raises(TypeError) as excinfo:
            sf.SoundFile(filename_new, mode, samplerate=44100, format='WAV')
        assert "channels" in str(excinfo.value)
        with pytest.raises(TypeError) as excinfo:
            sf.SoundFile(filename_new, mode, channels=2, format='WAV')
        assert "samplerate" in str(excinfo.value)


def test_open_with_mode_is_none():
    with pytest.raises(TypeError) as excinfo:
        sf.SoundFile(filename_stereo, mode=None)
    assert "Invalid mode: None" in str(excinfo.value)
    with open(filename_stereo, 'rb') as fobj:
        with sf.SoundFile(fobj, mode=None) as f:
            assert f.mode == 'rb'


def test_open_with_mode_is_x():
    with pytest.raises(OSError) as excinfo:
        sf.SoundFile(filename_stereo, 'x', 44100, 2)
    assert "exists" in str(excinfo.value)
    with pytest.raises(OSError) as excinfo:
        sf.SoundFile(filename_stereo, 'x+', 44100, 2)
    assert "exists" in str(excinfo.value)


@pytest.mark.parametrize("mode", ['w', 'w+'])
def test_if_open_with_mode_w_truncates(file_stereo_rplus, mode):
    with sf.SoundFile(file_stereo_rplus, mode, 48000, 6, format='AIFF') as f:
        pass
    with sf.SoundFile(filename_new) as f:
        if isinstance(file_stereo_rplus, str):
            assert f.samplerate == 48000
            assert f.channels == 6
            assert f.format == 'AIFF'
            assert len(f) == 0
        else:
            # This doesn't really work for file descriptors and file objects
            pass


def test_clipping_float_to_int(file_inmemory):
    float_to_clipped_int16 = [
        (-1.0 - 2**-15, -2**15    ),
        (-1.0         , -2**15    ),
        (-1.0 + 2**-15, -2**15 + 1),
        ( 0.0         ,  0        ),
        ( 1.0 - 2**-14,  2**15 - 2),
        ( 1.0 - 2**-15,  2**15 - 1),
        ( 1.0         ,  2**15 - 1),
    ]
    written, expected = zip(*float_to_clipped_int16)
    sf.write(file_inmemory, written, 44100, format='WAV', subtype='PCM_16')
    file_inmemory.seek(0)
    read, fs = sf.read(file_inmemory, dtype='int16')
    assert np.all(read == expected)
    assert fs == 44100


def test_non_clipping_float_to_float(file_inmemory):
    data = -2.0, -1.0, 0.0, 1.0, 2.0
    sf.write(file_inmemory, data, 44100, format='WAV', subtype='FLOAT')
    file_inmemory.seek(0)
    read, fs = sf.read(file_inmemory)
    assert np.all(read == data)
    assert fs == 44100


class LimitedFile(object):
    def __init__(self, file, attrs):
        for attr in attrs:
            setattr(self, attr, getattr(file, attr))


@pytest.mark.parametrize("readmethod", ['read', 'readinto'])
def test_virtual_io_readonly(file_obj_stereo_rplus, readmethod):
    limitedfile = LimitedFile(file_obj_stereo_rplus,
                              ['seek', 'tell', readmethod])
    data, fs = sf.read(limitedfile)
    assert fs == 44100
    assert np.all(data == data_stereo)


def test_virtual_io_writeonly(file_obj_w):
    limitedfile = LimitedFile(file_obj_w, ['seek', 'tell', 'write'])
    sf.write(limitedfile, [0.5], 48000, format='WAV')
    data, fs = sf.read(filename_new)
    assert fs == 48000
    assert data == [0.5]


VIRTUAL_IO_ATTRS = 'seek', 'tell', 'read', 'write'


@pytest.mark.parametrize("missing", VIRTUAL_IO_ATTRS)
def test_virtual_io_missing_attr(file_obj_stereo_rplus, missing):
    attrs = list(VIRTUAL_IO_ATTRS)
    goodfile = LimitedFile(file_obj_stereo_rplus, attrs)
    success = sf.SoundFile(goodfile, 'r+')
    attrs.remove(missing)
    badfile = LimitedFile(file_obj_stereo_rplus, attrs)
    with pytest.raises(TypeError) as excinfo:
        sf.SoundFile(badfile, 'r+')
    assert "Invalid file" in str(excinfo.value)
    assert np.all(success.read() == data_stereo)


# -----------------------------------------------------------------------------
# Test file metadata
# -----------------------------------------------------------------------------


def test_file_content(sf_stereo_r):
    assert np.all(data_stereo == sf_stereo_r.read())


def test_file_attributes_in_read_mode(sf_stereo_r):
    if isinstance(sf_stereo_r.name, str):
        assert sf_stereo_r.name == filename_stereo
    elif not isinstance(sf_stereo_r.name, int):
        assert sf_stereo_r.name.name == filename_stereo
    assert sf_stereo_r.mode == 'r'
    assert sf_stereo_r.samplerate == 44100
    assert sf_stereo_r.channels == 2
    assert sf_stereo_r.format == 'WAV'
    assert sf_stereo_r.subtype == 'FLOAT'
    assert sf_stereo_r.endian == 'FILE'
    assert sf_stereo_r.format_info == 'WAV (Microsoft)'
    assert sf_stereo_r.subtype_info == '32 bit float'
    assert sf_stereo_r.sections == 1
    assert sf_stereo_r.closed is False
    assert sf_stereo_r.seekable() is True
    assert len(sf_stereo_r) == len(data_stereo)


def test__repr__(sf_stereo_r):
    assert repr(sf_stereo_r) == ("SoundFile({0.name!r}, mode='r', "
                                 "samplerate=44100, channels=2, "
                                 "format='WAV', subtype='FLOAT', "
                                 "endian='FILE')").format(sf_stereo_r)


def test_extra_info(sf_stereo_r):
    assert 'WAVE_FORMAT_IEEE_FLOAT' in sf_stereo_r.extra_info


def test_mode_should_be_in_write_mode(sf_stereo_w):
    assert sf_stereo_w.mode == 'w'
    assert len(sf_stereo_w) == 0


def test_mode_should_be_in_readwrite_mode(sf_stereo_rplus):
    assert sf_stereo_rplus.mode == 'r+'


# -----------------------------------------------------------------------------
# Test seek/tell
# -----------------------------------------------------------------------------


def test_seek_in_read_mode(sf_stereo_r):
    assert sf_stereo_r.seek(0, sf.SEEK_CUR) == 0
    assert sf_stereo_r.tell() == 0
    assert sf_stereo_r.seek(2) == 2
    assert sf_stereo_r.tell() == 2
    assert sf_stereo_r.seek(2, sf.SEEK_CUR) == 4
    assert sf_stereo_r.seek(-2, sf.SEEK_END) == len(data_stereo) - 2
    with pytest.raises(RuntimeError):
        sf_stereo_r.seek(666)
    with pytest.raises(RuntimeError):
        sf_stereo_r.seek(-666)


def test_seek_in_write_mode(sf_stereo_w):
    assert sf_stereo_w.seek(0, sf.SEEK_CUR) == 0
    assert sf_stereo_w.tell() == 0
    assert sf_stereo_w.seek(2) == 2
    assert sf_stereo_w.tell() == 2


def test_seek_in_rplus_mode(sf_stereo_rplus):
    assert sf_stereo_rplus.seek(0, sf.SEEK_CUR) == 0
    assert sf_stereo_rplus.tell() == 0
    assert sf_stereo_rplus.seek(2) == 2
    assert sf_stereo_rplus.seek(0, sf.SEEK_CUR) == 2
    assert sf_stereo_rplus.tell() == 2


@pytest.mark.parametrize("use_default", [True, False])
def test_truncate(file_stereo_rplus, use_default):
    if isinstance(file_stereo_rplus, (str, int)):
        with sf.SoundFile(file_stereo_rplus, 'r+', closefd=False) as f:
            if use_default:
                f.seek(2)
                f.truncate()
            else:
                f.truncate(2)
            assert f.tell() == 2
            assert len(f) == 2
        if isinstance(file_stereo_rplus, int):
            os.lseek(file_stereo_rplus, 0, os.SEEK_SET)
        data, fs = sf.read(file_stereo_rplus)
        assert np.all(data == data_stereo[:2])
        assert fs == 44100
    else:
        # file objects don't support truncate()
        with sf.SoundFile(file_stereo_rplus, 'r+', closefd=False) as f:
            with pytest.raises(RuntimeError) as excinfo:
                f.truncate()
            assert "Error truncating" in str(excinfo.value)


# -----------------------------------------------------------------------------
# Test read
# -----------------------------------------------------------------------------


def test_read_write_only(sf_stereo_w):
    with pytest.raises(RuntimeError):
        sf_stereo_w.read(2)


def test_read_should_read_data_and_advance_read_pointer(sf_stereo_r):
    data = sf_stereo_r.read(2)
    assert np.all(data == data_stereo[:2])
    assert sf_stereo_r.seek(0, sf.SEEK_CUR) == 2


def test_read_n_frames_should_return_n_frames(sf_stereo_r):
    assert len(sf_stereo_r.read(2)) == 2


def test_read_all_frames_should_read_all_remaining_frames(sf_stereo_r):
    sf_stereo_r.seek(-2, sf.SEEK_END)
    assert np.all(sf_stereo_r.read() == data_stereo[-2:])


def test_read_over_end_should_return_only_remaining_frames(sf_stereo_r):
    sf_stereo_r.seek(-2, sf.SEEK_END)
    assert np.all(sf_stereo_r.read(4) == data_stereo[-2:])


def test_read_over_end_with_fill_should_reaturn_asked_frames(sf_stereo_r):
    sf_stereo_r.seek(-2, sf.SEEK_END)
    data = sf_stereo_r.read(4, fill_value=0)
    assert np.all(data[:2] == data_stereo[-2:])
    assert np.all(data[2:] == 0)
    assert len(data) == 4


def test_read_into_out_over_end_should_return_shorter_data_and_write_into_out(
        sf_stereo_r):
    out = np.ones((4, sf_stereo_r.channels), dtype='float64')
    sf_stereo_r.seek(-2, sf.SEEK_END)
    data = sf_stereo_r.read(out=out)
    assert np.all(data[:2] == out[:2])
    assert np.all(data[2:] == 1)
    assert out.shape == (4, sf_stereo_r.channels)
    assert data.shape == (2, sf_stereo_r.channels)


def test_read_into_out_over_end_with_fill_should_return_full_data_and_write_into_out(
        sf_stereo_r):
    out = np.ones((4, sf_stereo_r.channels), dtype='float64')
    sf_stereo_r.seek(-2, sf.SEEK_END)
    data = sf_stereo_r.read(out=out, fill_value=0)
    assert np.all(data == out)
    assert np.all(data[2:] == 0)
    assert out.shape == (4, sf_stereo_r.channels)


# -----------------------------------------------------------------------------
# Test buffer read
# -----------------------------------------------------------------------------


def test_buffer_read(sf_stereo_r):
    buf = sf_stereo_r.buffer_read(2)
    assert len(buf) == 2 * 2 * 8
    assert sf_stereo_r.seek(0, sf.SEEK_CUR) == 2
    data = np.frombuffer(buf, dtype='float64').reshape(-1, 2)
    assert np.all(data == data_stereo[:2])
    buf = sf_stereo_r.buffer_read(ctype='float')
    assert len(buf) == 2 * 2 * 4
    assert sf_stereo_r.seek(0, sf.SEEK_CUR) == 4
    data = np.frombuffer(buf, dtype='float32').reshape(-1, 2)
    assert np.all(data == data_stereo[2:])
    buf = sf_stereo_r.buffer_read()
    assert len(buf) == 0
    buf = sf_stereo_r.buffer_read(666)
    assert len(buf) == 0
    with pytest.raises(ValueError) as excinfo:
        sf_stereo_r.buffer_read(ctype='char')
    assert "Unsupported data type" in str(excinfo.value)


@xfail_from_buffer
def test_buffer_read_into(sf_stereo_r):
    out = np.ones((3, 2))
    frames = sf_stereo_r.buffer_read_into(out)
    assert frames == 3
    assert np.all(out == data_stereo[:3])
    assert sf_stereo_r.seek(0, sf.SEEK_CUR) == 3
    frames = sf_stereo_r.buffer_read_into(out)
    assert frames == 1
    assert np.all(out[:1] == data_stereo[3:])
    assert sf_stereo_r.seek(0, sf.SEEK_CUR) == 4


# -----------------------------------------------------------------------------
# Test write
# -----------------------------------------------------------------------------


def test_write_to_read_only_file_should_fail(sf_stereo_r):
    with pytest.raises(RuntimeError):
        sf_stereo_r.write(data_stereo)


def test_if_write_advances_write_pointer(sf_stereo_w):
    position = sf_stereo_w.seek(0, sf.SEEK_CUR)
    sf_stereo_w.write(data_stereo)
    assert sf_stereo_w.seek(0, sf.SEEK_CUR) == position + len(data_stereo)


def test_write_flush_should_write_to_disk(sf_stereo_w):
    sf_stereo_w.flush()
    size = os.path.getsize(filename_new)
    sf_stereo_w.write(data_stereo)
    sf_stereo_w.flush()
    assert os.path.getsize(filename_new) == size + data_stereo.size * 2


def test_wplus_read_written_data(sf_stereo_wplus):
    sf_stereo_wplus.write(data_stereo)
    assert sf_stereo_wplus.seek(0, sf.SEEK_CUR) == len(data_stereo)
    sf_stereo_wplus.seek(0)
    assert np.all(sf_stereo_wplus.read() == data_stereo)
    assert sf_stereo_wplus.seek(0, sf.SEEK_CUR) == len(data_stereo)
    sf_stereo_wplus.close()
    data, fs = sf.read(filename_new)
    assert np.all(data == data_stereo)


def test_rplus_append_data(sf_stereo_rplus):
    sf_stereo_rplus.seek(0, sf.SEEK_END)
    sf_stereo_rplus.write(data_stereo / 2)
    sf_stereo_rplus.close()
    data, fs = sf.read(filename_new)
    assert np.all(data[:len(data_stereo)] == data_stereo)
    assert np.all(data[len(data_stereo):] == data_stereo / 2)


# -----------------------------------------------------------------------------
# Test buffer write
# -----------------------------------------------------------------------------


@xfail_from_buffer
def test_buffer_write(sf_stereo_w):
    buf = np.array([[1, 2], [-1, -2]], dtype='int16')
    sf_stereo_w.buffer_write(buf, 'short')
    sf_stereo_w.close()
    data, fs = sf.read(filename_new, dtype='int16')
    assert np.all(data == buf)
    assert fs == 44100


def test_buffer_write_with_bytes(sf_stereo_w):
    b = b"\x01\x00\xFF\xFF\xFF\x00\x00\xFF"
    sf_stereo_w.buffer_write(b, 'short')
    sf_stereo_w.close()
    data, fs = sf.read(filename_new, dtype='int16')
    assert np.all(data == [[1, -1], [255, -256]])
    assert fs == 44100


@xfail_from_buffer
def test_buffer_write_with_wrong_size(sf_stereo_w):
    buf = np.array([1, 2, 3], dtype='int16')
    with pytest.raises(ValueError) as excinfo:
        sf_stereo_w.buffer_write(buf, 'short')
    assert "multiple of frame size" in str(excinfo.value)


# -----------------------------------------------------------------------------
# Other tests
# -----------------------------------------------------------------------------


def test_context_manager_should_open_and_close_file(file_stereo_r):
    with sf.SoundFile(file_stereo_r) as f:
        assert not f.closed
    assert f.closed


def test_closing_should_close_file(file_stereo_r):
    f = sf.SoundFile(file_stereo_r)
    assert not f.closed
    f.close()
    assert f.closed


def test_anything_on_closed_file(file_stereo_r):
    with sf.SoundFile(file_stereo_r) as f:
        pass
    with pytest.raises(RuntimeError) as excinfo:
        f.seek(0)
    assert "closed" in str(excinfo.value)


def test_file_attributes_should_save_to_disk(file_w):
    with sf.SoundFile(file_w, 'w', 44100, 2, format='WAV') as f:
        f.title = 'testing'
    with sf.SoundFile(filename_new) as f:
        assert f.title == 'testing'


def test_non_file_attributes_should_not_save_to_disk(file_w):
    with sf.SoundFile(file_w, 'w', 44100, 2, format='WAV') as f:
        f.foobar = 'testing'
    with sf.SoundFile(filename_new) as f:
        with pytest.raises(AttributeError):
            f.foobar


def test_getAttributeNames(sf_stereo_r):
    names = sf_stereo_r._getAttributeNames()
    assert 'artist' in names
    assert 'genre' in names


# -----------------------------------------------------------------------------
# RAW tests
# -----------------------------------------------------------------------------


def test_read_raw_files_should_read_data():
    with sf.SoundFile(filename_raw, 'r', 44100, 1, 'PCM_16') as f:
        assert np.all(f.read(dtype='int16') == data_mono)


def test_read_raw_files_with_too_few_arguments_should_fail():
    with pytest.raises(TypeError):  # missing everything
        sf.SoundFile(filename_raw)
    with pytest.raises(TypeError):  # missing subtype
        sf.SoundFile(filename_raw, samplerate=44100, channels=2)
    with pytest.raises(TypeError):  # missing channels
        sf.SoundFile(filename_raw, samplerate=44100, subtype='PCM_16')
    with pytest.raises(TypeError):  # missing samplerate
        sf.SoundFile(filename_raw, channels=2, subtype='PCM_16')


def test_available_formats():
    formats = sf.available_formats()
    assert 'WAV' in formats
    assert 'OGG' in formats
    assert 'FLAC' in formats


def test_available_subtypes():
    subtypes = sf.available_subtypes()
    assert 'PCM_24' in subtypes
    assert 'FLOAT' in subtypes
    assert 'VORBIS' in subtypes
    subtypes = sf.available_subtypes('WAV')
    assert 'PCM_24' in subtypes
    assert 'FLOAT' in subtypes
    assert 'VORBIS' not in subtypes
    subtypes = sf.available_subtypes('nonsense')
    assert subtypes == {}


def test_default_subtype():
    assert sf.default_subtype('FLAC') == 'PCM_16'
    assert sf.default_subtype('RAW') is None
    with pytest.raises(ValueError) as excinfo:
        sf.default_subtype('nonsense')
    assert str(excinfo.value) == "Unknown format: 'nonsense'"
    with pytest.raises(TypeError) as excinfo:
        sf.default_subtype(666)
    assert str(excinfo.value) == "Invalid format: 666"


# -----------------------------------------------------------------------------
# Test non-seekable files
# -----------------------------------------------------------------------------


def test_write_non_seekable_file(file_w):
    with sf.SoundFile(file_w, 'w', 44100, 1, format='XI') as f:
        assert not f.seekable()
        assert len(f) == 0
        f.write(data_mono)
        assert len(f) == len(data_mono)

        with pytest.raises(RuntimeError) as excinfo:
            f.seek(2)
        assert "unseekable" in str(excinfo.value)

    with sf.SoundFile(filename_new) as f:
        assert not f.seekable()
        assert len(f) == len(data_mono)
        data = f.read(3, dtype='int16')
        assert np.all(data == data_mono[:3])
        data = f.read(666, dtype='int16')
        assert np.all(data == data_mono[3:])

        with pytest.raises(RuntimeError) as excinfo:
            f.seek(2)
        assert "unseekable" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            f.read()
        assert "frames" in str(excinfo.value)

        with pytest.raises(ValueError) as excinfo:
            list(f.blocks(blocksize=3, overlap=1))
        assert "overlap" in str(excinfo.value)

    data, fs = sf.read(filename_new, dtype='int16')
    assert np.all(data == data_mono)
    assert fs == 44100

    with pytest.raises(ValueError) as excinfo:
        sf.read(filename_new, start=3)
    assert "start is only allowed for seekable files" in str(excinfo.value)
