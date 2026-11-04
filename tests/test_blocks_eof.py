import io

import numpy as np
import pytest
from numpy.testing import assert_array_equal

import soundfile as sf


@pytest.mark.parametrize('use_out', [False, True])
@pytest.mark.parametrize('size, frames, overlap, ranges', [
    (10, 16, 0, [(0, 4), (4, 8), (8, 10)]),
    (9, 16, 2, [(0, 4), (2, 6), (4, 8), (6, 9)]),
    (8, 16, 0, [(0, 4), (4, 8)]),
    (1, 2, 0, [(0, 1)]),
    (0, 8, 0, []),
])
def test_blocks_non_seekable_eof(use_out, size, frames, overlap, ranges):
    values = np.arange(size, dtype='int16') - 4
    encoded = io.BytesIO()
    sf.write(encoded, values, 16000, format='XI', subtype='DPCM_16')
    encoded.seek(0)
    out = np.full(4, 12345, dtype='int16')
    options = {'out': out} if use_out else {'blocksize': 4}

    with sf.SoundFile(encoded) as source:
        assert not source.seekable()
        blocks = []
        for block in source.blocks(frames=frames, overlap=overlap,
                                   dtype='int16', **options):
            if use_out:
                assert np.shares_memory(block, out)
            blocks.append(block.copy())

    assert len(blocks) == len(ranges)
    for block, (start, stop) in zip(blocks, ranges):
        assert_array_equal(block, values[start:stop])


def test_blocks_function_non_seekable_eof():
    values = np.array([123, -456, 789, -1234, 5678], dtype='int16')
    encoded = io.BytesIO()
    sf.write(encoded, values, 16000, format='XI', subtype='DPCM_16')
    encoded.seek(0)
    blocks = list(sf.blocks(encoded, blocksize=4, frames=16, dtype='int16'))
    assert [len(block) for block in blocks] == [4, 1]
    assert_array_equal(np.concatenate(blocks), values)


def test_blocks_non_seekable_explicit_fill():
    values = np.array([123, -456, 789, -1234, 5678], dtype='int16')
    encoded = io.BytesIO()
    sf.write(encoded, values, 16000, format='XI', subtype='DPCM_16')
    encoded.seek(0)
    with sf.SoundFile(encoded) as source:
        blocks = list(source.blocks(blocksize=4, frames=12,
                                    dtype='int16', fill_value=42))
    assert_array_equal(np.concatenate(blocks),
                       np.concatenate([values, np.full(7, 42, dtype='int16')]))
