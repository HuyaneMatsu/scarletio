import vampytest

from ..constants import (
    IP_TYPE_IP_V4, IP_TYPE_IP_V6, NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES,
    NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
)
from ..resolve_configuration import NameServerConfiguration


def _assert_fields_set(name_server_configuration):
    """
    Asserts whether the given name server configuration has all of its fields set.
    
    Parameters
    ----------
    name_server_configuration : ``NameServerConfiguration``
        The instance to check.
    """
    vampytest.assert_instance(name_server_configuration, NameServerConfiguration)
    vampytest.assert_instance(name_server_configuration.ip_type, int)
    vampytest.assert_instance(name_server_configuration.ip_value, int)
    vampytest.assert_instance(name_server_configuration.supports_multiple_questions_in_queries, bool)
    vampytest.assert_instance(name_server_configuration.secure_connection_support_level, int)


def test__NameServerConfiguration__new():
    """
    Tests whether ``NameServerConfiguration.__new__`` works as intended.
    """
    ip_type = IP_TYPE_IP_V4
    ip_value = 1233555
    supports_multiple_questions_in_queries = False
    secure_connection_support_level = NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO
    
    name_server_configuration = NameServerConfiguration(
        ip_type,
        ip_value,
        supports_multiple_questions_in_queries,
        secure_connection_support_level,
    )
    _assert_fields_set(name_server_configuration)
    
    vampytest.assert_eq(name_server_configuration.ip_type, ip_type)
    vampytest.assert_eq(name_server_configuration.ip_value, ip_value)
    vampytest.assert_eq(
        name_server_configuration.supports_multiple_questions_in_queries, supports_multiple_questions_in_queries
    )
    vampytest.assert_eq(name_server_configuration.secure_connection_support_level, secure_connection_support_level)


def test__NameServerConfiguration__repr():
    """
    Tests whether ``NameServerConfiguration.__repr__`` works as intended.
    """
    ip_type = IP_TYPE_IP_V4
    ip_value = 1233555
    supports_multiple_questions_in_queries = False
    secure_connection_support_level = NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO
    
    name_server_configuration = NameServerConfiguration(
        ip_type,
        ip_value,
        supports_multiple_questions_in_queries,
        secure_connection_support_level,
    )
    
    output = repr(name_server_configuration)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    ip_type = IP_TYPE_IP_V4
    ip_value = 1233555
    supports_multiple_questions_in_queries = False
    secure_connection_support_level = NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO
    
    keyword_parameters = {
        'ip_type': ip_type,
        'ip_value': ip_value,
        'supports_multiple_questions_in_queries': supports_multiple_questions_in_queries,
        'secure_connection_support_level': secure_connection_support_level
    }
    
    yield (
        keyword_parameters,
        keyword_parameters,
        True,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'ip_type': IP_TYPE_IP_V6,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'ip_value': 98989889,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'supports_multiple_questions_in_queries': True,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'secure_connection_support_level': NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__NameServerConfiguration__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``NameServerConfiguration.__eq__`` works as intended.
    
    Parameters
    ----------
    keyword_parameters_0 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    keyword_parameters_1 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    name_server_configuration_0 = NameServerConfiguration(**keyword_parameters_0)
    name_server_configuration_1 = NameServerConfiguration(**keyword_parameters_1)
    
    output = name_server_configuration_0 == name_server_configuration_1
    vampytest.assert_instance(output, bool)
    return output
