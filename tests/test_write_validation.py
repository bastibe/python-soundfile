import io

import numpy as np
import pytest

import soundfile as sf


@pytest.mark.parametrize('shape', [(), (2, 2, 2), (2, 2, 2, 2)])
@pytest.mark.parametrize('destination', ['new', 'existing', 'filelike'])
def test_invalid_write_dimensions_leave_destination_untouched(
        tmp_path, shape, destination):
    """Reject invalid dimensions before creating or changing the destination."""
    target = tmp_path / 'audio.wav'
    original = io.BytesIO()
    sf.write(original, np.array([0.25, -0.5]), 8000, format='WAV')
    snapshot = original.getvalue()
    if destination == 'existing':
        target.write_bytes(snapshot)
    elif destination == 'filelike':
        target = original
        target.seek(0)

    with pytest.raises(ValueError, match='Invalid shape'):
        sf.write(target, np.zeros(shape), 8000, format='WAV')

    if destination == 'new':
        assert not target.exists()
    elif destination == 'existing':
        assert target.read_bytes() == snapshot
    else:
        assert target.getvalue() == snapshot
        assert target.tell() == 0
