__all__ = ('create_zip_stream_resource', 'stream_zip',)

from ..resource_streaming import ResourceStreamFunction

from .compression import select_compressor_type
from .constants import (
    CENTRAL_DIRECTORY_FILE_HEADER_SIGNATURE, CENTRAL_DIRECTORY_FILE_HEADER_STRUCT, CENTRAL_DIRECTORY_HEADER_LENGTH,
    END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE, END_OF_CENTRAL_DIRECTORY_RECORD_STRUCT, LOCAL_FILE_HEADER_LENGTH,
    LOCAL_FILE_HEADER_SIGNATURE, LOCAL_FILE_HEADER_STRUCT, ZIP64_DATA_DESCRIPTOR_LENGTH,
    ZIP64_DATA_DESCRIPTOR_SIGNATURE, ZIP64_DATA_DESCRIPTOR_STRUCT, ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_SIGNATURE,
    ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_STRUCT, ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE,
    ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_STRUCT, ZIP64_EXTRA_FIELD_LENGTH, ZIP64_EXTRA_FIELD_SIGNATURE,
    ZIP64_EXTRA_FIELD_STRUCT, ZIP64_VERSION_MADE_BY, ZIP64_VERSION_REQUIRED_TO_EXTRACT
)
from .file_state import ZipStreamFileState
from .name_deduplication import NAME_DEDUPLICATOR_REGEX_PATTERN_DEFAULT, name_deduplicator_default, name_deduplicator_name_reconstructor_default


def _create_local_file_header(file, file_state):
    """
    Creates a local file header for a zip-64 archive.
    
    Parameters
    ----------
    file : ``ZipStreamFile``
        The file to create header for.
    
    file_state : ``ZipStreamFileState``
        The file's state.
    
    Returns
    -------
    chunk : `bytes`
    """
    return LOCAL_FILE_HEADER_STRUCT.pack(
        LOCAL_FILE_HEADER_SIGNATURE,
        ZIP64_VERSION_REQUIRED_TO_EXTRACT,
        file_state.flags,
        file.compression_method,
        file_state.modification_time,
        file_state.modification_date,
        0,
        0,
        0,
        len(file_state.name_binary),
        0,
    )


def _create_data_descriptor(file_state):
    """
    Creates a data descriptor for a zip archive.
    
    Parameters
    ----------
    file_state : ``ZipStreamFileState``
        The file's state to create data descriptor for.
    
    Returns
    -------
    chunk : `bytes`
    """
    return ZIP64_DATA_DESCRIPTOR_STRUCT.pack(
        ZIP64_DATA_DESCRIPTOR_SIGNATURE,
        file_state.crc,
        file_state.size_compressed,
        file_state.size_uncompressed,
    )


def _create_central_directory_file_header(file, file_state):
    """
    Creates a central directory file header for zip-64 archive.
    
    Parameters
    ----------
    file : ``ZipStreamFile``
        The file to create header for.
    
    file_state : ``ZipStreamFileState``
        The file's state.
    
    Returns
    -------
    chunk : `bytes`
    """
    return CENTRAL_DIRECTORY_FILE_HEADER_STRUCT.pack(
        CENTRAL_DIRECTORY_FILE_HEADER_SIGNATURE,
        ZIP64_VERSION_MADE_BY,
        ZIP64_VERSION_REQUIRED_TO_EXTRACT,
        file_state.flags,
        file.compression_method,
        file_state.modification_time,
        file_state.modification_date,
        file_state.crc,
        0xffffffff,
        0xffffffff,
        len(file_state.name_binary),
        28,
        0,
        0,
        0,
        0,
        0xffffffff,
    )


def _create_zip64_extra_field(file_state):
    """
    Creates a zip-64 extra field.
    
    Parameters
    ----------
    file_state : ``ZipStreamFileState``
        The file's state to create extra fields for.
    
    Returns
    -------
    chunk : `bytes`
    """
    return ZIP64_EXTRA_FIELD_STRUCT.pack(
        ZIP64_EXTRA_FIELD_SIGNATURE,
        24,
        file_state.size_uncompressed,
        file_state.size_compressed,
        file_state.offset,
    )


def _create_zip64_end_of_central_directory_record(
    files_count, offset_to_start_of_central_directory, central_directory_size
):
    """
    Creates a zip-64 end of central directory record.
    
    Parameters
    ----------
    files_count : `int`
        The amount of archived files.
    
    offset_to_start_of_central_directory : `int`
        Offset till the central directory records.
    
    central_directory_size : `int`
        The size of the central directory.
    
    Returns
    -------
    chunk : `bytes`
    """
    return ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_STRUCT.pack(
        ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE,
        44,
        ZIP64_VERSION_MADE_BY,
        ZIP64_VERSION_REQUIRED_TO_EXTRACT,
        0,
        0,
        files_count,
        files_count,
        central_directory_size,
        offset_to_start_of_central_directory,
    )


def _create_zip64_end_of_central_directory_locator(offset_to_start_of_end_directory):
    """
    Creates a zip-64 end of central directory locator.
    
    Parameters
    ----------
    offset_to_start_of_end_directory : `int`
        Offset till the end records.
    
    Returns
    -------
    chunk : `bytes`
    """
    return ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_STRUCT.pack(
        ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_SIGNATURE,
        0,
        offset_to_start_of_end_directory,
        1,
    )


def _create_end_of_central_directory_record(files_count):
    """
    Creates a end of central directory record for a zip archive,
    
    Parameters
    ----------
    files_count : `int`
        The amount of archived files.
    
    Returns
    -------
    chunk : `bytes`
    """
    return END_OF_CENTRAL_DIRECTORY_RECORD_STRUCT.pack(
        END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE,
        0,
        0,
        files_count,
        files_count,
        0xffffffff,
        0xffffffff,
        0,
    )


async def stream_zip(files, *, name_deduplicator = ...):
    """
    Streams the zip archive.
    
    This method is a coroutine generator.
    
    Parameters
    ----------
    files : `iterable<ZipStreamFile>`
        The files to stream.
    
    name_deduplicator : `None | Generator`, Optional (Keyword only)
        Name deduplicator generator to use.
    
    Yields
    -------
    chunk : `bytes | memoryview`
    """
    while True:
        if name_deduplicator is ...:
            name_deduplicator = name_deduplicator_default(
                NAME_DEDUPLICATOR_REGEX_PATTERN_DEFAULT, name_deduplicator_name_reconstructor_default
            )
            
        elif name_deduplicator is None:
            break
        
        name_deduplicator.send(None)
        break
    
    try:
        files_with_states = [(file, ZipStreamFileState(file, name_deduplicator)) for file in files]
    finally:
        if (name_deduplicator is not None):
            name_deduplicator.close()
            name_deduplicator = None
    
    
    offset = 0
    for file, file_state in files_with_states:
        file_state.offset = offset
        # Stream a single file
        #
        # Includes:
        # local_file_header | file_path | ... data chunks ... | data descriptor
        
        yield _create_local_file_header(file, file_state)
        yield file_state.name_binary
        
        try:
            compressor = select_compressor_type(file.compression_method)()
            
            async for chunk in file.async_generator:
                chunk = compressor.process(file_state, chunk)
                if chunk:
                    yield chunk
            
            chunk = compressor.tail(file_state)
            if chunk:
                yield chunk
        
        finally:
            # deallocate the compressor
            compressor = None
        
        yield _create_data_descriptor(file_state)
        
        offset += (
            LOCAL_FILE_HEADER_LENGTH + len(file_state.name_binary) + file_state.size_compressed +
            ZIP64_DATA_DESCRIPTOR_LENGTH
        )
    
    # Stream end structure
    #
    # Includes:
    # For every file: central_directory_file_header | file_path | zip64_extra_fields
    # zip64_end_of_central_directory_record | zip64_end_of_central_directory_locator | end_of_central_directory_record 
    
    # Stream central directory entries
    central_directory_size = (CENTRAL_DIRECTORY_HEADER_LENGTH + ZIP64_EXTRA_FIELD_LENGTH) * len(files_with_states)
    
    for file, file_state in files_with_states:
        yield _create_central_directory_file_header(file, file_state)
        yield file_state.name_binary
        yield _create_zip64_extra_field(file_state)
        central_directory_size += len(file_state.name_binary)
    
    # Stream central directory end
    yield _create_zip64_end_of_central_directory_record(len(files_with_states), offset, central_directory_size)
    yield _create_zip64_end_of_central_directory_locator(offset + central_directory_size)
    yield _create_end_of_central_directory_record(len(files_with_states))


create_zip_stream_resource = ResourceStreamFunction(stream_zip)
