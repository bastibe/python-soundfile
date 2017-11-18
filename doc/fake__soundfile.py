"""Mock module for Sphinx autodoc."""

import ctypes

# Monkey-patch ctypes to disable searching for libsndfile
ctypes.util.find_library = lambda _: NotImplemented


class ffi(object):

    def dlopen(self, _):
        return self

    def string(self, _):
        return b'not implemented'

    def sf_version_string(self):
        return NotImplemented

    SFC_GET_FORMAT_INFO = NotImplemented


ffi = ffi()
