import os

def make_wheel(platform, arch, dist):
    os.system('python setup.py clean --all')
    os.environ['PYSOUNDFILE_PLATFORM'] = platform
    os.environ['PYSOUNDFILE_ARCHITECTURE'] = arch
    os.system(f'python setup.py {dist}')

if __name__ == '__main__':
    make_wheel('darwin', '64bit', 'bdist_wheel')
    make_wheel('win32', '32bit', 'bdist_wheel')
    make_wheel('win32', '64bit', 'bdist_wheel')
    make_wheel('', '', 'bdist_wheel')
    make_wheel('', '', 'sdist')
