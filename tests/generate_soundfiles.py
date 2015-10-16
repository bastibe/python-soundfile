#!/usr/bin/env python

import struct


def uint32(number):
    return struct.pack('<I', number)


def uint16(number):
    return struct.pack('<H', number)


mono_raw = struct.pack('<5h', 0, 1, 2, -2, -1)

# floating point data is typically limited to the interval [-1.0, 1.0],
# but smaller/larger values are supported as well
stereo_raw = struct.pack('<8f',
                         1.75, -1.75,
                         1.0,  -1.0,
                         0.5,  -0.5,
                         0.25, -0.25)

mono_data = (
    b'RIFF' +
    uint32(46) +  # size

    b'WAVE' +  # file type

    b'fmt ' +
    uint32(16) +  # chunk size
    uint16(1) +  # data type (PCM)
    uint16(1) +  # channels
    uint32(44100) +  # samplerate
    uint32(44100 * 2) +  # bytes per second
    uint16(2) +  # frame size
    uint16(16) +  # bits per sample

    b'data' +
    uint32(5 * 2) +  # chunk size
    mono_raw
)

stereo_data = (
    b'RIFF' +
    uint32(80) +  # size

    b'WAVE' +  # file type

    b'fmt ' +
    uint32(16) +  # chunk size
    uint16(3) +  # data type (float)
    uint16(2) +  # channels
    uint32(44100) +  # samplerate
    uint32(44100 * 2 * 4) +  # bytes per second
    uint16(2 * 4) +  # frame size
    uint16(32) +  # bits per sample

    b'fact' +
    uint32(4) +  # chunk size
    uint32(4) +  # number of frames

    b'data' +
    uint32(8 * 4) +  # chunk size
    stereo_raw
)

with open('stereo.wav', 'wb') as f:
    f.write(stereo_data)

with open('mono.wav', 'wb') as f:
    f.write(mono_data)

with open('mono.raw', 'wb') as f:
    f.write(mono_raw)
