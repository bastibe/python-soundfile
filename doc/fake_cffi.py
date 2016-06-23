"""Mock module for Sphinx autodoc."""


class FFI(object):

    def cdef(self, _):
        pass

    def dlopen(self, _):
        return self

    def string(self, _):
        return b'not implemented'

    def sf_version_string(self):
        return NotImplemented

    SFC_GET_FORMAT_INFO = NotImplemented
