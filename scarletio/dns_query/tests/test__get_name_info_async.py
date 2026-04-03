from itertools import count
from socket import (
    EAI_NONAME as ERROR_CODE_ADDRESS_INFO_NO_NAME, EAI_SERVICE as ERROR_CODE_ADDRESS_INFO_SERVICE,
    NI_DGRAM as NAME_INFO_DATAGRAM, NI_NAMEREQD as NAME_INFO_RAISE_ERROR_IF_NAME_CANNOT_BE_DETERMINED,
    NI_NUMERICSERV as NAME_INFO_NUMERIC_SERVICE
)

import vampytest

from ...core import get_event_loop

from ..constants import (
    IP_TYPE_IP_V4, NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
    NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES, QUERY_TRANSPORT_TYPE_TLS, QUERY_TRANSPORT_TYPE_UDP
)
from ..requests import get_name_info_async
from ..resolve_configuration import NameServerConfiguration, ResolveConfiguration

from .helpers import clear_request_data, get_request_datas, patch_event_loop, set_response_datas


def _iter_options():
    request_ip_v4_0 = (
        b'\x00\x00\x01\x10\x00\x01\x00\x00\x00\x00\x00\x00\x010\x0297\x03114\x03188\x07in-addr\x04arpa'
        b'\x00\x00\x0c\x00\x01'
    )
    
    request_ip_v6_0 = (
        b'\x00\x00\x01\x10\x00\x01\x00\x00\x00\x00\x00\x00\x013\x010\x010\x010\x010\x010\x010\x010\x010\x010\x010'
        b'\x010\x010\x010\x010\x010\x010\x010\x010\x010\x010\x012\x011\x013\x011\x01c\x018\x019\x016\x010\x01a\x012'
        b'\x03ip6\x04arpa\x00\x00\x0c\x00\x01'
    )
    
    response_ip_v4_0 = (
        b'\x00\x00\x81\x83\x00\x01\x00\x00\x00\x01\x00\x00\x010\x0297\x03114\x03188\x07in-addr\x04arpa'
        b'\x00\x00\x0c\x00\x01\xc0\x0e\x00\x06\x00\x01\x00\x00\x01}\x002\x04darl\x02ns\ncloudflare\x03com'
        b'\x00\x03dns\xc0?\x88i\xa7\xee\x00\x00\'\x10\x00\x00\t`\x00\t:\x80\x00\x00\x0e\x10'
    )
    response_ip_v6_0 = (
        b'\x00\x00\x81\x83\x00\x01\x00\x00\x00\x00\x00\x00\x013\x010\x010\x010\x010\x010\x010\x010\x010\x010\x010'
        b'\x010\x010\x010\x010\x010\x010\x010\x010\x010\x010\x012\x011\x013\x011\x01c\x018\x019\x016\x010\x01a'
        b'\x012\x03ip6\x04arpa\x00\x00\x0c\x00\x01'
    )
    
    request_ip_v4_1 = (
        b'\x00\x00\x01\x10\x00\x01\x00\x00\x00\x00\x00\x00\x014\x014\x018\x018\x07in-addr\x04arpa\x00\x00\x0c\x00\x01'
    )
    request_ip_v6_1 = (
        b'\x00\x00\x01\x10\x00\x01\x00\x00\x00\x00\x00\x00\x018\x018\x018\x018\x010\x010\x010\x010\x010\x010\x010'
        b'\x010\x010\x010\x010\x010\x010\x010\x010\x010\x010\x016\x018\x014\x010\x016\x018\x014\x011\x010\x010'
        b'\x012\x03ip6\x04arpa\x00\x00\x0c\x00\x01'
    )
    response_ip_v4_1 = (
        b'\x00\x00\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x014\x014\x018\x018\x07in-addr\x04arpa\x00\x00\x0c\x00\x01'
        b'\xc0\x0c\x00\x0c\x00\x01\x00\x00E\x02\x00\x0c\x03dns\x06google\x00'
    )
    response_ip_v6_1 = (
        b'\x00\x00\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x018\x018\x018\x018\x010\x010\x010\x010\x010\x010\x010'
        b'\x010\x010\x010\x010\x010\x010\x010\x010\x010\x010\x016\x018\x014\x010\x016\x018\x014\x011\x010\x010'
        b'\x012\x03ip6\x04arpa\x00\x00\x0c\x00\x01\xc0\x0c\x00\x0c\x00\x01\x00\x00\xb8\xcc\x00\x0c\x03dns\x06google\x00'
    )
    
    request_ip_v4_2 = b'\x00\x00\x01\x10\x00\x01\x00\x00\x00\x00\x00\x00\tylvapedia\x04wiki\x00\x00\x01\x00\x01'
    response_ip_v4_2 = (
        b'\x00\x00\x81\x80\x00\x01\x00\x02\x00\x00\x00\x00\tylvapedia\x04wiki'
        b'\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x01\x0f\x00\x04\xbcr`'
        b'\x00\xc0\x0c\x00\x01\x00\x01\x00\x00\x01\x0f\x00\x04\xbcra\x00'
    )
    
    resolve_configuration_0 = ResolveConfiguration()
    resolve_configuration_0.name_server_configurations = (
        NameServerConfiguration(
            IP_TYPE_IP_V4,
            88888,
            False,
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES,
        ),
    )
    
    resolve_configuration_1 = ResolveConfiguration()
    resolve_configuration_1.name_server_configurations = None
    resolve_configuration_1.name_server_configurations_fallback = None
    
    resolve_configuration_2 = ResolveConfiguration()
    resolve_configuration_2.name_server_configurations = (
        NameServerConfiguration(
            IP_TYPE_IP_V4,
            88888,
            False,
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
        ),
    )
    resolve_configuration_2.preference_raise_upon_response_parsing_error = True
    
    resolve_configuration_3 = ResolveConfiguration()
    resolve_configuration_3.name_server_configurations = (
        NameServerConfiguration(
            IP_TYPE_IP_V4,
            88888,
            False,
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES,
        ),
    )
    resolve_configuration_3.preference_query_transport_type = QUERY_TRANSPORT_TYPE_UDP
    
    resolve_configuration_4 = ResolveConfiguration()
    resolve_configuration_4.name_server_configurations = (
        NameServerConfiguration(
            IP_TYPE_IP_V4,
            88888,
            False,
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
        ),
    )
    resolve_configuration_4.preference_query_transport_type = QUERY_TRANSPORT_TYPE_TLS
    
    resolve_configuration_5 = ResolveConfiguration()
    resolve_configuration_5.name_server_configurations = (
        NameServerConfiguration(
            IP_TYPE_IP_V4,
            88888,
            False,
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES,
        ),
    )
    resolve_configuration_5.preference_query_transport_type = QUERY_TRANSPORT_TYPE_TLS
    
    
    yield (
        'ip v6, no answer',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
        ],
        ('2a06:98c1:3120::3%0', 'https'),
        0,
        '',
        resolve_configuration_0,
        ('2a06:98c1:3120::3', 443, 0, 0),
        0,
    )
    
    yield (
        'ip v4, no answer',
        [
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, len(response_ip_v4_0).to_bytes(2, 'big') + response_ip_v4_0),
        ],
        ('188.114.97.0', 'https'),
        0,
        '',
        resolve_configuration_0,
        ('188.114.97.0', 443),
        0,
    )
    
    
    yield (
        'ip v6, with answer',
        [
            len(request_ip_v6_1).to_bytes(2, 'big') + request_ip_v6_1,
        ],
        [
            (True, len(response_ip_v6_1).to_bytes(2, 'big') + response_ip_v6_1),
        ],
        ('dns.google', 'https'),
        0,
        '',
        resolve_configuration_0,
        ('2001:4860:4860::8888', 443, 0, 0),
        0,
    )
    
    yield (
        'ip v4, with answer',
        [
            len(request_ip_v4_1).to_bytes(2, 'big') + request_ip_v4_1,
        ],
        [
            (True, len(response_ip_v4_1).to_bytes(2, 'big') + response_ip_v4_1),
        ],
        ('dns.google', 'https'),
        0,
        '',
        resolve_configuration_0,
        ('8.8.4.4', 443),
        0,
    )
    
    yield (
        'ip ??',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_SERVICE,
        '`socket_address` length can be 2 or 4, got 3; socket_address = (\'8.8.4.4\', 443, 0).',
        resolve_configuration_0,
        ('8.8.4.4', 443, 0),
        0,
    )
    
    yield (
        'Many replies',
        [
            len(request_ip_v4_2).to_bytes(2, 'big') + request_ip_v4_2,
        ],
        [
            (True, len(response_ip_v4_2).to_bytes(2, 'big') + response_ip_v4_2),
        ],
        None,
        ERROR_CODE_ADDRESS_INFO_NO_NAME,
        '`get_address_info` resolved to multiple addresses.',
        resolve_configuration_0,
        ('ylvapedia.wiki', 443),
        0,
    )
    
    
    yield (
        'ip v6, no answer, raise if name cannot be determined',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
        ],
        None,
        ERROR_CODE_ADDRESS_INFO_NO_NAME,
        'Name and service not known.',
        resolve_configuration_0,
        ('2a06:98c1:3120::3', 443, 0, 0),
        NAME_INFO_RAISE_ERROR_IF_NAME_CANNOT_BE_DETERMINED,
    )
    
    yield (
        'ip v4, numeric service',
        [
            len(request_ip_v4_1).to_bytes(2, 'big') + request_ip_v4_1,
        ],
        [
            (True, len(response_ip_v4_1).to_bytes(2, 'big') + response_ip_v4_1),
        ],
        ('dns.google', '443'),
        0,
        '',
        resolve_configuration_0,
        ('8.8.4.4', 443),
        NAME_INFO_NUMERIC_SERVICE,
    )
    
    yield (
        'ip v4, bad protocol',
        [
            len(request_ip_v4_1).to_bytes(2, 'big') + request_ip_v4_1,
        ],
        [
            (True, len(response_ip_v4_1).to_bytes(2, 'big') + response_ip_v4_1),
        ],
        None,
        ERROR_CODE_ADDRESS_INFO_NO_NAME,
        'port/proto not found',
        resolve_configuration_0,
        ('8.8.4.4', 120),
        NAME_INFO_DATAGRAM,
    )


@vampytest._(vampytest.call_from(_iter_options()).named_first())
async def test__get_name_info_async(
    expected_request_data,
    response_datas,
    expected_output,
    expected_error_code,
    expected_error_message,
    resolve_configuration,
    socket_address,
    socket_flags,
):
    """
    Tests whether ``get_name_info_async`` works as intended.
    
    This function is a coroutine.
    
    Parameters
    ----------
    expected_request_data : `None | list<bytes>`
        Expected data to be requested.
    
    response_datas : `None | list<(bool<True>, bytes) | (bool<False>, BaseException)>`
        Data to reply with on request with.
    
    expected_output : `None | list<(int, int, int, str, (str, int) | (str, int, int, int))>`
        Expected output.
    
    expected_error_code : `int`
        Excepted error code to be received.
    
    expected_error_message : `str`
        Excepted error message to be received.
    
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration to use.
    
    socket_address : `(str, int) | (str, int, int, int)`
        Socket address to query for.
    
    socket_flags : `int`
        Socket flags to query as.
    """
    if (response_datas is not None):
        response_datas = response_datas.copy()
    
    set_response_datas(response_datas)
    clear_request_data()
    event_loop = get_event_loop()
    
    counter = count()
    
    def _get_next_id():
        nonlocal counter
        return (next(counter) & 0xffff)
    
    mocked = vampytest.mock_globals(
        get_name_info_async,
        3,
        _get_next_id = _get_next_id,
    )
    
    with patch_event_loop(event_loop):
        try:
            output = await mocked(
                event_loop,
                socket_address,
                socket_flags = socket_flags,
                resolve_configuration = resolve_configuration,
            )
        except OSError as exception:
            error_code = exception.errno
            error_message = exception.strerror
            output = None
        
        else:
            error_code = 0
            error_message = ''
    
    
    vampytest.assert_eq(output, expected_output)
    vampytest.assert_eq(error_code, expected_error_code)
    vampytest.assert_eq(error_message, expected_error_message)
    
    actual_request_data = get_request_datas()
    vampytest.assert_eq(actual_request_data, expected_request_data)
