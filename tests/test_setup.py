"""Keep wheel platform tags and bundled library selection consistent."""

import os
import platform
import runpy
import sys
import sysconfig
from pathlib import Path
from types import ModuleType

import pytest
import setuptools


def setup_options(monkeypatch, host, python_platform, machine, bits,
                  target=None, architecture=None, packaged=True):
    root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(root)
    monkeypatch.setattr(sys, 'platform', host)
    monkeypatch.setattr(sysconfig, 'get_platform', lambda: python_platform)
    monkeypatch.setattr(platform, 'machine', lambda: machine)
    monkeypatch.setattr(platform, 'architecture', lambda: (bits, ''))
    for name, value in [('PYSOUNDFILE_PLATFORM', target),
                        ('PYSOUNDFILE_ARCHITECTURE', architecture)]:
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    original_isdir = os.path.isdir
    monkeypatch.setattr(os.path, 'isdir', lambda path:
                        packaged if path == '_soundfile_data' else original_isdir(path))
    options = {}
    monkeypatch.setattr(setuptools, 'setup', lambda **kwargs: options.update(kwargs))
    wheel_command = ModuleType('wheel.bdist_wheel')
    wheel_command.bdist_wheel = object
    monkeypatch.setitem(sys.modules, 'wheel.bdist_wheel', wheel_command)
    namespace = runpy.run_path(str(root / 'setup.py'))
    return namespace, options


@pytest.mark.parametrize('python_platform,machine,bits,library,tag', [
    ('win32', 'AMD64', '32bit', 'libsndfile_x86.dll', 'win32'),
    ('win-amd64', 'AMD64', '64bit', 'libsndfile_x64.dll', 'win_amd64'),
    ('win-arm64', 'ARM64', '64bit', 'libsndfile_arm64.dll', 'win_arm64'),
    ('win-amd64', 'ARM64', '64bit', 'libsndfile_x64.dll', 'win_amd64'),
])
def test_default_windows_architecture(monkeypatch, python_platform, machine,
                                      bits, library, tag):
    namespace, options = setup_options(monkeypatch, 'win32', python_platform,
                                       machine, bits)
    assert namespace['libname'] == library
    assert options['package_data']['_soundfile_data'] == [library, 'COPYING']
    assert options['zip_safe'] is False
    assert options['cmdclass']['bdist_wheel'].get_tag(None) == ('py2.py3', 'none', tag)


@pytest.mark.parametrize('target,architecture,machine,library,tag', [
    ('win32', 'x64', 'ARM64', 'libsndfile_x64.dll', 'win_amd64'),
    ('win32', 'x86', 'ARM64', 'libsndfile_x86.dll', 'win32'),
    ('win32', 'arm64', 'AMD64', 'libsndfile_arm64.dll', 'win_arm64'),
    ('win32', '64bit', 'AMD64', 'libsndfile_64bit.dll', 'win_amd64'),
    ('win32', '32bit', 'AMD64', 'libsndfile_32bit.dll', 'win32'),
    ('darwin', 'x86_64', 'AMD64', 'libsndfile_x86_64.dylib', 'macosx_10_9_x86_64'),
    ('darwin', 'arm64', 'AMD64', 'libsndfile_arm64.dylib', 'macosx_11_0_arm64'),
    ('linux', 'x86_64', 'AMD64', 'libsndfile_x86_64.so', 'manylinux_2_28_x86_64'),
    ('linux', 'arm64', 'AMD64', 'libsndfile_arm64.so', 'manylinux_2_28_aarch64'),
])
def test_explicit_target(monkeypatch, target, architecture, machine, library, tag):
    namespace, options = setup_options(monkeypatch, 'win32', 'win-amd64',
                                       machine, '64bit', target, architecture)
    assert namespace['architecture0'] == architecture
    assert namespace['libname'] == library
    assert options['package_data']['_soundfile_data'] == [library, 'COPYING']
    assert options['cmdclass']['bdist_wheel'].get_tag(None) == ('py2.py3', 'none', tag)


@pytest.mark.parametrize('host,machine,library', [
    ('darwin', 'x86_64', 'libsndfile_x86_64.dylib'),
    ('darwin', 'arm64', 'libsndfile_arm64.dylib'),
    ('linux', 'x86_64', 'libsndfile_x86_64.so'),
])
def test_default_non_windows_architecture(monkeypatch, host, machine, library):
    namespace, _ = setup_options(monkeypatch, host, host, machine, '64bit')
    assert namespace['libname'] == library


@pytest.mark.parametrize('target,packaged', [('noplatform', True), ('win32', False)])
def test_without_packaged_library(monkeypatch, target, packaged):
    _, options = setup_options(monkeypatch, 'win32', 'win-amd64', 'AMD64',
                               '64bit', target, 'x64', packaged)
    assert options['packages'] is None
    assert options['package_data'] is None
    assert options['zip_safe'] is True
