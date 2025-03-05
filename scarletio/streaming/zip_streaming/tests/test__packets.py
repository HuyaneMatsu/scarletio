from datetime import datetime as DateTime, timezone as TimeZone

import vampytest

from ..constants import (
    CENTRAL_DIRECTORY_FILE_HEADER_SIGNATURE, COMPRESSION_METHOD_DEFLATE, END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE,
    LOCAL_FILE_HEADER_SIGNATURE, ZIP64_DATA_DESCRIPTOR_SIGNATURE, ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_SIGNATURE,
    ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE, ZIP64_EXTRA_FIELD_SIGNATURE, ZIP64_VERSION_MADE_BY,
    ZIP64_VERSION_REQUIRED_TO_EXTRACT
)
from ..file import ZipStreamFile
from ..file_state import ZipStreamFileState
from ..zip_stream import (
    _create_central_directory_file_header, _create_data_descriptor, _create_end_of_central_directory_record,
    _create_local_file_header, _create_zip64_end_of_central_directory_locator,
    _create_zip64_end_of_central_directory_record, _create_zip64_extra_field
)

from .resources import AsyncGenerator


ASYNC_GENERATOR = AsyncGenerator(['mrrr\n', 'mrrr\n'])


def test__create_local_file_header():
    """
    Tests whether ``_create_local_file_header`` works as intended.
    """
    file = ZipStreamFile(
        'mister.txt',
        ASYNC_GENERATOR,
        compression_method = COMPRESSION_METHOD_DEFLATE,
        modified_at = DateTime(2016, 5, 14, 6, 5, 56, tzinfo = TimeZone.utc),
    )
    file_state = ZipStreamFileState(file, None)
    
    vampytest.assert_eq(
        _create_local_file_header(file, file_state),
        b''.join([
            LOCAL_FILE_HEADER_SIGNATURE,
            ZIP64_VERSION_REQUIRED_TO_EXTRACT.to_bytes(2, 'little'),
            file_state.flags.to_bytes(2, 'little'),
            COMPRESSION_METHOD_DEFLATE.to_bytes(2, 'little'),
            file_state.modification_time.to_bytes(2, 'little'),
            file_state.modification_date.to_bytes(2, 'little'),
            (0).to_bytes(4, 'little'),
            (0).to_bytes(4, 'little'),
            (0).to_bytes(4, 'little'),
            len(file_state.name_binary).to_bytes(2, 'little'),
            (0).to_bytes(2, 'little'),
        ]),
    )


def test__create_data_descriptor():
    """
    Tests whether ``_create_data_descriptor`` works as intended.
    """
    file = ZipStreamFile(
        'mister.txt',
        ASYNC_GENERATOR,
        compression_method = COMPRESSION_METHOD_DEFLATE,
        modified_at = DateTime(2016, 5, 14, 6, 5, 56, tzinfo = TimeZone.utc),
    )
    file_state = ZipStreamFileState(file, None)
    
    crc = 45566
    size_compressed = 12
    size_uncompressed = 16
    
    file_state.crc = crc
    file_state.size_compressed = size_compressed
    file_state.size_uncompressed = size_uncompressed
    
    vampytest.assert_eq(
        _create_data_descriptor(file_state),
        b''.join([
            ZIP64_DATA_DESCRIPTOR_SIGNATURE,
            crc.to_bytes(4, 'little'),
            size_compressed.to_bytes(8, 'little'),
            size_uncompressed.to_bytes(8, 'little'),
        ]),
    )


def test__create_central_directory_file_header():
    """
    Tests whether ``_create_central_directory_file_header`` works as intended.
    """
    file = ZipStreamFile(
        'mister.txt',
        ASYNC_GENERATOR,
        compression_method = COMPRESSION_METHOD_DEFLATE,
        modified_at = DateTime(2016, 5, 14, 6, 5, 56, tzinfo = TimeZone.utc),
    )
    file_state = ZipStreamFileState(file, None)
    
    crc = 45566
    
    file_state.crc = crc
    
    vampytest.assert_eq(
        _create_central_directory_file_header(file, file_state),
        b''.join([
            CENTRAL_DIRECTORY_FILE_HEADER_SIGNATURE,
            ZIP64_VERSION_MADE_BY.to_bytes(2, 'little'),
            ZIP64_VERSION_REQUIRED_TO_EXTRACT.to_bytes(2, 'little'),
            file_state.flags.to_bytes(2, 'little'),
            COMPRESSION_METHOD_DEFLATE.to_bytes(2, 'little'),
            file_state.modification_time.to_bytes(2, 'little'),
            file_state.modification_date.to_bytes(2, 'little'),
            crc.to_bytes(4, 'little'),
            (0xffffffff).to_bytes(4, 'little'),
            (0xffffffff).to_bytes(4, 'little'),
            len(file_state.name_binary).to_bytes(2, 'little'),
            (28).to_bytes(2, 'little'),
            (0).to_bytes(2, 'little'),
            (0).to_bytes(2, 'little'),
            (0).to_bytes(2, 'little'),
            (0).to_bytes(4, 'little'),
            (0xffffffff).to_bytes(4, 'little'),
        ]),
    )


def test__create_zip64_extra_field():
    """
    Tests whether ``_create_zip64_extra_field`` works as intended.
    """
    file = ZipStreamFile(
        'mister.txt',
        ASYNC_GENERATOR,
        compression_method = COMPRESSION_METHOD_DEFLATE,
        modified_at = DateTime(2016, 5, 14, 6, 5, 56, tzinfo = TimeZone.utc),
    )
    file_state = ZipStreamFileState(file, None)
    
    offset = 216
    size_compressed = 12
    size_uncompressed = 16
    
    file_state.offset = offset
    file_state.size_compressed = size_compressed
    file_state.size_uncompressed = size_uncompressed
    
    vampytest.assert_eq(
        _create_zip64_extra_field(file_state),
        b''.join([
            ZIP64_EXTRA_FIELD_SIGNATURE,
            (24).to_bytes(2, 'little'),
            size_uncompressed.to_bytes(8, 'little'),
            size_compressed.to_bytes(8, 'little'),
            offset.to_bytes(8, 'little'),
        ]),
    )


def test__create_zip64_end_of_central_directory_record():
    """
    Tests whether ``_create_zip64_end_of_central_directory_record`` works as intended.
    """
    file_count = 8
    offset_to_start_of_central_directory = 12000
    central_directory_size = 6699
    
    vampytest.assert_eq(
        _create_zip64_end_of_central_directory_record(
            file_count,  offset_to_start_of_central_directory, central_directory_size
        ),
        b''.join([
            ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE,
            (44).to_bytes(8, 'little'),
            ZIP64_VERSION_MADE_BY.to_bytes(2, 'little'),
            ZIP64_VERSION_REQUIRED_TO_EXTRACT.to_bytes(2, 'little'),
            (0).to_bytes(4, 'little'),
            (0).to_bytes(4, 'little'),
            file_count.to_bytes(8, 'little'),
            file_count.to_bytes(8, 'little'),
            central_directory_size.to_bytes(8, 'little'),
            offset_to_start_of_central_directory.to_bytes(8, 'little'),
        ]),
    )


def test__create_zip64_end_of_central_directory_locator():
    """
    Tests whether ``_create_zip64_end_of_central_directory_locator`` works as intended.
    """
    offset_to_start_of_end_directory = 66536
    
    vampytest.assert_eq(
        _create_zip64_end_of_central_directory_locator(offset_to_start_of_end_directory),
        b''.join([
            ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_SIGNATURE,
            (0).to_bytes(4, 'little'),
            offset_to_start_of_end_directory.to_bytes(8, 'little'),
            (1).to_bytes(4, 'little'),
        ]),
    )


def test__create_end_of_central_directory_record():
    """
    Tests whether ``_create_end_of_central_directory_record`` works as intended.
    """
    file_count = 8
    
    vampytest.assert_eq(
        _create_end_of_central_directory_record(file_count),
        b''.join([
            END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE,
            (0).to_bytes(2, 'little'),
            (0).to_bytes(2, 'little'),
            file_count.to_bytes(2, 'little'),
            file_count.to_bytes(2, 'little'),
            (0xffffffff).to_bytes(4, 'little'),
            (0xffffffff).to_bytes(4, 'little'),
            (0).to_bytes(2, 'little'),
        ]),
    )
