import vampytest

from ..building_and_parsing import parse_result_data
from ..constants import (
    CLASS_CODE_INTERNET, DATA_VERIFIED_SHIFT, MESSAGE_TYPE_SHIFT, RECURSION_AVAILABLE_SHIFT,
    RESOURCE_RECORD_TYPE_IP_V4_ADDRESS, RESPONSE_CODE_OK, RESPONSE_CODE_SHIFT,
    RESPONSE_PARSING_ERROR_CODE_HEADER_OUT_OF_BOUND, RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_FORWARD,
    RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_READ_OUT_OF_BOUND, RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_INVALID_RANGE,
    RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_READ_OUT_OF_BOUND, RESPONSE_PARSING_ERROR_CODE_LABEL_READ_END_OUT_OF_BOUND,
    RESPONSE_PARSING_ERROR_CODE_QUESTION_HEADER_OUT_OF_BOUND,
    RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_DATA_OUT_OF_BOUND,
    RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_HEADER_OUT_OF_BOUND, TRUNCATED_SHIFT
)
from ..question import Question
from ..resource_record import ResourceRecord
from ..response_parsing_error import ResponseParsingError
from ..result import Result


def _iter_options():
    data = b''.join([
        (56).to_bytes(2, 'big'),
        (
            (False << MESSAGE_TYPE_SHIFT) |
            (True << DATA_VERIFIED_SHIFT) |
            (True << TRUNCATED_SHIFT) |
            (True << RECURSION_AVAILABLE_SHIFT) |
            (RESPONSE_CODE_OK << RESPONSE_CODE_SHIFT)
        ).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        
        (3).to_bytes(1, 'big'),
        b'www',
        (6).to_bytes(1, 'big'),
        b'google',
        (3).to_bytes(1, 'big'),
        b'com',
        (0).to_bytes(1, 'big'),
        CLASS_CODE_INTERNET.to_bytes(2, 'big'),
        RESOURCE_RECORD_TYPE_IP_V4_ADDRESS.to_bytes(2, 'big'),
        
        (192).to_bytes(1, 'big'),
        (12).to_bytes(1, 'big'),
        CLASS_CODE_INTERNET.to_bytes(2, 'big'),
        RESOURCE_RECORD_TYPE_IP_V4_ADDRESS.to_bytes(2, 'big'),
        (56666).to_bytes(4, 'big'),
        (4).to_bytes(2, 'big'),
        b'abcd',
    ])
    
    yield (
        'result',
        data,
        (
            Result(
                56,
                True,
                True,
                True,
                RESPONSE_CODE_OK,
                (
                    Question(
                        (b'www', b'google', b'com'),
                        CLASS_CODE_INTERNET,
                        RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
                    ),
                ),
                (
                    ResourceRecord(
                        (b'www', b'google', b'com'),
                        CLASS_CODE_INTERNET,
                        RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
                        56666,
                        b'abcd',
                    ),
                ),
                None,
                None,
            ),
            None,
        ),
    )
    
    data = b''.join([
        b'abcd',
    ])
    
    yield (
        'header our of bound',
        data,
        (
            None,
            ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_HEADER_OUT_OF_BOUND,
                data,
                (),
            ),
        ),
    )
    
    data = b''.join([
        (56).to_bytes(2, 'big'),
        (
            (False << MESSAGE_TYPE_SHIFT) |
            (True << DATA_VERIFIED_SHIFT) |
            (True << TRUNCATED_SHIFT) |
            (True << RECURSION_AVAILABLE_SHIFT) |
            (RESPONSE_CODE_OK << RESPONSE_CODE_SHIFT)
        ).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        
        (3).to_bytes(1, 'big'),
        b'www',
        (6).to_bytes(1, 'big'),
        b'google',
        (3).to_bytes(1, 'big'),
        b'com',
        (0).to_bytes(1, 'big'),
        b'ab',
    ])
    
    yield (
        'question header out of bound',
        data,
        (
            None,
            ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_QUESTION_HEADER_OUT_OF_BOUND,
                data,
                (len(data) + 2, ),
            ),
        ),
    )
    
    data = b''.join([
        (56).to_bytes(2, 'big'),
        (
            (False << MESSAGE_TYPE_SHIFT) |
            (True << DATA_VERIFIED_SHIFT) |
            (True << TRUNCATED_SHIFT) |
            (True << RECURSION_AVAILABLE_SHIFT) |
            (RESPONSE_CODE_OK << RESPONSE_CODE_SHIFT)
        ).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        
        (3).to_bytes(1, 'big'),
        b'www',
        (6).to_bytes(1, 'big'),
        b'google',
        (3).to_bytes(1, 'big'),
        b'com',
        (0).to_bytes(1, 'big'),
        CLASS_CODE_INTERNET.to_bytes(2, 'big'),
        RESOURCE_RECORD_TYPE_IP_V4_ADDRESS.to_bytes(2, 'big'),
        
        (192).to_bytes(1, 'big'),
        (12).to_bytes(1, 'big'),
        b'ab',
    ])
    
    yield (
        'resource record header out of bound.',
        data,
        (
            None,
            ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_HEADER_OUT_OF_BOUND,
                data,
                (len(data) + 8, ),
            ),
        ),
    )
    
    data = b''.join([
        (56).to_bytes(2, 'big'),
        (
            (False << MESSAGE_TYPE_SHIFT) |
            (True << DATA_VERIFIED_SHIFT) |
            (True << TRUNCATED_SHIFT) |
            (True << RECURSION_AVAILABLE_SHIFT) |
            (RESPONSE_CODE_OK << RESPONSE_CODE_SHIFT)
        ).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        
        (3).to_bytes(1, 'big'),
        b'www',
        (6).to_bytes(1, 'big'),
        b'google',
        (3).to_bytes(1, 'big'),
        b'com',
        (0).to_bytes(1, 'big'),
        CLASS_CODE_INTERNET.to_bytes(2, 'big'),
        RESOURCE_RECORD_TYPE_IP_V4_ADDRESS.to_bytes(2, 'big'),
        
        (192).to_bytes(1, 'big'),
        (12).to_bytes(1, 'big'),
        CLASS_CODE_INTERNET.to_bytes(2, 'big'),
        RESOURCE_RECORD_TYPE_IP_V4_ADDRESS.to_bytes(2, 'big'),
        (56666).to_bytes(4, 'big'),
        (4).to_bytes(2, 'big'),
        b'ab',
    ])
    
    yield (
        'resource record data out of bound',
        data,
        (
            None,
            ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_RESOURCE_RECORD_DATA_OUT_OF_BOUND,
                data,
                (len(data) - 2, len(data) + 2),
            ),
        ),
    )
    
    data = b''.join([
        (56).to_bytes(2, 'big'),
        (
            (False << MESSAGE_TYPE_SHIFT) |
            (True << DATA_VERIFIED_SHIFT) |
            (True << TRUNCATED_SHIFT) |
            (True << RECURSION_AVAILABLE_SHIFT) |
            (RESPONSE_CODE_OK << RESPONSE_CODE_SHIFT)
        ).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        
        (3).to_bytes(1, 'big'),
        b'www',
        (6).to_bytes(1, 'big'),
        b'google',
    ])
    
    yield (
        'label length read out of bound',
        data,
        (
            None,
            ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_READ_OUT_OF_BOUND,
                data,
                (),
            ),
        ),
    )
    
    data = b''.join([
        (56).to_bytes(2, 'big'),
        (
            (False << MESSAGE_TYPE_SHIFT) |
            (True << DATA_VERIFIED_SHIFT) |
            (True << TRUNCATED_SHIFT) |
            (True << RECURSION_AVAILABLE_SHIFT) |
            (RESPONSE_CODE_OK << RESPONSE_CODE_SHIFT)
        ).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        
        (3).to_bytes(1, 'big'),
        b'www',
        (6).to_bytes(1, 'big'),
        b'google',
        (192).to_bytes(1, 'big'),
    ])
    
    yield (
        'label jump read out of bound',
        data,
        (
            None,
            ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_READ_OUT_OF_BOUND,
                data,
                (),
            ),
        ),
    )
    
    data = b''.join([
        (56).to_bytes(2, 'big'),
        (
            (False << MESSAGE_TYPE_SHIFT) |
            (True << DATA_VERIFIED_SHIFT) |
            (True << TRUNCATED_SHIFT) |
            (True << RECURSION_AVAILABLE_SHIFT) |
            (RESPONSE_CODE_OK << RESPONSE_CODE_SHIFT)
        ).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        
        (3).to_bytes(1, 'big'),
        b'www',
        (6).to_bytes(1, 'big'),
        b'google',
        (150).to_bytes(1, 'big'),
        b'ab',
    ])
    
    yield (
        'label length invalid range',
        data,
        (
            None,
            ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_LABEL_LENGTH_INVALID_RANGE,
                data,
                (150, len(data) - 2),
            ),
        ),
    )
    
    data = b''.join([
        (56).to_bytes(2, 'big'),
        (
            (False << MESSAGE_TYPE_SHIFT) |
            (True << DATA_VERIFIED_SHIFT) |
            (True << TRUNCATED_SHIFT) |
            (True << RECURSION_AVAILABLE_SHIFT) |
            (RESPONSE_CODE_OK << RESPONSE_CODE_SHIFT)
        ).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        
        (3).to_bytes(1, 'big'),
        b'www',
        (6).to_bytes(1, 'big'),
        b'google',
        (192).to_bytes(1, 'big'),
        (40).to_bytes(1, 'big'),
        b'abcd',
    ])
    
    yield (
        'label jump forward',
        data,
        (
            None,
            ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_LABEL_JUMP_FORWARD,
                data,
                (len(data) - 4, 40),
            ),
        ),
    )
    
    data = b''.join([
        (56).to_bytes(2, 'big'),
        (
            (False << MESSAGE_TYPE_SHIFT) |
            (True << DATA_VERIFIED_SHIFT) |
            (True << TRUNCATED_SHIFT) |
            (True << RECURSION_AVAILABLE_SHIFT) |
            (RESPONSE_CODE_OK << RESPONSE_CODE_SHIFT)
        ).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (1).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        (0).to_bytes(2, 'big'),
        
        (3).to_bytes(1, 'big'),
        b'www',
        (6).to_bytes(1, 'big'),
        b'go',
    ])
    
    yield (
        'label read end ouf of bound',
        data,
        (
            None,
            ResponseParsingError(
                RESPONSE_PARSING_ERROR_CODE_LABEL_READ_END_OUT_OF_BOUND,
                data,
                (len(data) - 2, len(data) + 4),
            ),
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).named_first().returning_last())
def test__parse_result_data(data):
    """
    Tests whether ``parse_result_data`` works as intended.
    
    Parameters
    ----------
    data : `bytes`
        Data to parse from.
    
    Returns
    -------
    output : ``(None | Result, None | ResponseParsingError)``
    """
    output = parse_result_data(data)
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    vampytest.assert_instance(output[0], Result, nullable = True)
    vampytest.assert_instance(output[1], ResponseParsingError, nullable = True)
    return output
