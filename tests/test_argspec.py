"""Make sure that arguments of open/read/write don't diverge"""

import pysoundfile as sf
from inspect import getargspec


open = getargspec(sf.open)
init = getargspec(sf.SoundFile.__init__)
read_function = getargspec(sf.read)
read_method = getargspec(sf.SoundFile.read)
write_function = getargspec(sf.write)


def defaults(spec):
    return dict(zip(reversed(spec.args), reversed(spec.defaults)))


def test_if_open_is_identical_to_init():
    assert ['self'] + open.args == init.args
    assert open.varargs == init.varargs
    assert open.keywords == init.keywords
    assert open.defaults == init.defaults


def test_read_function():
    func_defaults = defaults(read_function)
    meth_defaults = defaults(read_method)
    open_defaults = defaults(open)

    # Not meaningful in read() function:
    del open_defaults['mode']

    # Only in read() function:
    del func_defaults['start']
    del func_defaults['stop']

    # Same default values as open() and SoundFile.read():
    for spec in open_defaults, meth_defaults:
        for arg, default in spec.items():
            assert (arg, func_defaults[arg]) == (arg, default)
            del func_defaults[arg]

    assert not func_defaults  # No more arguments should be left


def test_write_function():
    write_defaults = defaults(write_function)
    open_defaults = defaults(open)

    # Same default values as open():
    for arg, default in write_defaults.items():
        assert (arg, open_defaults[arg]) == (arg, default)
        del open_defaults[arg]

    del open_defaults['mode']  # mode is always 'w'
    del open_defaults['channels']  # Inferred from data
    del open_defaults['sample_rate']  # Obligatory in write()

    assert not open_defaults  # No more arguments should be left
