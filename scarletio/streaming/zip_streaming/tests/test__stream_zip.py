from datetime import datetime as DateTime, timezone as TimeZone
from itertools import count
from re import compile as re_compile

import vampytest

from ..file import ZipStreamFile
from ..zip_stream import stream_zip

from .resources import AsyncGenerator

MODIFIED_AT = DateTime(2016, 5, 14, 4, 6, 16, tzinfo = TimeZone.utc)
ASYNC_GENERATOR_0 = AsyncGenerator([b'hey mister\n', b'mrrrrrrrrrrrr\n'])
ASYNC_GENERATOR_1 = AsyncGenerator([b'hey sister\n', b'mrrrrrrrrrrr\n'])


def _get_test_files(*, compression_method = 0, name_0 = 'mister.txt', name_1 = 'sister.txt'):
    return [
        ZipStreamFile(
            name_0,
            ASYNC_GENERATOR_0,
            modified_at = MODIFIED_AT,
            compression_method = compression_method,
        ),
        ZipStreamFile(
            name_1,
            ASYNC_GENERATOR_1,
            modified_at = MODIFIED_AT,
            compression_method = compression_method,
        ),
    ]


async def test__zip_stream():
    """
    Tests whether ``stream_zip`` works as intended.
    
    This function is a coroutine.
    """
    output_parts = []
    async for chunk in stream_zip(_get_test_files()):
        output_parts.append(chunk)
    
    vampytest.assert_eq(
        output_parts,
        [
            b'PK\x03\x04-\x00\x08\x00\x00\x00\xc8 \xaeH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00',
            b'mister.txt',
            b'hey mister\n',
            b'mrrrrrrrrrrrr\n',
            b'PK\x07\x08\x08\xc2\xc0\xce\x19\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x03\x04-\x00\x08\x00\x00\x00\xc8 \xaeH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00',
            b'sister.txt',
            b'hey sister\n',
            b'mrrrrrrrrrrr\n',
            b'PK\x07\x08\x17\xfe\xac\t\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x01\x02E\n-\x00\x08\x00\x00\x00\xc8 \xaeH\x08\xc2\xc0\xce\xff\xff\xff\xff\xff\xff\xff\xff\n\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
            b'mister.txt',
            b'\x01\x00\x18\x00\x19\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x01\x02E\n-\x00\x08\x00\x00\x00\xc8 \xaeH\x17\xfe\xac\t\xff\xff\xff\xff\xff\xff\xff\xff\n\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
            b'sister.txt',
            b'\x01\x00\x18\x00\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00Y\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x06\x06,\x00\x00\x00\x00\x00\x00\x00E\n-\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xa8\x00\x00\x00\x00\x00\x00\x00\xb1\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x06\x07\x00\x00\x00\x00Y\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00',
            b'PK\x05\x06\x00\x00\x00\x00\x02\x00\x02\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00',
        ],
    )


async def test__zip_stream__compressed__zlib_default():
    """
    Tests whether ``stream_zip`` works as intended.
    
    This function is a coroutine.
    
    Case: using zlib deflate compression.
    """
    output_parts = []
    async for chunk in stream_zip(_get_test_files(compression_method = 8)):
        output_parts.append(chunk)
    
    vampytest.assert_eq(
        output_parts,
        [
            b'PK\x03\x04-\x00\x08\x00\x08\x00\xc8 \xaeH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00',
            b'mister.txt',
            b'\xcbH\xadT\xc8\xcd,.I-\xe2\xca-B\x02\\\x00',
            b'PK\x07\x08\x08\xc2\xc0\xce\x11\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x03\x04-\x00\x08\x00\x08\x00\xc8 \xaeH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00',
            b'sister.txt',
            b'\xcbH\xadT(\xce,.I-\xe2\xca-B\x00.\x00',
            b'PK\x07\x08\x17\xfe\xac\t\x11\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x01\x02E\n-\x00\x08\x00\x08\x00\xc8 \xaeH\x08\xc2\xc0\xce\xff\xff\xff\xff\xff\xff\xff\xff\n\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
            b'mister.txt',
            b'\x01\x00\x18\x00\x19\x00\x00\x00\x00\x00\x00\x00\x11\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x01\x02E\n-\x00\x08\x00\x08\x00\xc8 \xaeH\x17\xfe\xac\t\xff\xff\xff\xff\xff\xff\xff\xff\n\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
            b'sister.txt',
            b'\x01\x00\x18\x00\x18\x00\x00\x00\x00\x00\x00\x00\x11\x00\x00\x00\x00\x00\x00\x00Q\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x06\x06,\x00\x00\x00\x00\x00\x00\x00E\n-\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xa8\x00\x00\x00\x00\x00\x00\x00\xa2\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x06\x07\x00\x00\x00\x00J\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00',
            b'PK\x05\x06\x00\x00\x00\x00\x02\x00\x02\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00',
        ],
    )


async def test__zip_stream__duplicate_name():
    """
    Tests whether ``stream_zip`` works as intended.
    
    This function is a coroutine.
    """
    output_parts = []
    async for chunk in stream_zip(_get_test_files(name_0 = 'sister.txt', name_1 = 'sister.txt')):
        output_parts.append(chunk)
    
    vampytest.assert_eq(
        output_parts,
        [
            b'PK\x03\x04-\x00\x08\x00\x00\x00\xc8 \xaeH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00',
            b'sister.txt',
            b'hey mister\n',
            b'mrrrrrrrrrrrr\n',
            b'PK\x07\x08\x08\xc2\xc0\xce\x19\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x03\x04-\x00\x08\x00\x00\x00\xc8 \xaeH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x00\x00\x00',
            b'sister (1).txt',
            b'hey sister\n',
            b'mrrrrrrrrrrr\n',
            b'PK\x07\x08\x17\xfe\xac\t\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x01\x02E\n-\x00\x08\x00\x00\x00\xc8 \xaeH\x08\xc2\xc0\xce\xff\xff\xff\xff\xff\xff\xff\xff\n\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
            b'sister.txt',
            b'\x01\x00\x18\x00\x19\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x01\x02E\n-\x00\x08\x00\x00\x00\xc8 \xaeH\x17\xfe\xac\t\xff\xff\xff\xff\xff\xff\xff\xff\x0e\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
            b'sister (1).txt',
            b'\x01\x00\x18\x00\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00Y\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x06\x06,\x00\x00\x00\x00\x00\x00\x00E\n-\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xac\x00\x00\x00\x00\x00\x00\x00\xb5\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x06\x07\x00\x00\x00\x00a\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00',
            b'PK\x05\x06\x00\x00\x00\x00\x02\x00\x02\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00',
        ],
    )


async def test__zip_stream__custom_deduplicator():
    """
    Tests whether ``stream_zip`` works as intended.
    
    This function is a coroutine.
    """
    NAME_REGEX = re_compile('((?:.*/)?.*?)(?:\\.(.*?))?')
    
    def name_deduplicator_postfixed():
        nonlocal NAME_REGEX
        nonlocal name_reconstructor
        
        name = yield
        
        for index in count():
            match = NAME_REGEX.fullmatch(name)
            if match is None:
                path = name
                extension = None
            else:
                path, extension = match.groups()
            
            name = yield name_reconstructor(path, index, extension)
    
    def name_reconstructor(path, index, extension):
        name_parts = [path, '_', str(index).rjust(4, '0')]
        
        if (extension is not None):
            name_parts.append('.')
            name_parts.append(extension)
        
        return ''.join(name_parts)
    
    output_parts = []
    async for chunk in stream_zip(
        _get_test_files(name_0 = 'sister.txt', name_1 = 'sister.txt'),
        name_deduplicator = name_deduplicator_postfixed(),
    ):
        output_parts.append(chunk)
    
    vampytest.assert_eq(
        output_parts,
        [
            b'PK\x03\x04-\x00\x08\x00\x00\x00\xc8 \xaeH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00',
            b'sister_0000.txt',
            b'hey mister\n',
            b'mrrrrrrrrrrrr\n',
            b'PK\x07\x08\x08\xc2\xc0\xce\x19\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x03\x04-\x00\x08\x00\x00\x00\xc8 \xaeH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00',
            b'sister_0001.txt',
            b'hey sister\n',
            b'mrrrrrrrrrrr\n',
            b'PK\x07\x08\x17\xfe\xac\t\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x01\x02E\n-\x00\x08\x00\x00\x00\xc8 \xaeH\x08\xc2\xc0\xce\xff\xff\xff\xff\xff\xff\xff\xff\x0f\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
            b'sister_0000.txt',
            b'\x01\x00\x18\x00\x19\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x01\x02E\n-\x00\x08\x00\x00\x00\xc8 \xaeH\x17\xfe\xac\t\xff\xff\xff\xff\xff\xff\xff\xff\x0f\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
            b'sister_0001.txt', b'\x01\x00\x18\x00\x18\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x00\x00\x00\x00^\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x06\x06,\x00\x00\x00\x00\x00\x00\x00E\n-\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\xb2\x00\x00\x00\x00\x00\x00\x00\xbb\x00\x00\x00\x00\x00\x00\x00',
            b'PK\x06\x07\x00\x00\x00\x00m\x01\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00',
            b'PK\x05\x06\x00\x00\x00\x00\x02\x00\x02\x00\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00',
        ],
    )
