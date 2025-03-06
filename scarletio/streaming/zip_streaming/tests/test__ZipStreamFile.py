from datetime import datetime as DateTime, timezone as TimeZone

import vampytest

from ..constants import COMPRESSION_METHOD_DEFLATE, COMPRESSION_METHOD_NONE
from ..file import ZipStreamFile

from .resources import AsyncGenerator


def _assert_fields_set(file):
    """
    Asserts whether every field is set.
    
    Parameters
    ----------
    file : ``ZipStreamFile``
        The file to check.
    """
    vampytest.assert_instance(file, ZipStreamFile)
    vampytest.assert_instance(file.async_generator, object)
    vampytest.assert_instance(file.compression_method, int)
    vampytest.assert_instance(file.modified_at, DateTime)
    vampytest.assert_instance(file.name, str)


def test__ZipStreamFile__new__min_fields():
    """
    Tests whether ``ZipStreamFile.__new__`` works as intended.
    
    Case: minimal amount of fields given.
    """
    async_generator = AsyncGenerator([b'aya'])
    name = 'koishi'
    
    file = ZipStreamFile(name, async_generator)
    _assert_fields_set(file)
    
    vampytest.assert_is(file.async_generator, async_generator)
    vampytest.assert_eq(file.name, name)


def test__ZipStreamFile__new__all_fields():
    """
    Tests whether ``ZipStreamFile.__new__`` works as intended.
    
    Case: all fields given.
    """
    async_generator = AsyncGenerator([b'aya'])
    compression_method = COMPRESSION_METHOD_DEFLATE
    modified_at = DateTime(2016, 5, 14, tzinfo = TimeZone.utc)
    name = 'koishi'
    
    file = ZipStreamFile(name, async_generator, compression_method = compression_method, modified_at = modified_at)
    _assert_fields_set(file)
    
    vampytest.assert_is(file.async_generator, async_generator)
    vampytest.assert_eq(file.compression_method, compression_method)
    vampytest.assert_eq(file.modified_at, modified_at)
    vampytest.assert_eq(file.name, name)


def test__ZipStreamFile__repr():
    """
    Tests whether ``ZipStreamFile.__repr__`` works as intended.
    """
    async_generator = AsyncGenerator([b'aya'])
    name = 'koishi'
    
    file = ZipStreamFile(name, async_generator)
    
    output = repr(file)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    async_generator_0 = AsyncGenerator([b'aya'])
    async_generator_1 = AsyncGenerator([b'ayaya'])
    
    modified_at_0 = DateTime(2016, 5, 14, tzinfo = TimeZone.utc)
    modified_at_1 = DateTime(2016, 5, 13, tzinfo = TimeZone.utc)
    
    yield (
        ('hatate.txt', async_generator_0),
        {'compression_method': COMPRESSION_METHOD_NONE, 'modified_at': modified_at_0},
        ('hatate.txt', async_generator_0),
        {'compression_method': COMPRESSION_METHOD_NONE, 'modified_at': modified_at_0},
        True,
    )
    
    yield (
        ('hatate.txt', async_generator_0),
        {'compression_method': COMPRESSION_METHOD_NONE, 'modified_at': modified_at_0},
        ('koishi.txt', async_generator_0),
        {'compression_method': COMPRESSION_METHOD_NONE, 'modified_at': modified_at_0},
        False,
    )
    
    yield (
        ('hatate.txt', async_generator_0),
        {'compression_method': COMPRESSION_METHOD_NONE, 'modified_at': modified_at_0},
        ('hatate.txt', async_generator_1),
        {'compression_method': COMPRESSION_METHOD_NONE, 'modified_at': modified_at_0},
        False,
    )
    
    yield (
        ('hatate.txt', async_generator_0),
        {'compression_method': COMPRESSION_METHOD_NONE, 'modified_at': modified_at_0},
        ('hatate.txt', async_generator_0),
        {'compression_method': COMPRESSION_METHOD_DEFLATE, 'modified_at': modified_at_0},
        False,
    )
    
    yield (
        ('hatate.txt', async_generator_0),
        {'compression_method': COMPRESSION_METHOD_NONE, 'modified_at': modified_at_0},
        ('hatate.txt', async_generator_0),
        {'compression_method': COMPRESSION_METHOD_NONE, 'modified_at': modified_at_1},
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__ZipStreamFile__eq(
    positional_parameters_0, keyword_parameters_0, positional_parameters_1, keyword_parameters_1
):
    """
    Tests whether ``ZipStreamFile.__eq__`` works as intended.
    
    Parameters
    ----------
    positional_parameters_0 : `tuple<object>`
        Positional parameters to create instance with.
    
    keyword_parameters_0 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    positional_parameters_1 : `tuple<object>`
        Positional parameters to create instance with.
    
    keyword_parameters_1 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    file_0 = ZipStreamFile(*positional_parameters_0, **keyword_parameters_0)
    file_1 = ZipStreamFile(*positional_parameters_1, **keyword_parameters_1)
    
    output = file_0 == file_1
    vampytest.assert_instance(output, bool)
    return output
