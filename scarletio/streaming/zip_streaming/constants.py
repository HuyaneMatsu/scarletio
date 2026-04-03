__all__ = (
    'COMPRESSION_METHOD_BZIP2', 'COMPRESSION_METHOD_DEFLATE', 'COMPRESSION_METHOD_LZMA', 'COMPRESSION_METHOD_NONE'
)

from struct import Struct


# ---- Constants ----

ZIP64_VERSION_REQUIRED_TO_EXTRACT = 45
ZIP64_VERSION_MADE_BY = 2629


# ---- Flags ----

FLAG_DATA_DESCRIPTOR = 1 << 3
FLAG_UTF8 = 1 << 11


# ---- Compression methods ----

COMPRESSION_METHOD_NONE = 0
COMPRESSION_METHOD_DEFLATE = 8
COMPRESSION_METHOD_BZIP2 = 12
COMPRESSION_METHOD_LZMA = 14


# ---- Local file header ---

LOCAL_FILE_HEADER_SIGNATURE = b'\x50\x4b\x03\x04'
LOCAL_FILE_HEADER_STRUCT = Struct(b"<4sHHHHHLLLHH")
LOCAL_FILE_HEADER_LENGTH = 30

"""
Structure (4.3.7):

| name                          | size  | value                                     |
+===============================+=======+===========================================+
| signature                     | 4     | LOCAL_FILE_HEADER_SIGNATURE               |
| version_required_to_extract   | 2     | ZIP64_VERSION_REQUIRED_TO_EXTRACT         |
| flags                         | 2     | int flag                                  |
| compression_method            | 2     | int enum                                  |
| modification_time             | 2     | hour, minute, second packed               |
| modification_date             | 2     | year, month of year packed                |
| crc                           | 4     | 0                                         |
| size_compressed               | 4     | 0                                         |
| size_uncompressed             | 4     | 0                                         |
| file_name_length              | 2     | file name length                          |
| extra_field_length            | 2     | 0                                         |

Notes:
Why is the smaller part of the modification date first? Are they brainrotted?
"""


# ---- Data descriptor ----

ZIP64_DATA_DESCRIPTOR_SIGNATURE = b'\x50\x4b\x07\x08'
ZIP64_DATA_DESCRIPTOR_STRUCT = Struct(b"<4sLQQ")
ZIP64_DATA_DESCRIPTOR_LENGTH = 24

"""
Structure (4.3.9):


| name              | size  | value                             |
+===================+=======+===================================+
| signature         | 4     | ZIP64_DATA_DESCRIPTOR_SIGNATURE   |
| crc               | 4     | CRC-32 of the uncompressed data   |
| size_compressed   | 8     | size of the compressed data       |
| size_uncompressed | 8     | size of the uncompressed data     |

Notes:
For zip32 `size_compressed` and `size_uncompressed` are 4 bytes.
"""


# --- Central directory file header ---

CENTRAL_DIRECTORY_FILE_HEADER_SIGNATURE = b'\x50\x4b\x01\x02'
CENTRAL_DIRECTORY_FILE_HEADER_STRUCT = Struct(b"<4sHHHHHHLLLHHHHHLL")
CENTRAL_DIRECTORY_HEADER_LENGTH = 46

"""
Structure (4.3.12):

| name                          | size  | value                                     |
+===============================+=======+===========================================+
| signature                     | 4     | CENTRAL_DIRECTORY_FILE_HEADER_SIGNATURE   |
| version_made_by               | 2     | ZIP64_VERSION_MADE_BY                     |
| version_required_to_extract   | 2     | ZIP64_VERSION_REQUIRED_TO_EXTRACT         |
| flags                         | 2     | int flag                                  |
| compression_method            | 2     | int enum                                  |
| modification_time             | 2     | hour, minute, second packed               |
| modification_date             | 2     | year, month of year packed                |
| crc                           | 4     | CRC-32 of the uncompressed data           |
| size_compressed               | 4     | 0xffffffff                                |
| size_uncompressed             | 4     | 0xffffffff                                |
| file_name_length              | 2     | file name length                          |
| extra_field_length            | 2     | 28                                        |
| file_comment_size             | 2     | 0                                         |
| disk_start                    | 2     | 0                                         |
| internal_file_attribute       | 2     | 0                                         |
| external_file_attribute       | 4     | 0                                         |
| offset                        | 4     | 0xffffffff                                |
"""


# ---- zip64 extra fields ----

ZIP64_EXTRA_FIELD_SIGNATURE = b'\x01\x00'
ZIP64_EXTRA_FIELD_STRUCT = Struct(b"<2sHQQQ")
ZIP64_EXTRA_FIELD_LENGTH = 28

"""
Structure (4.5.3):

| name                  | size  | value                                         |
+=======================+=======+===============================================+
| signature             | 2     | ZIP64_EXTRA_FIELD_SIGNATURE                   |
| extra_field_length    | 2     | 24                                            |
| size_uncompressed     | 8     | size of the uncompressed data                 |
| size_compressed       | 8     | size of the compressed data                   |
| offset                | 8     | where the file starts in the created archive  |

Notes:
Now here the `size_uncompressed` is before `size_compressed`, why would they do this? Are they brainrotted?
"""


# ---- zip64 end of central directory record ----

ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE = b'\x50\x4b\x06\x06'
ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_STRUCT = Struct(b"<4sQHHIIQQQQ")
ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_LENGTH = 56

"""
Structure (4.3.14):

| name                                          | size  | value                                                             |
+===============================================+=======+===================================================================+
| signature                                     | 4     | ZIP64_END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE                   |
| size_of_zip64_end_of_central_directory_record | 8     | 44 (size of self + comment length - 12)                           |
| version_made_by                               | 2     | ZIP64_VERSION_MADE_BY                                             |
| version_required_to_extract                   | 2     | ZIP64_VERSION_REQUIRED_TO_EXTRACT                                 |
| number_of_this_disk                           | 4     | 0                                                                 |
| central_directory_start                       | 4     | 0                                                                 |
| central_directory_entries_this_disk           | 8     | The amount of files                                               |
| central_directory_entries_total               | 8     | The amount of files                                               |
| central_directory_size                        | 8     | The cumulative size of the central directory entries              |
| central_directory_offset                      | 8     | Where the central directory entries start in the created archive  |
"""

# ---- end of central directory locator ----

ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_SIGNATURE = b'\x50\x4b\x06\x07'
ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_STRUCT = Struct(b"<4sLQL")
ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_LENGTH = 20

"""
Structure (4.3.15):

| name                  | size  | value                                                 |
+=======================+=======+=======================================================+
| signature             | 4     | ZIP64_END_OF_CENTRAL_DIRECTORY_LOCATOR_SIGNATURE      |
| disk_with_zip64_end   | 4     | 0                                                     |
| zip64_end_offset      | 8     | Where the end directory starts in the created archive |
| total_disks           | 4     | 1                                                     |
"""


# ---- end of central directory record ---

END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE = b'P\x4b\x05\x06'
END_OF_CENTRAL_DIRECTORY_RECORD_STRUCT = Struct(b"<4sHHHHLLH")
END_OF_CDIR_RECORD_CD_RECORD_LENGTH = 22

"""
Structure (4.3.16):

| name                          | size  | value                                     |
+===============================+=======+===========================================+
| signature                     | 4     | END_OF_CENTRAL_DIRECTORY_RECORD_SIGNATURE |
| number_of_this_disk           | 2     | 0                                         |
| central_directory_start       | 2     | 0                                         |
| total_entries_on_this_disk    | 2     | The amount of files                       |
| total_entries_total           | 2     | The amount of files                       |
| central_directory_size        | 4     | 0xffffffff                                |
| offset_of_central_directory   | 4     | 0xffffffff                                |
| comment_size                  | 2     | 0                                         |
"""
