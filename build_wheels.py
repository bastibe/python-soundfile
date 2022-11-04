import os
import shutil

architectures = dict(darwin=['x86_64', 'arm64'],
                     win32=['32bit', '64bit'],
                     linux=['x86_64'],
                     noplatform='noarch')

def cleanup():
    os.environ['PYSOUNDFILE_PLATFORM'] = ''
    os.environ['PYSOUNDFILE_ARCHITECTURE'] = ''
    shutil.rmtree('build', ignore_errors=True)
    shutil.rmtree('soundfile.egg-info', ignore_errors=True)
    try:
        os.remove('_soundfile.py')
    except:
        pass

for platform, archs in architectures.items():
    for arch in archs:
        os.environ['PYSOUNDFILE_PLATFORM'] = platform
        os.environ['PYSOUNDFILE_ARCHITECTURE'] = arch
        os.system('python3 setup.py bdist_wheel')
        cleanup()

os.system('python3 setup.py sdist')
cleanup()
