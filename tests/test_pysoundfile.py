import unittest
import pysoundfile as sf
import numpy as np
import os
import io
import pytest

data_r = np.ones((5,2))*0.5
file_r = 'tests/test_r.wav'
file_w  = 'tests/test_w.wav'

def open_filename(filename, rw, _):
    if rw == 'r':
        return sf.SoundFile(filename)
    elif rw == 'w':
        return sf.SoundFile(filename, mode=rw, sample_rate=44100, channels=2)
    elif rw == 'rw' and filename == file_r:
        return sf.SoundFile(filename, mode=rw)
    elif rw == 'rw' and filename == file_w:
        return sf.SoundFile(filename, mode=rw, sample_rate=44100, channels=2)

def open_filehandle(filename, rw, _):
    # TODO: does sf.SoundFile auto-close the handle???
    # request.addfinalizer(lambda: os.close(handle))
    if rw == 'r':
        handle = os.open(filename, os.O_RDONLY)
    elif rw == 'w':
        handle = os.open(filename, os.O_CREAT | os.O_WRONLY)
    elif rw == 'rw' and filename == file_r:
        handle = os.open(filename, os.O_RDWR)
    elif rw =='rw' and filename == file_w:
        handle = os.open(filename, os.O_CREAT | os.O_RDWR)
    if filename == file_r:
        return sf.SoundFile(handle, mode=rw)
    elif filename == file_w:
        return sf.SoundFile(handle, mode=rw, sample_rate=44100, channels=2, format='wav')

def open_bytestream(filename, rw, request):
    if rw == 'r':
        bytesio = open(filename, 'rb')
    elif rw == 'w':
        bytesio = open(filename, 'wb')
    elif rw == 'rw' and filename == file_r:
        bytesio = open(filename, 'a+b')
    elif rw == 'rw' and filename == file_w:
        bytesio = open(filename, 'w+b')
    if filename == file_r:
        file = sf.SoundFile(bytesio, mode=rw)
    elif filename == file_w:
        file = sf.SoundFile(bytesio, mode=rw, sample_rate=44100, channels=2, format='wav')
    request.addfinalizer(bytesio.close)
    return file

@pytest.fixture(params=[('r', open_filename),
                        ('r', open_filehandle),
                        ('r', open_bytestream)])
def wavefile_r(request):
    rw, open_func = request.param
    file = open_func(file_r, rw, request)
    request.addfinalizer(file.close)
    return file

@pytest.fixture(params=[('w', open_filename),
                        ('w', open_filehandle),
                        ('w', open_bytestream)])
def wavefile_w(request):
    rw, open_func = request.param
    file = open_func(file_w, rw, request)
    request.addfinalizer(file.close)
    request.addfinalizer(lambda: os.remove(file_w))
    return file

@pytest.fixture(params=[('rw', open_filename),
                        ('rw', open_filehandle),
                        # rw is not permissable with bytestreams
                        ])
def wavefile_rw_existing(request):
    rw, open_func = request.param
    file = open_func(file_r, rw, request)
    request.addfinalizer(file.close)
    return file

@pytest.fixture(params=[('rw', open_filename),
                        ('rw', open_filehandle),
                        # rw is not permissable with bytestreams
                        ])
def wavefile_rw_new(request):
    rw, open_func = request.param
    file = open_func(file_w, rw, request)
    request.addfinalizer(file.close)
    request.addfinalizer(lambda: os.remove(file_w))
    return file

@pytest.fixture(params=[('r', open_filename),
                        ('w', open_filename),
                        ('rw', open_filename),
                        ('r', open_filehandle),
                        ('w', open_filehandle),
                        ('rw', open_filehandle),
                        ('r', open_bytestream),
                        ('w', open_bytestream),
                        # rw is not permissable with bytestreams
                        ])
def wavefile_all(request):
    rw, open_func = request.param
    if 'r' in rw:
        file = open_func(file_r, rw, request)
    elif rw == 'w':
        file = open_func(file_w, rw, request)
    request.addfinalizer(file.close)
    if rw == 'w':
        request.addfinalizer(lambda: os.remove(file_w))
    return file

# ------------------------------------------------------------------------------
# Test file metadata
# ------------------------------------------------------------------------------

def test_file_content(wavefile_r):
    assert np.all(data_r == wavefile_r[:])

def test_mode_should_be_in_read_mode(wavefile_r):
    assert wavefile_r.mode == 'r'

def test_mode_should_be_in_read_mode(wavefile_w):
    assert wavefile_w.mode == 'w'

def test_mode_should_be_in_read_mode(wavefile_rw_existing):
    assert wavefile_rw_existing.mode == 'rw'

def test_mode_read_should_start_at_beginning(wavefile_r):
    assert wavefile_r.seek(0, sf.SEEK_CUR) == 0

def test_mode_write_should_start_at_beginning(wavefile_w):
    assert wavefile_w.seek(0, sf.SEEK_CUR) == 0

def test_mode_rw_should_start_at_end(wavefile_rw_existing):
    assert wavefile_rw_existing.seek(0, sf.SEEK_CUR) == 5

def test_number_of_channels(wavefile_all):
    assert wavefile_all.channels == 2

def test_sample_rate(wavefile_all):
    assert wavefile_all.sample_rate == 44100

def test_format_metadata(wavefile_all):
    assert wavefile_all.format == 'WAV'
    assert wavefile_all.subtype == 'PCM_16'
    assert wavefile_all.endian == 'FILE'
    assert wavefile_all.format_info == 'WAV (Microsoft)'
    assert wavefile_all.subtype_info == 'Signed 16 bit PCM'

def test_data_length(wavefile_r):
    assert len(wavefile_r) == len(data_r)

def test_data_length(wavefile_w):
    assert len(wavefile_w) == 0

def test_file_exists(wavefile_w):
    assert os.path.isfile(file_w)

# ------------------------------------------------------------------------------
# Test seek
# ------------------------------------------------------------------------------

def test_seek_should_advance_read_pointer(wavefile_r):
    assert wavefile_r.seek(2) == 2

def test_seek_multiple_times_should_advance_read_pointer(wavefile_r):
    wavefile_r.seek(2)
    assert wavefile_r.seek(2, whence=sf.SEEK_CUR) == 4

def test_seek_to_end_should_advance_read_pointer_to_end(wavefile_r):
    assert wavefile_r.seek(-2, whence=sf.SEEK_END) == 3

def test_seek_read_pointer_should_advance_read_pointer(wavefile_r):
    assert wavefile_r.seek(2, which='r') == 2

def test_seek_read_pointer_should_advance_read_pointer(wavefile_w):
    assert wavefile_w.seek(2, which='w') == 2

# ------------------------------------------------------------------------------
# Test read
# ------------------------------------------------------------------------------

def test_read_write_only(wavefile_w):
    with pytest.raises(RuntimeError):
        wavefile_w.read(2)

def test_read_should_read_data_and_advance_read_pointer(wavefile_r):
    data = wavefile_r.read(2)
    assert np.all(data == data_r[:2])
    assert wavefile_r.seek(0, sf.SEEK_CUR) == 2

def test_read_should_read_float64_data(wavefile_r):
    assert wavefile_r[:].dtype == np.float64

def test_read_int16_should_read_int16_data(wavefile_r):
    assert wavefile_r.read(2, dtype='int16').dtype == np.int16

def test_read_int32_should_read_int32_data(wavefile_r):
    assert wavefile_r.read(2, dtype='int32').dtype == np.int32

def test_read_float32_should_read_float32_data(wavefile_r):
    assert wavefile_r.read(2, dtype='float32').dtype == np.float32

def test_read_by_indexing_should_read_but_not_advance_read_pointer(wavefile_r):
    assert np.all(wavefile_r[:2] == data_r[:2])
    assert wavefile_r.seek(0, sf.SEEK_CUR) == 0

def test_read_n_frames_should_return_n_frames(wavefile_r):
    assert len(wavefile_r.read(2)) == 2

def test_read_all_frames_should_read_all_remaining_frames(wavefile_r):
    wavefile_r.seek(-2, sf.SEEK_END)
    assert np.all(wavefile_r.read() == data_r[-2:])

def test_read_over_end_should_return_only_remaining_frames(wavefile_r):
    wavefile_r.seek(-2, sf.SEEK_END)
    assert np.all(wavefile_r.read(4) == data_r[-2:])

def test_read_over_end_with_fill_should_reaturn_asked_frames(wavefile_r):
    wavefile_r.seek(-2, sf.SEEK_END)
    data = wavefile_r.read(4, fill_value=0)
    assert np.all(data[:2] == data_r[-2:])
    assert np.all(data[2:] == 0)
    assert len(data) == 4

def test_read_into_out_should_return_data_and_write_into_out(wavefile_r):
    out = np.empty((2, wavefile_r.channels), dtype='float64')
    data = wavefile_r.read(out=out)
    assert np.all(data == out)

def test_read_into_malformed_out_should_fail(wavefile_r):
    out = np.empty((2, wavefile_r.channels+1), dtype='float64')
    with pytest.raises(ValueError):
        wavefile_r.read(out=out)

def test_read_into_out_with_too_many_dimensions_should_fail(wavefile_r):
    out = np.empty((2, wavefile_r.channels, 1), dtype='float64')
    with pytest.raises(ValueError):
        wavefile_r.read(out=out)

def test_read_into_zero_len_out_should_not_read_anything(wavefile_r):
    out = np.empty((0, wavefile_r.channels), dtype='float64')
    data = wavefile_r.read(out=out)
    assert len(data) == 0
    assert len(out) == 0
    assert wavefile_r.seek(0, sf.SEEK_CUR) == 0

def test_read_into_out_over_end_should_return_shorter_data_and_write_into_out(wavefile_r):
    out = np.ones((4, wavefile_r.channels), dtype='float64')
    wavefile_r.seek(-2, sf.SEEK_END)
    data = wavefile_r.read(out=out)
    assert np.all(data[:2] == out[:2])
    assert np.all(data[2:] == 1)
    assert out.shape == (4, wavefile_r.channels)
    assert data.shape == (2, wavefile_r.channels)

def test_read_into_out_over_end_with_fill_should_return_full_data_and_write_into_out(wavefile_r):
    out = np.ones((4, wavefile_r.channels), dtype='float64')
    wavefile_r.seek(-2, sf.SEEK_END)
    data = wavefile_r.read(out=out, fill_value=0)
    assert np.all(data == out)
    assert np.all(data[2:] == 0)
    assert out.shape == (4, wavefile_r.channels)

# ------------------------------------------------------------------------------
# Test write
# ------------------------------------------------------------------------------

def test_write_to_read_only_file_should_fail(wavefile_r):
    with pytest.raises(RuntimeError):
        wavefile_r.write(data_r)

def test_write_should_write_and_advance_write_pointer(wavefile_w):
    position_w = wavefile_w.seek(0, sf.SEEK_CUR, which='w')
    position_r = wavefile_w.seek(0, sf.SEEK_CUR, which='r')
    wavefile_w.write(data_r)
    assert wavefile_w.seek(0, sf.SEEK_CUR, which='w') == position_w+len(data_r)
    assert wavefile_w.seek(0, sf.SEEK_CUR, which='r') == position_r

def test_write_flush_should_write_to_disk(wavefile_w):
    wavefile_w.flush()
    size = os.path.getsize(file_w)
    wavefile_w.write(data_r)
    wavefile_w.flush()
    assert os.path.getsize(file_w) == size + data_r.size*2 # 16 bit integer

# ------------------------------------------------------------------------------
# Test read/write
# ------------------------------------------------------------------------------

def test_rw_initial_read_and_write_pointer(wavefile_rw_existing):
    assert wavefile_rw_existing.seek(0, sf.SEEK_CUR, which='w') == 5
    assert wavefile_rw_existing.seek(0, sf.SEEK_CUR, which='r') == 0

def test_rw_seek_write_should_advance_write_pointer(wavefile_rw_existing):
    assert wavefile_rw_existing.seek(2, which='w') == 2
    assert wavefile_rw_existing.seek(0, sf.SEEK_CUR, which='r') == 0

def test_rw_seek_read_should_advance_read_pointer(wavefile_rw_existing):
    assert wavefile_rw_existing.seek(2, which='r') == 2
    assert wavefile_rw_existing.seek(0, sf.SEEK_CUR, which='w') == 5

def test_rw_writing_float_should_be_written_approximately_correct(wavefile_rw_new):
    data = np.ones((5,2), dtype='float64')
    wavefile_rw_new.seek(0, which='w')
    wavefile_rw_new.write(data)
    written_data = wavefile_rw_new[-len(data):]
    assert np.allclose(data, written_data, atol=2**-15)

def test_rw_writing_int_should_be_written_exactly_correct(wavefile_rw_new):
    data = np.zeros((5,2)) + 2**15-1 # full scale int16
    wavefile_rw_new.seek(0, which='w')
    wavefile_rw_new.write(np.array(data, dtype='int16'))
    written_data = wavefile_rw_new.read(dtype='int16')
    assert np.all(data == written_data)

def test_rw_writing_using_indexing_should_write_but_not_advance_write_pointer(wavefile_rw_new):
    data = np.ones((5,2))
    wavefile_rw_new.write(np.zeros((5,2))) # grow file to make room for indexing
    position = wavefile_rw_new.seek(0, sf.SEEK_CUR, which='w')
    wavefile_rw_new[:len(data)] = data
    written_data = wavefile_rw_new[:len(data)]
    assert np.allclose(data, written_data, atol=2**-15)
    assert position == wavefile_rw_new.seek(0, sf.SEEK_CUR, which='w')

# ------------------------------------------------------------------------------
# Other tests
# ------------------------------------------------------------------------------

def test_context_manager_should_open_and_close_file():
    with open_filename(file_r, 'r', None) as f:
        assert not f.closed
    assert f.closed

def test_closing_should_close_file():
    f = open_filename(file_r, 'r', None)
    assert not f.closed
    f.close()
    assert f.closed

def test_file_attributes_should_save_to_disk():
    with open_filename(file_w, 'w', None) as f:
        f.title = 'testing'
    with open_filename(file_w, 'r', None) as f:
        assert f.title == 'testing'
    os.remove(file_w)

def test_non_file_attributes_should_not_save_to_disk():
    with open_filename(file_w, 'w', None) as f:
        f.foobar = 'testing'
    with open_filename(file_w, 'r', None) as f:
        with pytest.raises(AttributeError):
            f.foobar
    os.remove(file_w)

# ------------------------------------------------------------------------------
# Legacy tests
# ------------------------------------------------------------------------------

class TestWaveFile(unittest.TestCase):
    def setUp(self):
        """create a dummy wave file"""
        self.sample_rate = 44100
        self.channels = 2
        self.filename = 'test.wav'
        self.data = np.ones((self.sample_rate, self.channels))*0.5
        with sf.SoundFile(self.filename, 'w', self.sample_rate, self.channels) as f:
            f.write(self.data)

    def tearDown(self):
        os.remove(self.filename)


class TestSeekWaveFile(TestWaveFile):
    def test_read_mono_into_out(self):
        """Reading mono signal into out should return data and write into out"""
        # create a dummy mono wave file
        self.sample_rate = 44100
        self.channels = 1
        self.filename = 'test.wav'
        self.data = np.ones((self.sample_rate, self.channels))*0.5
        with sf.SoundFile(self.filename, 'w', self.sample_rate, self.channels) as f:
            f.write(self.data)

        with sf.SoundFile(self.filename) as f:
            data = np.empty((100, f.channels), dtype='float64')
            out_data = f.read(out=data)
            self.assertTrue(np.all(data == out_data))

    def test_read_mono_as_array(self):
        """Reading with always_2d=False should return array"""
        # create a dummy mono wave file
        self.sample_rate = 44100
        self.channels = 1
        self.filename = 'test.wav'
        self.data = np.ones((self.sample_rate, self.channels))*0.5
        with sf.SoundFile(self.filename, 'w', self.sample_rate, self.channels) as f:
            f.write(self.data)

        with sf.SoundFile(self.filename) as f:
            data = f.read(100, always_2d=False)
            self.assertEqual(data.shape, (100,))
