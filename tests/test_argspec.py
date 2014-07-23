"""Make sure that arguments of open/read/write don't diverge."""

import pysoundfile as sf
from inspect import getargspec


open = getargspec(sf.open)
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


def test_if_open_is_identical_to_init():
    assert ['self'] + open.args == init.args
    assert open.varargs == init.varargs
    assert open.keywords == init.keywords
    assert open.defaults == init.defaults


def test_read_defaults():
    func_defaults = defaults(read_function)
    meth_defaults = defaults(read_method)
    open_defaults = defaults(open)

    del open_defaults['mode']  # Not meaningful in read() function:

    del func_defaults['start']
    del func_defaults['stop']

    # Same default values as open() and SoundFile.read():
    for spec in open_defaults, meth_defaults:
        func_defaults = remove_items(func_defaults, spec)

    assert not func_defaults  # No more arguments should be left


def test_write_defaults():
    write_defaults = defaults(write_function)
    open_defaults = defaults(open)

    # Same default values as open()
    open_defaults = remove_items(open_defaults, write_defaults)

    del open_defaults['mode']  # mode is always 'w'
    del open_defaults['channels']  # Inferred from data
    del open_defaults['sample_rate']  # Obligatory in write()
    assert not open_defaults  # No more arguments should be left


def test_if_blocks_function_and_method_have_same_defaults():
    func_defaults = defaults(blocks_function)
    meth_defaults = defaults(blocks_method)
    open_defaults = defaults(open)

    del func_defaults['start']
    del func_defaults['stop']
    del open_defaults['mode']

    for spec in open_defaults, meth_defaults:
        func_defaults = remove_items(func_defaults, spec)

    assert not func_defaults


def test_order_of_blocks_arguments():
    meth_args = blocks_method.args[1:]  # remove 'self'
    meth_args[2:2] = ['start', 'stop']
    open_args = open.args[:]
    open_args.remove('mode')
    assert blocks_function.args == open_args + meth_args
