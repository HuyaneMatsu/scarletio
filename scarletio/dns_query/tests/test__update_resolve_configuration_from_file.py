import vampytest

from ..constants import IP_TYPE_IP_V4, OPTION_ATTEMPTS_DEFAULT, OPTION_REQUIRED_DOT_COUNT_DEFAULT, OPTION_TIMEOUT_DEFAULT
from ..resolve_configuration import (
    NameServerConfiguration, ResolveConfiguration, update_resolve_configuration_from_file_content
)


def _iter_options():
    yield (
        (
            '# nyan'
        ),
        (
            None,
            OPTION_ATTEMPTS_DEFAULT,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            OPTION_REQUIRED_DOT_COUNT_DEFAULT,
            False,
            False,
            False,
            OPTION_TIMEOUT_DEFAULT,
            None,
            None,
        ),
    )
    yield (
        (
            'nameserver 8.8.8.8\n'
            'nameserver 8.8.4.4\n'
            'search komeiji.koishi\n'
            'sortlist 127.0.0.1\n'
            'options debug\n'
            'options rotate\n'
            'options no-aaaa\n'
            'options no-check-names\n'
            'options inet6\n'
            'options edn0\n'
            'options single-request\n'
            'options single-request-reopen\n'
            'options no-rld-query\n'
            'options use-vc\n'
            'options no-reload\n'
            'options trust-ad\n'
            'options edns0\n'
            'options no-tld-query\n'
            'options ndots:4\n'
            'options timeout:12\n'
            'options attempts:3\n'
        ),
        (
            (
                NameServerConfiguration(IP_TYPE_IP_V4, (8 << 24) | (8 << 16) | (8 << 8) | (8 << 0), False, False),
                NameServerConfiguration(IP_TYPE_IP_V4, (8 << 24) | (8 << 16) | (4 << 8) | (4 << 0), False, False),
            ),
            3,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            4,
            True,
            True,
            True,
            12,
            (
                (b'komeiji', b'koishi'),
            ),
            (
                '127.0.0.1',
            ),
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__update_resolve_configuration_from_file_content(content):
    """
    Tests whether ``update_resolve_configuration_from_file_content`` works as intended.
    
    Parameters
    ----------
    content : `str`
        The file's content.
    
    Returns
    -------
    output : ``(None | tuple<NameServerConfiguration>, int, 9 * bool, int, 3 * bool, int, 2 * None | tuple<str>, None | tuple<tuple<bytes>>)``
    """
    resolve_configuration = ResolveConfiguration()
    update_resolve_configuration_from_file_content(resolve_configuration, content)
    
    return (
        resolve_configuration.name_server_configurations,
        resolve_configuration.option_attempts,
        resolve_configuration.option_debug,
        resolve_configuration.option_disable_bind_checking,
        resolve_configuration.option_enable_dns_extension,
        resolve_configuration.option_force_tcp,
        resolve_configuration.option_limit_to_single_request,
        resolve_configuration.option_no_ip_v6_lookups,
        resolve_configuration.option_no_reload,
        resolve_configuration.option_no_unqualified_name_resolving,
        resolve_configuration.option_prefer_ip_v6,
        resolve_configuration.option_required_dot_count,
        resolve_configuration.option_rotate,
        resolve_configuration.option_set_verified_data_in_requests,
        resolve_configuration.option_single_request_re_open,
        resolve_configuration.option_timeout,
        resolve_configuration.searches,
        resolve_configuration.sort_list,
    )
