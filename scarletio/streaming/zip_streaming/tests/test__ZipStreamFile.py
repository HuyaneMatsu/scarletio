from datetime import datetime as DateTime, timezone as TimeZone

import vampytest

from ..constants import COMPRESSION_METHOD_DEFLATE
from ..file import ZipStreamFile

from .resources import AsyncGenerator


def _assert_fields_set(file):
    """
    Asserts whether every fields are set.
    
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
