"""Make sure that arguments of open/read/write don't diverge."""

import pytest
import soundfile as sf
import sys


pytestmark = pytest.mark.skipif(sys.version_info < (3, 3),
                                reason="signature module requires Python 3.3")


def defaults(func):
    from inspect import signature
    return dict((k, v) for k, v in signature(func).parameters.items()
                if v.default is not v.empty)


def remove_items(collection, subset):
    """From a collection of defaults, remove a subset and return the rest."""
    the_rest = collection.copy()
    for name, param in subset.items():
        assert (name, the_rest[name].default) == (name, param.default)
        del the_rest[name]
    return the_rest


def test_read_defaults():
    func_defaults = defaults(sf.read)
    meth_defaults = defaults(sf.SoundFile.read)
    init_defaults = defaults(sf.SoundFile.__init__)

    del init_defaults['mode']  # mode is always 'r'

    del func_defaults['start']
    del func_defaults['stop']

    # Same default values as SoundFile.__init__() and SoundFile.read():
    for spec in init_defaults, meth_defaults:
        func_defaults = remove_items(func_defaults, spec)

    assert not func_defaults  # No more arguments should be left


def test_write_defaults():
    write_defaults = defaults(sf.write)
    init_defaults = defaults(sf.SoundFile.__init__)

    # Same default values as SoundFile.__init__()
    init_defaults = remove_items(init_defaults, write_defaults)

    del init_defaults['mode']  # mode is always 'x' or 'w'
    del init_defaults['channels']  # Inferred from data
    del init_defaults['samplerate']  # Obligatory in write()
    assert not init_defaults  # No more arguments should be left


def test_if_blocks_function_and_method_have_same_defaults():
    func_defaults = defaults(sf.blocks)
    meth_defaults = defaults(sf.SoundFile.blocks)
    init_defaults = defaults(sf.SoundFile.__init__)

    del func_defaults['start']
    del func_defaults['stop']
    del init_defaults['mode']

    for spec in init_defaults, meth_defaults:
        func_defaults = remove_items(func_defaults, spec)

    assert not func_defaults


def test_order_of_blocks_arguments():
    from inspect import signature

    # remove 'self':
    meth_args = list(signature(sf.SoundFile.blocks).parameters)[1:]
    meth_args[3:3] = ['start', 'stop']
    func_args = list(signature(sf.blocks).parameters)
    assert func_args[:10] == ['file'] + meth_args
