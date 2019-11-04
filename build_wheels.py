#!/usr/bin/env python
import sys
import subprocess
import shutil

def make_dist(platform, arch, dist):
    print("removing 'SoundFile.egg-info' (and everything under it)")
    shutil.rmtree('SoundFile.egg-info', ignore_errors=True)
    subprocess.run([sys.executable, 'setup.py', 'clean', '--all'])
    subprocess.run([sys.executable, 'setup.py', dist], env={
        'PYSOUNDFILE_PLATFORM': platform,
        'PYSOUNDFILE_ARCHITECTURE': arch
    })

if __name__ == '__main__':
    make_dist('darwin', '64bit', 'bdist_wheel')
    make_dist('win32', '32bit', 'bdist_wheel')
    make_dist('win32', '64bit', 'bdist_wheel')
    make_dist('', '', 'bdist_wheel')
    make_dist('', '', 'sdist')
