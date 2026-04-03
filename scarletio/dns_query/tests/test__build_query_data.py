import vampytest

from ..building_and_parsing import build_query_data
from ..constants import (
    CLASS_CODE_INTERNET, DATA_VERIFICATION_DESIRED_SHIFT, MESSAGE_TYPE_SHIFT, OPERATION_CODE_QUERY_STANDARD,
    OPERATION_CODE_SHIFT, RECURSION_DESIRED_SHIFT, RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
)
from ..resource_record import ResourceRecord
from ..query import Query
from ..question import Question
from ..resolve_configuration import ResolveConfiguration


def _iter_options():
    yield (
        Query(
            56,
            True,
            True,
            (
                Question(
                    (b'www', b'google', b'com'),
                    CLASS_CODE_INTERNET,
                    RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
                ),
            ),
            (
                ResourceRecord(
                    None,
                    CLASS_CODE_INTERNET,
                    RESOURCE_RECORD_TYPE_IP_V4_ADDRESS,
                    123,
                    b'ner',
                ),
            ),
        ),
        ResolveConfiguration(),
        b''.join([
            (56).to_bytes(2, 'big'),
            (
                (False << MESSAGE_TYPE_SHIFT) |
                (OPERATION_CODE_QUERY_STANDARD << OPERATION_CODE_SHIFT) |
                (True << RECURSION_DESIRED_SHIFT) |
                (True << DATA_VERIFICATION_DESIRED_SHIFT)
            ).to_bytes(2, 'big'),
            (1).to_bytes(2, 'big'),
            (0).to_bytes(2, 'big'),
            (0).to_bytes(2, 'big'),
            (1).to_bytes(2, 'big'),
            
            (3).to_bytes(1, 'big'),
            b'www',
            (6).to_bytes(1, 'big'),
            b'google',
            (3).to_bytes(1, 'big'),
            b'com',
            (0).to_bytes(1, 'big'),
            CLASS_CODE_INTERNET.to_bytes(2, 'big'),
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS.to_bytes(2, 'big'),
            
            (0).to_bytes(1, 'big'),
            CLASS_CODE_INTERNET.to_bytes(2, 'big'),
            RESOURCE_RECORD_TYPE_IP_V4_ADDRESS.to_bytes(2, 'big'),
            (123).to_bytes(4, 'big'),
            (3).to_bytes(2, 'big'),
            b'ner',
        ]),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__build_query_data(query, resolve_configuration):
    """
    Tests whether ``build_query_data`` works as intended.
    
    Parameters
    ----------
    query : ``Query``
        Query to build data for.
    
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration.
    
    Returns
    -------
    output : `bytes`
    """
    output = build_query_data(query, resolve_configuration)
    vampytest.assert_instance(output, bytes)
    return output
