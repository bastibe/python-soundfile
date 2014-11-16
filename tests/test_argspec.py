"""Make sure that arguments of open/read/write don't diverge."""

import pysoundfile as sf
from inspect import getargspec


init = getargspec(sf.SoundFile.__init__)
read_function = getargspec(sf.read)
read_method = getargspec(sf.SoundFile.read)
write_function = getargspec(sf.write)
blocks_function = getargspec(sf.blocks)
blocks_method = getargspec(sf.SoundFile.blocks)


def defaults(spec):
    return dict(zip(reversed(spec.args), reversed(spec.defaults)))


def remove_items(collection, subset):
    """From a collection of defaults, remove a subset and return the rest."""
    the_rest = collection.copy()
    for arg, default in subset.items():
        assert (arg, the_rest[arg]) == (arg, default)
        del the_rest[arg]
    return the_rest


def test_read_defaults():
    func_defaults = defaults(read_function)
    meth_defaults = defaults(read_method)
    init_defaults = defaults(init)

    del init_defaults['mode']  # Not meaningful in read() function:

    del func_defaults['start']
    del func_defaults['stop']

    # Same default values as SoundFile.__init__() and SoundFile.read():
    for spec in init_defaults, meth_defaults:
        func_defaults = remove_items(func_defaults, spec)

    assert not func_defaults  # No more arguments should be left


def test_write_defaults():
    write_defaults = defaults(write_function)
    init_defaults = defaults(init)

    # Same default values as SoundFile.__init__()
    init_defaults = remove_items(init_defaults, write_defaults)

    del init_defaults['mode']  # mode is always 'w'
    del init_defaults['channels']  # Inferred from data
    del init_defaults['samplerate']  # Obligatory in write()
    assert not init_defaults  # No more arguments should be left


def test_if_blocks_function_and_method_have_same_defaults():
    func_defaults = defaults(blocks_function)
    meth_defaults = defaults(blocks_method)
    init_defaults = defaults(init)

    del func_defaults['start']
    del func_defaults['stop']
    del init_defaults['mode']

    for spec in init_defaults, meth_defaults:
        func_defaults = remove_items(func_defaults, spec)

    assert not func_defaults


def test_order_of_blocks_arguments():
    # Only the first few are checked
    meth_args = blocks_method.args[1:]  # remove 'self'
    meth_args[3:3] = ['start', 'stop']
    assert blocks_function.args[:10] == ['file'] + meth_args
