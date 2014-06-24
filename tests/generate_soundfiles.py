#!/usr/bin/env python3

import platform
import numpy as np
from scipy.io import wavfile

# SciPy >= 0.13 is needed for 32-bit floating point support

wavfile.write('stereo.wav', 44100, np.array([[1.0,  -1.0],
                                             [0.75, -0.75],
                                             [0.5,  -0.5],
                                             [0.25, -0.25]], dtype='float32'))

wavfile.write('mono.wav', 44100, np.array([0, 1, 2, -2, -1], dtype='int16'))

platform.subprocess.call(['sox', 'mono.wav', 'mono.raw'])
