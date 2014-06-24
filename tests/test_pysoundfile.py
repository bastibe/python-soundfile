import pysoundfile as sf
import numpy as np
import os
import pytest

data_r = np.array([[1.0, -1.0],
                   [0.8, -0.8],
                   [0.6, -0.6],
                   [0.4, -0.4],
                   [0.2, -0.2]])
file_r = 'tests/test_r.wav'
data_r_mono = np.array([1.0, 0.8, 0.6, 0.4, 0.2])
file_r_mono = 'tests/test_r_mono.wav'
data_r_raw = np.array(data_r, copy=True)
file_r_raw = 'tests/test_r.raw'
file_w = 'tests/test_w.wav'


def allclose(x, y):
    return np.allclose(x, y, atol=2**-15)


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
    else:
        assert False


def _file_new(request, fdarg, objarg=None):
    filename = file_w

    def finalizer():
        os.remove(filename)

    request.addfinalizer(finalizer)
    return _file_existing(request, filename, fdarg, objarg)


@pytest.fixture(params=['name', 'fd', 'obj'])
def file_stereo_r(request):
    return _file_existing(request, file_r, os.O_RDONLY, 'rb')


@pytest.fixture(params=['name', 'fd', 'obj'])
def file_mono_r(request):
    return _file_existing(request, file_r_mono, os.O_RDONLY, 'rb')


@pytest.fixture(params=['name', 'fd', 'obj'])
def file_stereo_w(request):
    return _file_new(request, os.O_CREAT | os.O_WRONLY, 'wb')


# 'rw' is not permissible with file-like objects
@pytest.fixture(params=['name', 'fd'])
def file_stereo_rw_existing(request):
    return _file_existing(request, file_r, os.O_RDWR)


# 'rw' is not permissible with file-like objects
@pytest.fixture(params=['name', 'fd'])
def file_stereo_rw_new(request):
    return _file_new(request, os.O_CREAT | os.O_RDWR)


@pytest.yield_fixture
def soundfile_stereo_r(file_stereo_r):
    with sf.SoundFile(file_stereo_r) as f:
        yield f


@pytest.yield_fixture
def soundfile_mono_r(file_mono_r):
    with sf.SoundFile(file_mono_r) as f:
        yield f


@pytest.yield_fixture
def soundfile_stereo_w(file_stereo_w):
    with sf.SoundFile(file_stereo_w, 'w', 44100, 2, format='WAV') as f:
        yield f


@pytest.yield_fixture
def soundfile_stereo_rw_existing(file_stereo_rw_existing):
    with sf.SoundFile(file_stereo_rw_existing, 'rw') as f:
        yield f


@pytest.yield_fixture
def soundfile_stereo_rw_new(file_stereo_rw_new):
    with sf.SoundFile(file_stereo_rw_new, 'rw', 44100, 2, format='WAV') as f:
        yield f


# -----------------------------------------------------------------------------
# Test file metadata
# -----------------------------------------------------------------------------


def test_file_content(soundfile_stereo_r):
    assert allclose(data_r, soundfile_stereo_r[:])


def test_mode_should_be_in_read_mode(soundfile_stereo_r):
    assert soundfile_stereo_r.mode == 'r'


def test_mode_should_be_in_write_mode(soundfile_stereo_w):
    assert soundfile_stereo_w.mode == 'w'


def test_mode_should_be_in_readwrite_mode(soundfile_stereo_rw_existing):
    assert soundfile_stereo_rw_existing.mode == 'rw'


def test_mode_read_should_start_at_beginning(soundfile_stereo_r):
    assert soundfile_stereo_r.seek(0, sf.SEEK_CUR) == 0


def test_mode_write_should_start_at_beginning(soundfile_stereo_w):
    assert soundfile_stereo_w.seek(0, sf.SEEK_CUR) == 0


def test_mode_rw_should_start_at_end(soundfile_stereo_rw_existing):
    assert soundfile_stereo_rw_existing.seek(0, sf.SEEK_CUR) == 5


def test_number_of_channels(soundfile_stereo_r):
    assert soundfile_stereo_r.channels == 2


def test_sample_rate(soundfile_stereo_r):
    assert soundfile_stereo_r.sample_rate == 44100


def test_format_metadata(soundfile_stereo_r):
    assert soundfile_stereo_r.format == 'WAV'
    assert soundfile_stereo_r.subtype == 'PCM_16'
    assert soundfile_stereo_r.endian == 'FILE'
    assert soundfile_stereo_r.format_info == 'WAV (Microsoft)'
    assert soundfile_stereo_r.subtype_info == 'Signed 16 bit PCM'


def test_data_length_r(soundfile_stereo_r):
    assert len(soundfile_stereo_r) == len(data_r)


def test_data_length_w(soundfile_stereo_w):
    assert len(soundfile_stereo_w) == 0


def test_file_exists(soundfile_stereo_w):
    assert os.path.isfile(file_w)


# -----------------------------------------------------------------------------
# Test seek
# -----------------------------------------------------------------------------


def test_seek_should_advance_read_pointer(soundfile_stereo_r):
    assert soundfile_stereo_r.seek(2) == 2


def test_seek_multiple_times_should_advance_read_pointer(soundfile_stereo_r):
    soundfile_stereo_r.seek(2)
    assert soundfile_stereo_r.seek(2, whence=sf.SEEK_CUR) == 4


def test_seek_to_end_should_advance_read_pointer_to_end(soundfile_stereo_r):
    assert soundfile_stereo_r.seek(-2, whence=sf.SEEK_END) == 3


def test_seek_read_pointer_should_advance_read_pointer(soundfile_stereo_r):
    assert soundfile_stereo_r.seek(2, which='r') == 2


def test_seek_write_pointer_should_advance_write_pointer(soundfile_stereo_w):
    assert soundfile_stereo_w.seek(2, which='w') == 2


# -----------------------------------------------------------------------------
# Test read
# -----------------------------------------------------------------------------


def test_read_write_only(soundfile_stereo_w):
    with pytest.raises(RuntimeError):
        soundfile_stereo_w.read(2)


def test_read_should_read_data_and_advance_read_pointer(soundfile_stereo_r):
    data = soundfile_stereo_r.read(2)
    assert allclose(data, data_r[:2])
    assert soundfile_stereo_r.seek(0, sf.SEEK_CUR) == 2


def test_read_should_read_float64_data(soundfile_stereo_r):
    assert soundfile_stereo_r[:].dtype == np.float64


def test_read_int16_should_read_int16_data(soundfile_stereo_r):
    assert soundfile_stereo_r.read(2, dtype='int16').dtype == np.int16


def test_read_int32_should_read_int32_data(soundfile_stereo_r):
    assert soundfile_stereo_r.read(2, dtype='int32').dtype == np.int32


def test_read_float32_should_read_float32_data(soundfile_stereo_r):
    assert soundfile_stereo_r.read(2, dtype='float32').dtype == np.float32


def test_read_by_indexing_should_read_but_not_advance_read_pointer(
        soundfile_stereo_r):
    assert allclose(soundfile_stereo_r[:2], data_r[:2])
    assert soundfile_stereo_r.seek(0, sf.SEEK_CUR) == 0


def test_read_n_frames_should_return_n_frames(soundfile_stereo_r):
    assert len(soundfile_stereo_r.read(2)) == 2


def test_read_all_frames_should_read_all_remaining_frames(soundfile_stereo_r):
    soundfile_stereo_r.seek(-2, sf.SEEK_END)
    assert allclose(soundfile_stereo_r.read(), data_r[-2:])


def test_read_over_end_should_return_only_remaining_frames(soundfile_stereo_r):
    soundfile_stereo_r.seek(-2, sf.SEEK_END)
    assert allclose(soundfile_stereo_r.read(4), data_r[-2:])


def test_read_over_end_with_fill_should_reaturn_asked_frames(
        soundfile_stereo_r):
    soundfile_stereo_r.seek(-2, sf.SEEK_END)
    data = soundfile_stereo_r.read(4, fill_value=0)
    assert allclose(data[:2], data_r[-2:])
    assert np.all(data[2:] == 0)
    assert len(data) == 4


def test_read_into_out_should_return_data_and_write_into_out(
        soundfile_stereo_r):
    out = np.empty((2, soundfile_stereo_r.channels), dtype='float64')
    data = soundfile_stereo_r.read(out=out)
    assert np.all(data == out)


def test_read_into_malformed_out_should_fail(soundfile_stereo_r):
    out = np.empty((2, soundfile_stereo_r.channels+1), dtype='float64')
    with pytest.raises(ValueError):
        soundfile_stereo_r.read(out=out)


def test_read_into_out_with_too_many_dimensions_should_fail(
        soundfile_stereo_r):
    out = np.empty((2, soundfile_stereo_r.channels, 1), dtype='float64')
    with pytest.raises(ValueError):
        soundfile_stereo_r.read(out=out)


def test_read_into_zero_len_out_should_not_read_anything(soundfile_stereo_r):
    out = np.empty((0, soundfile_stereo_r.channels), dtype='float64')
    data = soundfile_stereo_r.read(out=out)
    assert len(data) == 0
    assert len(out) == 0
    assert soundfile_stereo_r.seek(0, sf.SEEK_CUR) == 0


def test_read_into_out_over_end_should_return_shorter_data_and_write_into_out(
        soundfile_stereo_r):
    out = np.ones((4, soundfile_stereo_r.channels), dtype='float64')
    soundfile_stereo_r.seek(-2, sf.SEEK_END)
    data = soundfile_stereo_r.read(out=out)
    assert np.all(data[:2] == out[:2])
    assert np.all(data[2:] == 1)
    assert out.shape == (4, soundfile_stereo_r.channels)
    assert data.shape == (2, soundfile_stereo_r.channels)


def test_read_into_out_over_end_with_fill_should_return_full_data_and_write_into_out(
        soundfile_stereo_r):
    out = np.ones((4, soundfile_stereo_r.channels), dtype='float64')
    soundfile_stereo_r.seek(-2, sf.SEEK_END)
    data = soundfile_stereo_r.read(out=out, fill_value=0)
    assert np.all(data == out)
    assert np.all(data[2:] == 0)
    assert out.shape == (4, soundfile_stereo_r.channels)


# -----------------------------------------------------------------------------
# Test write
# -----------------------------------------------------------------------------


def test_write_to_read_only_file_should_fail(soundfile_stereo_r):
    with pytest.raises(RuntimeError):
        soundfile_stereo_r.write(data_r)


def test_write_should_write_and_advance_write_pointer(soundfile_stereo_w):
    position_w = soundfile_stereo_w.seek(0, sf.SEEK_CUR, which='w')
    position_r = soundfile_stereo_w.seek(0, sf.SEEK_CUR, which='r')
    soundfile_stereo_w.write(data_r)
    assert (soundfile_stereo_w.seek(0, sf.SEEK_CUR, which='w') ==
            position_w+len(data_r))
    assert soundfile_stereo_w.seek(0, sf.SEEK_CUR, which='r') == position_r


def test_write_flush_should_write_to_disk(soundfile_stereo_w):
    soundfile_stereo_w.flush()
    size = os.path.getsize(file_w)
    soundfile_stereo_w.write(data_r)
    soundfile_stereo_w.flush()
    assert os.path.getsize(file_w) == size + data_r.size * 2  # 16 bit integer


# -----------------------------------------------------------------------------
# Test read/write
# -----------------------------------------------------------------------------


def test_rw_initial_read_and_write_pointer(soundfile_stereo_rw_existing):
    assert soundfile_stereo_rw_existing.seek(0, sf.SEEK_CUR, which='w') == 5
    assert soundfile_stereo_rw_existing.seek(0, sf.SEEK_CUR, which='r') == 0


def test_rw_seek_write_should_advance_write_pointer(
        soundfile_stereo_rw_existing):
    assert soundfile_stereo_rw_existing.seek(2, which='w') == 2
    assert soundfile_stereo_rw_existing.seek(0, sf.SEEK_CUR, which='r') == 0


def test_rw_seek_read_should_advance_read_pointer(
        soundfile_stereo_rw_existing):
    assert soundfile_stereo_rw_existing.seek(2, which='r') == 2
    assert soundfile_stereo_rw_existing.seek(0, sf.SEEK_CUR, which='w') == 5


def test_rw_writing_float_should_be_written_approximately_correct(
        soundfile_stereo_rw_new):
    data = np.ones((5, 2), dtype='float64')
    soundfile_stereo_rw_new.seek(0, which='w')
    soundfile_stereo_rw_new.write(data)
    written_data = soundfile_stereo_rw_new[-len(data):]
    assert allclose(data, written_data)


def test_rw_writing_int_should_be_written_exactly_correct(
        soundfile_stereo_rw_new):
    data = np.zeros((5, 2)) + 2**15 - 1  # full scale int16
    soundfile_stereo_rw_new.seek(0, which='w')
    soundfile_stereo_rw_new.write(np.array(data, dtype='int16'))
    written_data = soundfile_stereo_rw_new.read(dtype='int16')
    assert np.all(data == written_data)


def test_rw_writing_using_indexing_should_write_but_not_advance_write_pointer(
        soundfile_stereo_rw_new):
    data = np.ones((5, 2))
    # grow file to make room for indexing
    soundfile_stereo_rw_new.write(np.zeros((5, 2)))
    position = soundfile_stereo_rw_new.seek(0, sf.SEEK_CUR, which='w')
    soundfile_stereo_rw_new[:len(data)] = data
    written_data = soundfile_stereo_rw_new[:len(data)]
    assert allclose(data, written_data)
    assert position == soundfile_stereo_rw_new.seek(0, sf.SEEK_CUR, which='w')


# -----------------------------------------------------------------------------
# Other tests
# -----------------------------------------------------------------------------


def test_context_manager_should_open_and_close_file():
    with sf.SoundFile(file_r) as f:
        assert not f.closed
    assert f.closed


def test_closing_should_close_file():
    f = sf.SoundFile(file_r)
    assert not f.closed
    f.close()
    assert f.closed


def test_file_attributes_should_save_to_disk():
    with sf.SoundFile(file_w, 'w', 44100, 2, format='WAV') as f:
        f.title = 'testing'
    with sf.SoundFile(file_w) as f:
        assert f.title == 'testing'
    os.remove(file_w)


def test_non_file_attributes_should_not_save_to_disk():
    with sf.SoundFile(file_w, 'w', 44100, 2, format='WAV') as f:
        f.foobar = 'testing'
    with sf.SoundFile(file_w) as f:
        with pytest.raises(AttributeError):
            f.foobar
    os.remove(file_w)


def test_read_mono_without_always2d_should_read_array(soundfile_mono_r):
    out_data = soundfile_mono_r.read(always_2d=False)
    assert allclose(out_data, data_r_mono)
    assert out_data.ndim == 1


def test_read_mono_should_read_matrix(soundfile_mono_r):
    out_data = soundfile_mono_r.read()
    assert allclose(out_data, [[x] for x in data_r_mono])
    assert out_data.ndim == 2


def test_read_mono_into_mono_out_should_read_into_out(soundfile_mono_r):
    data = np.empty(5, dtype='float64')
    out_data = soundfile_mono_r.read(out=data)
    assert np.all(data == out_data)
    assert id(data) == id(out_data)


def test_read_mono_into_out_should_read_into_out(soundfile_mono_r):
    data = np.empty((5, 1), dtype='float64')
    out_data = soundfile_mono_r.read(out=data)
    assert np.all(data == out_data)
    assert id(data) == id(out_data)


# -----------------------------------------------------------------------------
# RAW tests
# -----------------------------------------------------------------------------


def test_read_raw_files_should_read_data():
    with sf.SoundFile(file_r_raw, sample_rate=44100,
                      channels=2, subtype='PCM_16') as f:
        assert allclose(f.read(), data_r_raw)


def test_read_raw_files_with_too_few_arguments_should_fail():
    with pytest.raises(TypeError):  # missing everything
        sf.SoundFile(file_r_raw)
    with pytest.raises(TypeError):  # missing subtype
        sf.SoundFile(file_r_raw, sample_rate=44100, channels=2)
    with pytest.raises(TypeError):  # missing channels
        sf.SoundFile(file_r_raw, sample_rate=44100, subtype='PCM_16')
    with pytest.raises(TypeError):  # missing sample_rate
        sf.SoundFile(file_r_raw, channels=2, subtype='PCM_16')
