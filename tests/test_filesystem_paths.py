import errno
import os
import wave
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_array_equal

import soundfile as sf


@pytest.mark.skipif(os.name == 'nt', reason='POSIX byte paths use surrogateescape')
@pytest.mark.parametrize('path_type', [str, Path])
def test_filesystem_byte_path_roundtrip(tmp_path, path_type):
    raw_name = os.fsencode(tmp_path) + b'/caf\xe9.wav'
    name = os.fsdecode(raw_name)
    if os.fsencode(name) != raw_name or not any(0xDC80 <= ord(c) <= 0xDCFF for c in name):
        pytest.skip('filesystem encoding represents this filename without surrogateescape')
    # Check filesystem support independently before testing SoundFile's codec.
    try:
        with open(raw_name, 'xb'):
            pass
    except OSError as error:
        if error.errno in (errno.EINVAL, errno.EILSEQ):
            pytest.skip('filesystem does not support this byte filename')
        raise
    path = path_type(name)
    samples = np.array([0, 1, 256, -2345], dtype='int16')
    sf.write(path, samples, 16000)
    discovered = path_type(tmp_path / os.listdir(tmp_path)[0])
    actual, rate = sf.read(discovered, dtype='int16')
    assert_array_equal(actual, samples)
    assert rate == 16000
    assert sf.info(discovered).frames == len(samples)
    with wave.open(name, 'rb') as f:
        assert_array_equal(np.frombuffer(f.readframes(len(samples)), dtype='<i2'), samples)
