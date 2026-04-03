import vampytest

from ..constants import IP_TYPE_IP_V4
from ..resolve_configuration import NameServerConfiguration, ResolveConfiguration


def _assert_fields_set(resolve_configuration):
    """
    Asserts whether all fields of the given resolve configuration are set.
    
    Parameters
    ----------
    resolve_configuration : ``ResolveConfiguration``
        The instance to check.
    """
    vampytest.assert_instance(resolve_configuration, ResolveConfiguration)
    vampytest.assert_instance(resolve_configuration.name_server_configurations, tuple, nullable = True)
    vampytest.assert_instance(resolve_configuration.name_server_configurations_fallback, tuple, nullable = True)
    vampytest.assert_instance(resolve_configuration.option_attempts, int)
    vampytest.assert_instance(resolve_configuration.option_debug, bool)
    vampytest.assert_instance(resolve_configuration.option_disable_bind_checking, bool)
    vampytest.assert_instance(resolve_configuration.option_enable_dns_extension, bool)
    vampytest.assert_instance(resolve_configuration.option_force_tcp, bool)
    vampytest.assert_instance(resolve_configuration.option_limit_to_single_request, bool)
    vampytest.assert_instance(resolve_configuration.option_no_ip_v6_lookups, bool)
    vampytest.assert_instance(resolve_configuration.option_no_reload, bool)
    vampytest.assert_instance(resolve_configuration.option_no_unqualified_name_resolving, bool)
    vampytest.assert_instance(resolve_configuration.option_prefer_ip_v6, bool)
    vampytest.assert_instance(resolve_configuration.option_required_dot_count, int)
    vampytest.assert_instance(resolve_configuration.option_rotate, bool)
    vampytest.assert_instance(resolve_configuration.option_set_verified_data_in_requests, bool)
    vampytest.assert_instance(resolve_configuration.option_single_request_re_open, bool)
    vampytest.assert_instance(resolve_configuration.option_timeout, float)
    vampytest.assert_instance(resolve_configuration.preference_query_transport_type, int)
    vampytest.assert_instance(resolve_configuration.preference_raise_upon_response_parsing_error, bool)
    vampytest.assert_instance(resolve_configuration.searches, tuple, nullable = True)
    vampytest.assert_instance(resolve_configuration.searches_fallback, tuple, nullable = True)
    vampytest.assert_instance(resolve_configuration.sort_list, tuple, nullable = True)


def test__ResolveConfiguration__new():
    """
    Tests whether ``ResolveConfiguration.__new__`` works as intended.
    """
    resolve_configuration = ResolveConfiguration()
    _assert_fields_set(resolve_configuration)


def test__ResolveConfiguration__repr__default():
    """
    Tests whether ``ResolveConfiguration.__repr__`` works as intended.
    
    Case: default.
    """
    resolve_configuration = ResolveConfiguration()
    
    output = repr(resolve_configuration)
    vampytest.assert_instance(output, str)


def test__ResolveConfiguration__repr__all_fields():
    """
    Tests whether ``ResolveConfiguration.__repr__`` works as intended.
    
    Case: all fields.
    """
    resolve_configuration = ResolveConfiguration()
    resolve_configuration.name_server_configurations = (
        NameServerConfiguration(IP_TYPE_IP_V4, (8 << 24) | (8 << 16) | (8 << 8) | (8 << 0), False, False),
        NameServerConfiguration(IP_TYPE_IP_V4, (8 << 24) | (8 << 16) | (4 << 8) | (4 << 0), False, False),
    )
    resolve_configuration.option_attempts = 3
    resolve_configuration.option_debug = True
    resolve_configuration.option_disable_bind_checking = True
    resolve_configuration.option_enable_dns_extension = True
    resolve_configuration.option_force_tcp = True
    resolve_configuration.option_limit_to_single_request = True
    resolve_configuration.option_no_ip_v6_lookups = True
    resolve_configuration.option_no_reload = True
    resolve_configuration.option_no_unqualified_name_resolving = True
    resolve_configuration.option_prefer_ip_v6 = True
    resolve_configuration.option_required_dot_count = 6
    resolve_configuration.option_rotate = True
    resolve_configuration.option_set_verified_data_in_requests = True
    resolve_configuration.option_single_request_re_open = True
    resolve_configuration.option_timeout = 5.0
    resolve_configuration.searches = (
        'komeiji.koishi',
    )
    resolve_configuration.sort_list = (
        '127.0.0.1',
    )
    
    output = repr(resolve_configuration)
    vampytest.assert_instance(output, str)
