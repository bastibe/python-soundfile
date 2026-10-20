"""Virtual read failures must not be mistaken for end of audio."""
import gc
import io
import sys
import wave
import weakref

import numpy as np
import pytest
import soundfile as sf


def wav_data(channels):
    samples = np.arange(32 * channels, dtype='<i2').reshape(32, channels)
    stream = io.BytesIO()
    with wave.open(stream, 'wb') as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(16000)
        wav.writeframes(samples.tobytes())
    return stream.getvalue(), samples


class Reader:
    def __init__(self, data, readinto):
        self.stream = io.BytesIO(data)
        self.error = None
        self.chunk_limit = None
        if readinto:
            self.readinto = self._readinto

    def read(self, count):
        if self.error is not None:
            raise self.error
        if self.chunk_limit is not None:
            count = min(count, self.chunk_limit)
        return self.stream.read(count)

    def _readinto(self, buffer):
        if self.error is not None:
            raise self.error
        if self.chunk_limit is not None:
            buffer = memoryview(buffer)[:self.chunk_limit]
        return self.stream.readinto(buffer)

    def seek(self, offset, whence=0):
        return self.stream.seek(offset, whence)

    def tell(self):
        return self.stream.tell()


def read_audio(audio, api):
    if api == 'read':
        return audio.read(4, dtype='int16', always_2d=True)
    if api == 'buffer_read':
        return audio.buffer_read(4, dtype='int16')
    if api == 'buffer_read_into':
        return audio.buffer_read_into(bytearray(4 * audio.channels * 2),
                                      dtype='int16')
    return next(audio.blocks(blocksize=4, dtype='int16'))


@pytest.mark.parametrize('readinto', [False, True])
@pytest.mark.parametrize('channels', [1, 2])
@pytest.mark.parametrize('api', ['read', 'buffer_read', 'buffer_read_into',
                                 'blocks'])
def test_read_oserror_reaches_caller(readinto, channels, api, monkeypatch):
    data, samples = wav_data(channels)
    reader = Reader(data, readinto)
    unraisable = []
    monkeypatch.setattr(sys, 'unraisablehook', unraisable.append)
    with sf.SoundFile(reader) as audio:
        error = OSError(5, 'injected audio read failure')
        reader.error = error
        with pytest.raises(OSError) as caught:
            read_audio(audio, api)
        assert caught.value is error
        assert caught.value.errno == 5
        assert unraisable == []
        # Consuming the error must not poison a later successful read.
        reader.error = None
        audio.seek(0)
        np.testing.assert_array_equal(
            audio.read(4, dtype='int16', always_2d=True), samples[:4])


@pytest.mark.parametrize('readinto', [False, True])
def test_open_read_oserror_reaches_caller(readinto, monkeypatch):
    data, _ = wav_data(1)
    reader = Reader(data, readinto)
    reader.error = OSError(5, 'injected header read failure')
    unraisable = []
    monkeypatch.setattr(sys, 'unraisablehook', unraisable.append)
    with pytest.raises(OSError) as caught:
        sf.SoundFile(reader)
    assert caught.value is reader.error
    assert unraisable == []


@pytest.mark.parametrize('readinto', [False, True])
@pytest.mark.parametrize('channels', [1, 2])
def test_successful_read_and_eof(readinto, channels):
    data, samples = wav_data(channels)
    with sf.SoundFile(Reader(data, readinto)) as audio:
        np.testing.assert_array_equal(
            audio.read(99, dtype='int16', always_2d=True), samples)
        assert audio.read(4, dtype='int16', always_2d=True).shape == (0, channels)


def test_read_errors_are_isolated_between_files():
    data, samples = wav_data(1)
    reader = Reader(data, True)
    with sf.SoundFile(reader) as failing, sf.SoundFile(io.BytesIO(data)) as good:
        reader.error = OSError(5, 'only the first file fails')
        with pytest.raises(OSError):
            failing.read(4)
        np.testing.assert_array_equal(
            good.read(4, dtype='int16', always_2d=True), samples[:4])


@pytest.mark.parametrize('readinto', [False, True])
@pytest.mark.parametrize('channels', [1, 2])
def test_short_read_without_error(readinto, channels):
    data, samples = wav_data(channels)
    reader = Reader(data, readinto)
    with sf.SoundFile(reader) as audio:
        reader.chunk_limit = 2 * channels * 2  # Two complete PCM frames.
        np.testing.assert_array_equal(
            audio.read(4, dtype='int16', always_2d=True), samples[:2])


@pytest.mark.parametrize('readinto', [False, True])
def test_nonseekable_audio_read_error(readinto):
    encoded = io.BytesIO()
    sf.write(encoded, np.arange(32, dtype='int16'), 16000, format='XI')
    reader = Reader(encoded.getvalue(), readinto)
    with sf.SoundFile(reader) as audio:
        assert not audio.seekable()
        reader.error = OSError(5, 'non-seekable audio read failed')
        with pytest.raises(OSError) as caught:
            audio.read(4)
        assert caught.value is reader.error


def test_callback_does_not_keep_closed_soundfile_alive():
    data, _ = wav_data(1)
    reader = Reader(data, True)
    audio = sf.SoundFile(reader)
    reference = weakref.ref(audio)
    reader.error = OSError(5, 'read failed')
    try:
        audio.read(4)
    except OSError:
        pass
    reader.error = None
    audio.close()
    del audio
    gc.collect()
    assert reference() is None
