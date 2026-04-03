import vampytest

from ..constants import (
    RESPONSE_PARSING_ERROR_CODE_HEADER_OUT_OF_BOUND, RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_FORWARD,
    RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_READ_OUT_OF_BOUND, RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_INVALID_RANGE,
    RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_READ_OUT_OF_BOUND, RESPONSE_PARSING_ERROR_CODE_LABEL_READ_END_OUT_OF_BOUND,
    RESPONSE_PARSING_ERROR_CODE_NONE, RESPONSE_PARSING_ERROR_CODE_QUESTION_HEADER_OUT_OF_BOUND,
    RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_DATA_OUT_OF_BOUND,
    RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_HEADER_OUT_OF_BOUND
)
from ..response_parsing_error import ResponseParsingError, get_response_parsing_error_message_producer


def _iter_options():
    yield (
        RESPONSE_PARSING_ERROR_CODE_NONE,
        b'nyan',
        (),
        None,
    )
    
    yield (
        RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_INVALID_RANGE,
        b'nyan',
        (100, 3),
        'Label length in invalid range (64, 192); label_length = 100; index = 3.',
    )
    
    yield (
        RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_FORWARD,
        b'nyan',
        (56, 3),
        'Label reading jumped forward; furthest_index = 56; index = 3.',
    )
    
    yield (
        RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_READ_OUT_OF_BOUND,
        b'nyan',
        (),
        'Could not read label length due to it being out of bound; data_length = 4.',
    )
    
    yield (
        RESPONSE_PARSING_ERROR_CODE_LABEL_READ_END_OUT_OF_BOUND,
        b'nyan',
        (56, 59),
        'Could not read label due to its end being out of bound; data_length = 4; start = 56; end = 59.',
    )
    
    yield (
        RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_READ_OUT_OF_BOUND,
        b'nyan',
        (),
        'Could not read label jump due to it being out of bound; data_length = 4.',
    )
    
    yield (
        RESPONSE_PARSING_ERROR_CODE_HEADER_OUT_OF_BOUND,
        b'nyan',
        (),
        'Could not read header (length 12) due to its end being out of bound; data_length = 4.',
    )
    
    yield (
        RESPONSE_PARSING_ERROR_CODE_QUESTION_HEADER_OUT_OF_BOUND,
        b'nyan',
        (56, ),
        'Could not read question header (length 4) due to its end being out of bound; data_length = 4; end = 56.',
    )
    
    yield (
        RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_HEADER_OUT_OF_BOUND,
        b'nyan',
        (56, ),
        'Could not read resource record header (length 10) due to its end being out of bound; data_length = 4; end = 56.',
    )
    
    yield (
        RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_DATA_OUT_OF_BOUND,
        b'nyan',
        (56, 60),
        'Could not read resource record data due to its end being out of bound; data_length = 4; start = 56; end = 60.',
    )
    
    yield (
        999,
        b'nyan',
        (),
        None,
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_response_parsing_error_message_producer(
    parsing_error_code,
    parsing_error_response_data,
    parsing_error_metadata,
):
    """
    Tests whether ``get_response_parsing_error_message_producer`` works as intended.
    
    Parameters
    ----------
    parsing_error_code : `int`
        Parsing error code.
    
    parsing_error_response_data : ``bytes`
        Received response data.
    
    parsing_error_metadata : `tuple<<object>`
        Additional metadata.
    
    Returns
    -------
    output : `None | str`
    """
    producer = get_response_parsing_error_message_producer(parsing_error_code)
    if (producer is None):
        return None
    
    parts = [*producer(ResponseParsingError(parsing_error_code, parsing_error_response_data, parsing_error_metadata))]
    for part in parts:
        vampytest.assert_instance(part, str)
    
    return ''.join(parts)
