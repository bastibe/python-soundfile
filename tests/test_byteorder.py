import io
import sys

import numpy as np
import pytest
from numpy.testing import assert_array_equal

import soundfile as sf


@pytest.mark.parametrize(
    'dtype,subtype',
    [
        ('int16', 'PCM_16'),
        ('int32', 'PCM_32'),
        ('float32', 'FLOAT'),
        ('float64', 'DOUBLE'),
    ],
)
@pytest.mark.parametrize('channels', [1, 2])
@pytest.mark.parametrize('strided', [False, True])
def test_write_non_native_endian_preserves_samples(dtype, subtype, channels, strided):
    order = '>' if sys.byteorder == 'little' else '<'
    values = (
        np.array([1, 256, -2345, 42], dtype=dtype)
        if dtype.startswith('int')
        else np.array([0.25, 0.5, -0.75, 0.125], dtype=dtype)
    )
    if channels == 2:
        values = np.column_stack((values, -values))
    swapped = values.astype(np.dtype(dtype).newbyteorder(order))
    if strided:
        backing = np.empty((len(values) * 2,) + values.shape[1:], dtype=swapped.dtype)
        backing[::2] = swapped
        swapped = backing[::2]
    snapshot = swapped.tobytes()
    output = io.BytesIO()
    sf.write(output, swapped, 8000, format='WAV', subtype=subtype)
    output.seek(0)
    decoded, _ = sf.read(output, dtype=dtype)
    assert_array_equal(decoded, values)
    assert swapped.tobytes() == snapshot


@pytest.mark.parametrize(
    'dtype,subtype',
    [
        ('int16', 'PCM_16'),
        ('int32', 'PCM_32'),
        ('float32', 'FLOAT'),
        ('float64', 'DOUBLE'),
    ],
)
@pytest.mark.parametrize('channels', [1, 2])
@pytest.mark.parametrize('fill', [None, 17])
def test_read_non_native_endian_out_rejected_without_mutation(
    dtype, subtype, channels, fill
):
    order = '>' if sys.byteorder == 'little' else '<'
    values = (
        np.array([1, 256, -2345, 42], dtype=dtype)
        if dtype.startswith('int')
        else np.array([0.25, 0.5, -0.75, 0.125], dtype=dtype)
    )
    if channels == 2:
        values = np.column_stack((values, -values))
    output = io.BytesIO()
    sf.write(output, values, 8000, format='WAV', subtype=subtype)
    output.seek(0)
    shape = (6,) if channels == 1 else (6, 2)
    out = np.full(shape, 23, dtype=np.dtype(dtype).newbyteorder(order))
    snapshot = out.tobytes()
    with sf.SoundFile(output) as file:
        with pytest.raises(ValueError, match='native byte order'):
            file.read(out=out, fill_value=fill)
        assert file.tell() == 0
    assert out.tobytes() == snapshot
