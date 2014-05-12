import unittest
import pysoundfile as sf
import numpy as np
import os
import io

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


class TestBasicAttributesOfWaveFile(TestWaveFile):
    def test_file_exists(self):
        """The test file should exist"""
        self.assertTrue(os.path.isfile(self.filename))

    def test_open_file_descriptor(self):
        """Opening a file handle should work"""
        handle = os.open(self.filename, os.O_RDONLY)
        with sf.SoundFile(handle) as f:
            self.assertTrue(np.all(self.data == f[:]))

    def test_open_virtual_io(self):
        """Opening a file-like object should work"""
        with open(self.filename, 'rb') as bytesio:
            with sf.SoundFile(bytesio) as f:
                self.assertTrue(np.all(self.data == f[:]))

    def test_read_mode(self):
        """Opening the file in read mode should open in read mode from beginning"""
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(f.mode, 'r')
            self.assertEqual(f.seek(0, sf.SEEK_CUR), 0)

    def test_write_mode(self):
        """Opening the file in write mode should open in write mode from beginning"""
        with sf.SoundFile(self.filename, 'w', self.sample_rate, self.channels) as f:
            self.assertEqual(f.mode, 'w')
            self.assertEqual(f.seek(0, sf.SEEK_CUR), 0)

    def test_rw_mode(self):
        """Opening the file in rw mode should open in rw mode from end"""
        with sf.SoundFile(self.filename, 'rw') as f:
            self.assertEqual(f.mode, 'rw')
            self.assertEqual(f.seek(0, sf.SEEK_CUR), len(f))

    def test_channels(self):
        """The test file should have the correct number of channels"""
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(f.channels, self.channels)

    def test_sample_rate(self):
        """The test file should have the correct number of sample rate"""
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(f.sample_rate, self.sample_rate)

    def test_format(self):
        """The test file should be a wave file"""
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(f.format, 'WAV')
            self.assertEqual(f.subtype, 'PCM_16')
            self.assertEqual(f.endian, 'FILE')
            self.assertEqual(f.format_info, 'WAV (Microsoft)')
            self.assertEqual(f.subtype_info, 'Signed 16 bit PCM')

    def test_context_manager(self):
        """The context manager should close the file"""
        with sf.SoundFile(self.filename) as f:
            pass
        self.assertTrue(f.closed)

    def test_closing(self):
        """Closing a file should close it"""
        f = sf.SoundFile(self.filename)
        self.assertFalse(f.closed)
        f.close()
        self.assertTrue(f.closed)

    def test_file_length(self):
        """The file should have the correct length"""
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(len(f), self.sample_rate)

    def test_file_contents(self):
        """The file should contain the correct data"""
        with sf.SoundFile(self.filename) as f:
            self.assertTrue(np.all(self.data == f[:]))

    def test_file_attributes(self):
        """Changing a file attribute should save it on disk"""
        with sf.SoundFile(self.filename, 'rw') as f:
            f.title = 'testing'
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(f.title, 'testing')

    def test_non_file_attributes(self):
        """Changing a non-file attribute should not save to disk"""
        with sf.SoundFile(self.filename, 'rw') as f:
            f.foobar = 'testing'
        with sf.SoundFile(self.filename) as f:
            with self.assertRaises(AttributeError):
                f.foobar


class TestSeekWaveFile(TestWaveFile):
    def test_seek(self):
        """Seeking should advance the read/write pointer"""
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(f.seek(100), 100)

    def test_seek_cur(self):
        """seeking multiple times should advance the read/write pointer"""
        with sf.SoundFile(self.filename) as f:
            f.seek(100)
            self.assertEqual(f.seek(100, whence=sf.SEEK_CUR), 200)

    def test_seek_end(self):
        """seeking from end should advance the read/write pointer"""
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(f.seek(-100, whence=SEEK_END), self.sample_rate-100)

    def test_seek_read(self):
        """Read-seeking should advance the read pointer"""
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(f.seek(100, which='r'), 100)

    def test_seek_write(self):
        """write-seeking should advance the write pointer"""
        with sf.SoundFile(self.filename, 'rw') as f:
            self.assertEqual(f.seek(100, which='w'), 100)

    def test_flush(self):
        """After flushing, data should be written to disk"""
        with sf.SoundFile(self.filename, 'rw') as f:
            size = os.path.getsize(self.filename)
            f.write(np.zeros((10,2)))
            f.flush()
            self.assertEqual(os.path.getsize(self.filename), size+40)


class TestSeekWaveFile(TestWaveFile):
    def test_read(self):
        """read should read data and advance the read pointer"""
        with sf.SoundFile(self.filename) as f:
            data = f.read(100)
            self.assertTrue(np.all(data == self.data[:100]))
            self.assertEqual(100, f.seek(0, sf.SEEK_CUR))

    def test_read_write_only(self):
        """reading a write-only file should not work"""
        with sf.SoundFile(self.filename, 'w', self.sample_rate, self.channels) as f:
            with self.assertRaises(RuntimeError) as err:
                f.read(100)

    def test_default_read_format(self):
        """By default, np.float64 should be read"""
        with sf.SoundFile(self.filename) as f:
            self.assertEqual(f[:].dtype, np.float64)

    def test_read_int16(self):
        """reading 16 bit integers should read np.int16"""
        with sf.SoundFile(self.filename) as f:
            data = f.read(100, dtype='int16')
            self.assertEqual(data.dtype, np.int16)

    def test_read_int32(self):
        """reading 32 bit integers should read np.int32"""
        with sf.SoundFile(self.filename) as f:
            data = f.read(100, dtype='int32')
            self.assertEqual(data.dtype, np.int32)

    def test_read_float32(self):
        """reading 32 bit floats should read np.float32"""
        with sf.SoundFile(self.filename) as f:
            data = f.read(100, dtype='float32')
            self.assertEqual(data.dtype, np.float32)

    def test_read_indexing(self):
        """Reading using indexing should read but not advance read pointer"""
        with sf.SoundFile(self.filename) as f:
            self.assertTrue(np.all(f[:100] == self.data[:100]))
            self.assertEqual(0, f.seek(0, sf.SEEK_CUR))

    def test_read_number_of_frames(self):
        """Reading N frames should return N frames"""
        with sf.SoundFile(self.filename) as f:
            data = f.read(100)
            self.assertEqual(len(data), 100)

    def test_read_all_frames(self):
        """Reading should return all remaining frames"""
        with sf.SoundFile(self.filename) as f:
            f.seek(-100, sf.SEEK_END)
            data = f.read()
            self.assertEqual(len(data), 100)

    def test_read_number_of_frames_over_end(self):
        """Reading N frames at EOF should return only remaining frames"""
        with sf.SoundFile(self.filename) as f:
            f.seek(-50, sf.SEEK_END)
            data = f.read(100)
            self.assertEqual(len(data), 50)

    def test_read_number_of_frames_over_end_with_fill(self):
        """Reading N frames with fill at EOF should return N frames"""
        with sf.SoundFile(self.filename) as f:
            f.seek(-50, sf.SEEK_END)
            data = f.read(100, fill_value=0)
            self.assertEqual(len(data), 100)
            self.assertTrue(np.all(data[50:] == 0))

    def test_read_into_out(self):
        """Reading into out should return data and write into out"""
        with sf.SoundFile(self.filename) as f:
            data = np.empty((100, f.channels), dtype='float64')
            out_data = f.read(out=data)
            self.assertTrue(np.all(data == out_data))

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

    def test_read_into_out_with_too_many_channels(self):
        """Reading into malformed out should throw an error"""
        with sf.SoundFile(self.filename) as f:
            data = np.empty((100, f.channels+1), dtype='float64')
            with self.assertRaises(ValueError) as err:
                out_data = f.read(out=data)

    def test_read_into_out_with_too_many_dimensions(self):
        """Reading into malformed out should throw an error"""
        with sf.SoundFile(self.filename) as f:
            data = np.empty((100, f.channels, 1), dtype='float64')
            with self.assertRaises(ValueError) as err:
                out_data = f.read(out=data)

    def test_read_into_zero_len_out(self):
        """Reading into aa zero len out should not read anything"""
        with sf.SoundFile(self.filename) as f:
            data = np.empty((0, f.channels), dtype='float64')
            out_data = f.read(out=data)
            self.assertTrue(np.all(data == out_data))

    def test_read_into_out_over_end(self):
        """Reading into out over end should return shorter data and write into out"""
        with sf.SoundFile(self.filename) as f:
            data = np.empty((100, f.channels), dtype='float64')
            f.seek(-50, sf.SEEK_END)
            out_data = f.read(out=data)
            self.assertTrue(np.all(data[:50] == out_data[:50]))
            self.assertEqual(out_data.shape, (50,2))
            self.assertEqual(data.shape, (100,2))

    def test_read_into_out_over_end_with_fill(self):
        """Reading into out over end with fill should return padded data and write into out"""
        with sf.SoundFile(self.filename) as f:
            data = np.empty((100, f.channels), dtype='float64')
            f.seek(-50, sf.SEEK_END)
            out_data = f.read(out=data, fill_value=0)
            self.assertTrue(np.all(data == out_data))
            self.assertTrue(np.all(data[50:] == 0))

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

class TestWriteWaveFile(TestWaveFile):
    def test_write(self):
        """write should write data and advance the write pointer"""
        with sf.SoundFile(self.filename, 'rw') as f:
            data = np.zeros((100,2))
            position = f.seek(0, sf.SEEK_CUR)
            f.write(data)
            self.assertTrue(np.all(f[-100:] == data))
            self.assertEqual(100, f.seek(0, sf.SEEK_CUR)-position)

    def test_write_read_only(self):
        """writing to a read-only file should not work"""
        with sf.SoundFile(self.filename) as f:
            with self.assertRaises(RuntimeError) as err:
                f.write(np.ones((100,2)))

    def test_write_float_precision(self):
        """Written float data should be written at most 2**-15 off"""
        with sf.SoundFile(self.filename, 'rw') as f:
            data = np.ones((100,2))
            f.write(data)
            written_data = f[-100:]
            self.assertTrue(np.allclose(data, written_data, atol=2**-15))

    def test_write_int_precision(self):
        """Written int data should be written"""
        with sf.SoundFile(self.filename, 'rw') as f:
            data = np.zeros((100,2)) + 2**15-1 # full scale int16
            data = np.array(data, dtype='int16')
            f.write(data)
            f.seek(-100, sf.SEEK_CUR)
            written_data = f.read(dtype='int16')
            self.assertTrue(np.all(data == written_data))

    def test_write_indexing(self):
        """Writing using indexing should write but not advance write pointer"""
        with sf.SoundFile(self.filename, 'rw') as f:
            position = f.seek(0, sf.SEEK_CUR)
            data = np.zeros((100,2))
            f[:100] = data
            self.assertEqual(position, f.seek(0, sf.SEEK_CUR))
            self.assertTrue(np.all(data == f[:100]))

class TestWriteFunctions(TestWaveFile):
    def test_write(self):
        """write should write data"""
        data = np.ones((100,2))
        sf.write(data, self.filename, self.sample_rate)
        self.assertTrue(np.allclose(sf.read(self.filename)[0], data, atol=2**-15))
