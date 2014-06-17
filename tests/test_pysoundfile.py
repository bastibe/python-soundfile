import pysoundfile as sf
import numpy as np
import os
import shutil
import pytest

data_stereo = np.array([[1.0,  -1.0],
                        [0.75, -0.75],
                        [0.5,  -0.5],
                        [0.25, -0.25]])
data_mono = np.array([[0], [1], [2], [-2], [-1]], dtype='int16')

filename_stereo = 'tests/stereo.wav'
filename_mono = 'tests/mono.wav'
filename_raw = 'tests/mono.raw'
filename_new = 'tests/new.wav'
tempfilename = 'tests/delme.please'


open_variants = 'name', 'fd', 'obj'


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
        obj = open(filename, objarg)
        request.addfinalizer(obj.close)
        return obj


def _file_new(request, fdarg, objarg=None):
    filename = filename_new
    request.addfinalizer(lambda: os.remove(filename))
    return _file_existing(request, filename, fdarg, objarg)


def _file_copy(request, filename, fdarg, objarg=None):
    shutil.copy(filename, tempfilename)
    request.addfinalizer(lambda: os.remove(tempfilename))
    return _file_existing(request, tempfilename, fdarg, objarg)


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
def file_stereo_rw_existing(request):
    return _file_copy(request, filename_stereo, os.O_RDWR, 'r+b')


@pytest.fixture(params=open_variants)
def file_rw_new(request):
    return _file_new(request, os.O_CREAT | os.O_RDWR, 'w+b')


@pytest.yield_fixture
def sf_stereo_r(file_stereo_r):
    with sf.open(file_stereo_r) as f:
        yield f


@pytest.yield_fixture
def sf_stereo_w(file_w):
    with sf.open(file_w, 'w', 44100, 2, format='WAV') as f:
        yield f


@pytest.yield_fixture
def sf_stereo_rw_existing(file_stereo_rw_existing):
    with sf.open(file_stereo_rw_existing, 'rw') as f:
        yield f


@pytest.yield_fixture
def sf_stereo_rw_new(file_rw_new):
    with sf.open(file_rw_new, 'rw', 44100, 2,
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
    assert np.all(data == data_mono * 2 ** 16)
    assert data.dtype == np.int32


def test_read_into_out(file_stereo_r):
    out = np.empty((3, 2), dtype='float64')
    data, fs = sf.read(file_stereo_r, out=out)
    assert data is out
    assert np.all(data == data_stereo[:3])


def test_if_read_into_malformed_out_fails(file_stereo_r):
    out = np.empty((2, 3), dtype='float64')
    with pytest.raises(ValueError):
        data, fs = sf.read(file_stereo_r, out=out)


def test_if_read_into_out_with_too_many_dimensions_fails(file_stereo_r):
    out = np.empty((3, 2, 1), dtype='float64')
    with pytest.raises(ValueError):
        data, fs = sf.read(file_stereo_r, out=out)


def test_if_read_into_zero_len_out_works(file_stereo_r):
    out = np.empty((0, 2), dtype='float64')
    data, fs = sf.read(file_stereo_r, out=out)
    assert data is out
    assert len(out) == 0


def test_read_mono_without_always2d(file_mono_r):
    data, fs = sf.read(file_mono_r, dtype='int16', always_2d=False)
    assert data.ndim == 1
    assert np.all(data == data_mono.squeeze())


def test_if_read_mono_returns_2d_array(file_mono_r):
    data, fs = sf.read(file_mono_r, dtype='int16')
    assert data.ndim == 2
    assert np.all(data == data_mono)


def test_read_mono_into_1d_out(file_mono_r):
    out = np.empty(len(data_mono), dtype='int16')
    data, fs = sf.read(file_mono_r, out=out)
    assert data is out
    assert np.all(data == data_mono.squeeze())


def test_read_mono_into_2d_out(file_mono_r):
    out = np.empty((len(data_mono), 1), dtype='int16')
    data, fs = sf.read(file_mono_r, out=out)
    assert data is out
    assert np.all(data == data_mono)


# -----------------------------------------------------------------------------
# Test write() function
# -----------------------------------------------------------------------------

# The read() function is tested above, we assume here that it is working.

def test_write_function(file_w):
    sf.write(data_mono, file_w, 44100, format='WAV')
    data, fs = sf.read(filename_new, dtype='int16')
    assert fs == 44100
    assert np.all(data == data_mono)


# -----------------------------------------------------------------------------
# Test blocks() function
# -----------------------------------------------------------------------------


def assert_equal_list_of_arrays(list1, list2):
    """Helper function to assert equality of all list items."""
    for item1, item2 in zip(list1, list2):
        assert np.all(item1 == item2)


def test_blocks_full_last_block():
    blocks = list(sf.blocks(filename_stereo, blocksize=2))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:2], data_stereo[2:4]])


def test_blocks_partial_last_block():
    blocks = list(sf.blocks(filename_stereo, blocksize=3))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:3], data_stereo[3:4]])


def test_blocks_fill_last_block():
    blocks = list(sf.blocks(filename_stereo, blocksize=3, fill_value=0))
    last_block = np.row_stack((data_stereo[3:4], np.zeros((2, 2))))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:3], last_block])


def test_blocks_with_overlap():
    blocks = list(sf.blocks(filename_stereo, blocksize=3, overlap=2))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:3], data_stereo[1:4]])


def test_blocks_with_start():
    blocks = list(sf.blocks(filename_stereo, blocksize=2, start=2))
    assert_equal_list_of_arrays(blocks, [data_stereo[2:4]])


def test_blocks_with_stop():
    blocks = list(sf.blocks(filename_stereo, blocksize=2, stop=2))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:2]])

    with pytest.raises(TypeError):
        list(sf.blocks(filename_stereo, blocksize=2, frames=2, stop=2))


def test_blocks_with_too_large_start():
    blocks = list(sf.blocks(filename_stereo, start=666))
    assert_equal_list_of_arrays(blocks, [[]])


def test_blocks_with_too_large_stop():
    blocks = list(sf.blocks(filename_stereo, blocksize=3, stop=666))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:3], data_stereo[3:4]])


def test_blocks_with_negative_start_and_stop():
    blocks = list(sf.blocks(filename_stereo, blocksize=2, start=-2, stop=-1))
    assert_equal_list_of_arrays(blocks, [data_stereo[-2:-1]])


def test_blocks_with_stop_smaller_than_start():
    blocks = list(sf.blocks(filename_stereo, blocksize=2, start=2, stop=1))
    assert blocks == []


def test_blocks_with_frames():
    blocks = list(sf.blocks(filename_stereo, blocksize=2, frames=3))
    assert_equal_list_of_arrays(blocks, [data_stereo[0:2], data_stereo[2:3]])


def test_blocks_with_out():
    out = np.empty((3, 2))
    blocks = list(sf.blocks(filename_stereo, out=out))
    assert blocks[0] is out
    # First frame was overwritten by second block:
    assert np.all(blocks[0] == [[0.25, -0.25], [0.75, -0.75], [0.5, -0.5]])
    assert blocks[1].base is out
    assert np.all(blocks[1] == [[0.25, -0.25]])

    with pytest.raises(TypeError):
        list(sf.blocks(filename_stereo, blocksize=3, out=out))


def test_blocks_mono():
    blocks = list(sf.blocks(filename_mono, blocksize=3, dtype='int16',
                            always_2d=False, fill_value=0))
    assert_equal_list_of_arrays(blocks, [[0, 1, 2], [-2, -1, 0]])


def test_blocks_write_interrupted(file_w):
    for block in sf.blocks(file_w, 'w', 44100, 2, blocksize=len(data_stereo),
                           format='WAV', subtype='FLOAT'):
        block[:] = data_stereo
        break  # Raises GeneratorExit
    data, fs = sf.read(filename_new)
    assert fs == 44100
    assert np.all(data == data_stereo)


def test_blocks_write_partial_last_block(file_w):
    for i, block in enumerate(
        sf.blocks(file_w, 'w', 44100, 2, blocksize=3,
                  format='WAV', subtype='FLOAT', frames=len(data_stereo))):
        if i == 0:
            block[:] = data_stereo[0:3]
        else:
            block[:] = data_stereo[3:4]
    data, fs = sf.read(filename_new)
    assert fs == 44100
    assert np.all(data == data_stereo)


def test_blocks_write_with_start(file_w):
    with pytest.raises(TypeError):
        list(sf.blocks(file_w, 'w', 44100, 2, blocksize=3,
                       format='WAV', subtype='FLOAT', start=1))


def test_blocks_write_with_stop(file_w):
    with pytest.raises(TypeError):
        list(sf.blocks(file_w, 'w', 44100, 2, blocksize=3,
                       format='WAV', subtype='FLOAT', stop=1))


def test_blocks_rw_existing(file_stereo_rw_existing):
    for block in sf.blocks(file_stereo_rw_existing, 'rw', blocksize=3):
        block[:] = block / 2

    data, fs = sf.read(tempfilename)
    assert fs == 44100
    assert np.all(data == data_stereo / 2)


def test_blocks_rw_existing_with_start_and_stop(file_stereo_rw_existing):
    for block in sf.blocks(file_stereo_rw_existing, 'rw', blocksize=2,
                           start=1, stop=-1):
        block[:] = block / 2

    data, fs = sf.read(tempfilename)
    assert fs == 44100
    assert np.all(data[:1] == data_stereo[:1])
    assert np.all(data[1:-1] == data_stereo[1:-1] / 2)
    assert np.all(data[-1:] == data_stereo[-1:])


def test_blocks_rw_overlap(file_stereo_rw_existing):
    with pytest.raises(TypeError):
        list(sf.blocks(file_stereo_rw_existing, 'rw', blocksize=3, overlap=1))


def test_blocks_rw_new(file_rw_new):
    """There is nothing to yield in a new 'rw' file."""
    blocks = list(sf.blocks(file_rw_new, 'rw', 44100, 2, format='WAV',
                            blocksize=2, frames=666))
    assert blocks == []


# -----------------------------------------------------------------------------
# Test file metadata
# -----------------------------------------------------------------------------


def test_file_content(sf_stereo_r):
    assert np.all(data_stereo == sf_stereo_r[:])


def test_file_attributes_in_read_mode(sf_stereo_r):
    assert sf_stereo_r.mode == 'r'
    assert sf_stereo_r.channels == 2
    assert sf_stereo_r.sample_rate == 44100
    assert sf_stereo_r.format == 'WAV'
    assert sf_stereo_r.subtype == 'FLOAT'
    assert sf_stereo_r.endian == 'FILE'
    assert sf_stereo_r.format_info == 'WAV (Microsoft)'
    assert sf_stereo_r.subtype_info == '32 bit float'
    assert len(sf_stereo_r) == len(data_stereo)


def test_mode_should_be_in_write_mode(sf_stereo_w):
    assert sf_stereo_w.mode == 'w'
    assert len(sf_stereo_w) == 0


def test_mode_should_be_in_readwrite_mode(sf_stereo_rw_existing):
    assert sf_stereo_rw_existing.mode == 'rw'


# -----------------------------------------------------------------------------
# Test seek
# -----------------------------------------------------------------------------


def test_seek_in_read_mode(sf_stereo_r):
    assert sf_stereo_r.seek(0, sf.SEEK_CUR) == 0
    assert sf_stereo_r.seek(2) == 2
    assert sf_stereo_r.seek(2, sf.SEEK_CUR) == 4
    assert sf_stereo_r.seek(-2, sf.SEEK_END) == len(data_stereo) - 2
    assert sf_stereo_r.seek(2, which='r') == 2
    assert sf_stereo_r.seek(666) == -1
    assert sf_stereo_r.seek(-666) == -1
    with pytest.raises(ValueError):
        sf_stereo_r.seek(2, which='w')


def test_seek_in_write_mode(sf_stereo_w):
    assert sf_stereo_w.seek(0, sf.SEEK_CUR) == 0
    assert sf_stereo_w.seek(2, which='w') == 2
    with pytest.raises(ValueError):
        sf_stereo_w.seek(2, which='r')


def test_initial_read_and_write_position(sf_stereo_rw_existing):
    assert sf_stereo_rw_existing.seek(0, sf.SEEK_CUR, 'w') == len(data_stereo)
    assert sf_stereo_rw_existing.seek(0, sf.SEEK_CUR, 'r') == 0
    # 'w' wins ...
    assert sf_stereo_rw_existing.seek(0, sf.SEEK_CUR) == len(data_stereo)
    # ... and moves read position:
    assert sf_stereo_rw_existing.seek(0, sf.SEEK_CUR, 'r') == len(data_stereo)


def test_if_seek_write_advances_read_position(sf_stereo_rw_existing):
    assert sf_stereo_rw_existing.seek(2, which='w') == 2
    assert sf_stereo_rw_existing.seek(0, sf.SEEK_CUR, 'r') == 0


def test_if_seek_read_advances_write_pointer(sf_stereo_rw_existing):
    assert sf_stereo_rw_existing.seek(2, which='r') == 2
    assert sf_stereo_rw_existing.seek(0, sf.SEEK_CUR, 'w') == len(data_stereo)


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


def test_read_by_indexing_should_read_but_not_advance_read_pointer(
        sf_stereo_r):
    assert np.all(sf_stereo_r[:2] == data_stereo[:2])
    assert sf_stereo_r.seek(0, sf.SEEK_CUR) == 0


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


def test_rw_read_written_data(sf_stereo_rw_new):
    sf_stereo_rw_new.seek(0)
    sf_stereo_rw_new.write(data_stereo)
    assert sf_stereo_rw_new.seek(0, sf.SEEK_CUR, 'w') == len(data_stereo)
    assert sf_stereo_rw_new.seek(0, sf.SEEK_CUR, 'r') == 0
    assert np.all(sf_stereo_rw_new.read() == data_stereo)
    assert sf_stereo_rw_new.seek(0, sf.SEEK_CUR, 'w') == len(data_stereo)
    assert sf_stereo_rw_new.seek(0, sf.SEEK_CUR, 'r') == len(data_stereo)
    sf_stereo_rw_new.close()
    data, fs = sf.read(filename_new)
    assert np.all(data == data_stereo)


def test_rw_writing_using_indexing_should_write_but_not_advance_write_pointer(
        sf_stereo_rw_new):
    data = np.ones((5, 2))
    # grow file to make room for indexing
    sf_stereo_rw_new.write(np.zeros((5, 2)))
    position = sf_stereo_rw_new.seek(0, sf.SEEK_CUR, which='w')
    sf_stereo_rw_new[:len(data)] = data
    written_data = sf_stereo_rw_new[:len(data)]
    assert np.all(data == written_data)
    assert position == sf_stereo_rw_new.seek(0, sf.SEEK_CUR, which='w')


def test_rw_append_data(sf_stereo_rw_existing):
    sf_stereo_rw_existing.write(data_stereo / 2)
    sf_stereo_rw_existing.close()
    data, fs = sf.read(tempfilename)
    assert np.all(data[:len(data_stereo)] == data_stereo)
    assert np.all(data[len(data_stereo):] == data_stereo / 2)


# -----------------------------------------------------------------------------
# Other tests
# -----------------------------------------------------------------------------


def test_context_manager_should_open_and_close_file():
    with sf.open(filename_stereo) as f:
        assert not f.closed
    assert f.closed


def test_closing_should_close_file():
    f = sf.open(filename_stereo)
    assert not f.closed
    f.close()
    assert f.closed


def test_file_attributes_should_save_to_disk():
    with sf.open(filename_new, 'w', 44100, 2, format='WAV') as f:
        f.title = 'testing'
    with sf.open(filename_new) as f:
        assert f.title == 'testing'
    os.remove(filename_new)


def test_non_file_attributes_should_not_save_to_disk():
    with sf.open(filename_new, 'w', 44100, 2, format='WAV') as f:
        f.foobar = 'testing'
    with sf.open(filename_new) as f:
        with pytest.raises(AttributeError):
            f.foobar
    os.remove(filename_new)


# -----------------------------------------------------------------------------
# RAW tests
# -----------------------------------------------------------------------------


def test_read_raw_files_should_read_data():
    with sf.open(filename_raw, sample_rate=44100,
                 channels=1, subtype='PCM_16') as f:
        assert np.all(f.read(dtype='int16') == data_mono)


def test_read_raw_files_with_too_few_arguments_should_fail():
    with pytest.raises(TypeError):  # missing everything
        sf.open(filename_raw)
    with pytest.raises(TypeError):  # missing subtype
        sf.open(filename_raw, sample_rate=44100, channels=2)
    with pytest.raises(TypeError):  # missing channels
        sf.open(filename_raw, sample_rate=44100, subtype='PCM_16')
    with pytest.raises(TypeError):  # missing sample_rate
        sf.open(filename_raw, channels=2, subtype='PCM_16')
