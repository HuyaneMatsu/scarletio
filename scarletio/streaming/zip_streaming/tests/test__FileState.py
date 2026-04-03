from datetime import datetime as DateTime, timezone as TimeZone

import vampytest

from ..constants import FLAG_DATA_DESCRIPTOR, FLAG_UTF8
from ..file import ZipStreamFile
from ..file_state import ZipStreamFileState

from .resources import AsyncGenerator


def _assert_fields_set(file_state):
    """
    Asserts whether every field is set.
    
    Parameters
    ----------
    file_state : ``ZipStreamFileState``
        The file_state to check.
    """
    vampytest.assert_instance(file_state, ZipStreamFileState)
    vampytest.assert_instance(file_state.crc, int)
    vampytest.assert_instance(file_state.flags, int)
    vampytest.assert_instance(file_state.modification_date, int)
    vampytest.assert_instance(file_state.modification_time, int)
    vampytest.assert_instance(file_state.name_binary, bytes)
    vampytest.assert_instance(file_state.offset, int)
    vampytest.assert_instance(file_state.size_compressed, int)
    vampytest.assert_instance(file_state.size_uncompressed, int)


def test__ZipStreamFileState__new():
    """
    Tests whether ``ZipStreamFileState.__new__`` works as intended.
    """
    async_generator = AsyncGenerator([b'aya'])
    name = 'koishi'
    modified_at = DateTime(2016, 5, 14, 5, 4, 23, tzinfo = TimeZone.utc)
    
    file = ZipStreamFile(name, async_generator, modified_at = modified_at)
    
    file_state = ZipStreamFileState(file, None)
    _assert_fields_set(file_state)
    
    vampytest.assert_eq(file_state.modification_date, 18606)
    vampytest.assert_eq(file_state.modification_time, 10379)
    vampytest.assert_eq(file_state.name_binary, b'koishi')
    vampytest.assert_eq(file_state.flags, FLAG_DATA_DESCRIPTOR)


def test__ZipStreamFileState__new__unicode_name():
    """
    Tests whether ``ZipStreamFileState.__new__`` works as intended.
    
    Case: Unicode name.
    """
    async_generator = AsyncGenerator([b'aya'])
    name = 'bűn'
    
    file = ZipStreamFile(name, async_generator)
    
    file_state = ZipStreamFileState(file, None)
    _assert_fields_set(file_state)
    
    vampytest.assert_eq(file_state.name_binary, b'b\xc5\xb1n')
    vampytest.assert_eq(file_state.flags, FLAG_DATA_DESCRIPTOR | FLAG_UTF8)


def test__ZipStreamFileState__name_deduplicator_check():
    """
    Tests whether ``ZipStreamFileState.__new__`` works as intended.
    
    Check whether name deduplicator is handled correctly.
    """
    def name_deduplicator_function():
        name = yield
        while True:
            name = yield name + ' (1)'
    
    async_generator = AsyncGenerator([b'aya'])
    name = 'koishi'
    modified_at = DateTime(2016, 5, 14, 5, 4, 23, tzinfo = TimeZone.utc)
    
    file = ZipStreamFile(name, async_generator, modified_at = modified_at)
    
    name_deduplicator = name_deduplicator_function()
    name_deduplicator.send(None)
    try:
        file_state = ZipStreamFileState(file, name_deduplicator)
        _assert_fields_set(file_state)
    
    finally:
        name_deduplicator.close()
        name_deduplicator = None
    
    vampytest.assert_eq(file_state.name_binary, b'koishi (1)')


def test__ZipStreamFileState__repr():
    """
    Tests whether ``ZipStreamFileState.__repr__`` works as intended.
    """
    async_generator = AsyncGenerator([b'aya'])
    name = 'koishi'
    
    file = ZipStreamFile(name, async_generator)
    
    file_state = ZipStreamFileState(file, None)
    
    output = repr(file_state)
    vampytest.assert_instance(output, str)
