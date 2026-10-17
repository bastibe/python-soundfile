import gc
import os

import numpy as np
import pytest
from numpy.testing import assert_array_equal

import soundfile as sf


@pytest.mark.parametrize('dtype', ['int16', 'int32', 'float32', 'float64'])
def test_buffer_read_nonseekable_short_final_block(tmp_path, dtype):
    filename = str(tmp_path / 'sample.xi')
    samples = np.array([0, 1, 2, -2, -1], dtype='int16')
    sf.write(filename, samples, 44100, subtype='DPCM_16')
    with sf.SoundFile(filename) as f:
        assert not f.seekable()
        expected = f.read(99, dtype=dtype)
    with sf.SoundFile(filename) as f:
        first = f.buffer_read(3, dtype=dtype)
        final = f.buffer_read(99, dtype=dtype)
        empty = f.buffer_read(99, dtype=dtype)
    # Returned buffers must keep their native allocations alive after close/GC.
    gc.collect()
    assert_array_equal(np.frombuffer(first, dtype=dtype), expected[:3])
    assert_array_equal(np.frombuffer(final, dtype=dtype), expected[3:])
    assert len(empty) == 0


@pytest.mark.skipif(os.name == 'nt', reason='pipe file descriptors require POSIX')
def test_buffer_read_stereo_pipe():
    samples = np.array([[1, -1], [256, -256], [2345, -2345]], dtype='int16')
    reader, writer = os.pipe()
    try:
        os.write(writer, samples.tobytes())
    finally:
        os.close(writer)
    with os.fdopen(reader, 'rb') as pipe:
        with sf.SoundFile(pipe.fileno(), format='RAW', subtype='PCM_16',
                          samplerate=16000, channels=2, endian='CPU', closefd=False) as f:
            assert not f.seekable()
            data = f.buffer_read(99, dtype='int16')
            assert len(f.buffer_read(99, dtype='int16')) == 0
    assert_array_equal(np.frombuffer(data, dtype='int16').reshape(-1, 2), samples)
