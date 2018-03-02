import os
import shutil

architectures = dict(darwin=['64bit'],
                     win32=['32bit', '64bit'],
                     noplatform='noarch')

def cleanup():
    shutil.rmtree('build', ignore_errors=True)
    try:
        os.remove('_soundfile.py')
    except:
        pass

for platform, archs in architectures.items():
    os.environ['PYSOUNDFILE_PLATFORM'] = platform
    for arch in archs:
        os.environ['PYSOUNDFILE_ARCHITECTURE'] = arch
        cleanup()
        os.system('python setup.py bdist_wheel')

cleanup()
os.system('python setup.py sdist')
