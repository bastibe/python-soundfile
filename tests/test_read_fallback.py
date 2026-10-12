import io

import numpy as np
import pytest
from numpy.testing import assert_array_equal

import soundfile as sf


class ReadAdapter(io.RawIOBase):
    def __init__(self, contents):
        self.source = io.BytesIO(contents)
        self.read_calls = 0

    def read(self, size=-1):
        self.read_calls += 1
        return self.source.read(size)

    def seek(self, offset, whence=0):
        return self.source.seek(offset, whence)

    def tell(self):
        return self.source.tell()

    def readable(self):
        return True

    def seekable(self):
        return True


@pytest.mark.parametrize('format', ['WAV', 'FLAC'])
@pytest.mark.parametrize('channels', [1, 2])
def test_virtual_io_read_adapter_with_unimplemented_readinto(format, channels):
    values = np.array([1, 256, -2345, 42], dtype='int16')
    if channels == 2:
        values = np.column_stack((values, -values))
    encoded = io.BytesIO()
    sf.write(encoded, values, 8000, format=format, subtype='PCM_16')
    adapter = ReadAdapter(encoded.getvalue())
    # The inherited method exists, but is not implemented by this adapter.
    with pytest.raises(NotImplementedError):
        adapter.readinto(bytearray(1))
    decoded, rate = sf.read(adapter, dtype='int16')
    assert rate == 8000
    assert_array_equal(decoded, values)
    assert adapter.read_calls > 0


def test_virtual_io_prefers_working_readinto():
    class ReadIntoAdapter(ReadAdapter):
        def readinto(self, buffer):
            return self.source.readinto(buffer)

    values = np.array([1, 256, -2345, 42], dtype='int16')
    encoded = io.BytesIO()
    sf.write(encoded, values, 8000, format='WAV', subtype='PCM_16')
    adapter = ReadIntoAdapter(encoded.getvalue())
    decoded, _ = sf.read(adapter, dtype='int16')
    assert_array_equal(decoded, values)
    assert adapter.read_calls == 0
