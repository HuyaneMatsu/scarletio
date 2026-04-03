import vampytest

from ..constants import (
    IP_TYPE_IP_V4, NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_MAYBE,
    NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
    NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES
)
from ..resolve_configuration import NameServerConfiguration, update_name_server_configuration_from_parsed


def _iter_options():
    yield (
        False,
        NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
        {},
        (
            False,
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
        ),
    )
    
    yield (
        True,
        NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES,
        {},
        (
            True,
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES,
        ),
    )
    
    yield (
        False,
        NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
        {
            'Resolve' : {
                'DNSOverTLS': 'yes',
            },
        },
        (
            False,
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_MAYBE,
        ),
    )
    
    yield (
        False,
        NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
        {
            'Resolve' : {
                'DNSOverTLS': 'no',
            },
        },
        (
            False,
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__update_name_server_configuration_from_parsed(
    supports_multiple_questions_in_queries,
    secure_connection_support_level,
    configuration,
):
    """
    Tests whether ``update_name_server_configuration_from_parsed`` works as intended.
    
    Parameters
    ----------
    supports_multiple_questions_in_queries : `bool`
        Whether the name server supports multiple questions in a single query.
    
    secure_connection_support_level : `int`
        Whether the server supports secure connections.
    
    configuration : `dict<str, dict<str, str>>`
        Configuration to update with.
    
    Returns
    -------
    fields : `(bool, int)`
    """
    name_server_configuration = NameServerConfiguration(
        IP_TYPE_IP_V4,
        5454656565,
        supports_multiple_questions_in_queries,
        secure_connection_support_level,
    )
    update_name_server_configuration_from_parsed(name_server_configuration, configuration)
    
    return (
        name_server_configuration.supports_multiple_questions_in_queries,
        name_server_configuration.secure_connection_support_level,
    )
