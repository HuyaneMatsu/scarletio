from errno import ECONNREFUSED as ERROR_CODE_CONNECTION_REFUSED
from itertools import count
from socket import (
    AF_INET as SOCKET_FAMILY_IP_V4, AF_INET6 as SOCKET_FAMILY_IP_V6, AF_UNSPEC as SOCKET_FAMILY_UNSPECIFIED,
    AI_ADDRCONFIG as ADDRESS_INFO_ADDRESS_CONFIGURATION, AI_NUMERICHOST as ADDRESS_INFO_NUMERIC_HOST,
    AI_V4MAPPED as ADDRESS_INFO_IP_V4_MAPPED, EAI_FAIL as ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
    EAI_FAMILY as ERROR_CODE_ADDRESS_INFO_FAMILY, EAI_NONAME as ERROR_CODE_ADDRESS_INFO_NO_NAME,
    EAI_SERVICE as ERROR_CODE_ADDRESS_INFO_SERVICE, EAI_SOCKTYPE as ERROR_CODE_ADDRESS_INFO_SOCKET_TYPE,
    SOCK_DGRAM as SOCKET_TYPE_DATAGRAM, SOCK_RAW as SOCKET_TYPE_RAW, SOCK_STREAM as SOCKET_TYPE_STREAM,
    SOL_IP as SOCKET_OPTION_LEVEL_IP, SOL_TCP as SOCKET_OPTION_LEVEL_TCP, SOL_UDP as SOCKET_OPTION_LEVEL_UDP,
    gaierror as GetAddressInfoError
)

import vampytest

from ...core import get_event_loop

from ..constants import (
    IP_TYPE_IP_V4, NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
    NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES, QUERY_TRANSPORT_TYPE_TLS, QUERY_TRANSPORT_TYPE_UDP
)
from ..requests import get_address_info_async
from ..resolve_configuration import NameServerConfiguration, ResolveConfiguration

from .helpers import clear_request_data, get_request_datas, patch_event_loop, set_response_datas


def _iter_options():
    request_ip_v4_0 = b'\x00\x02\x01\x10\x00\x01\x00\x00\x00\x00\x00\x00\tylvapedia\x04wiki\x00\x00\x01\x00\x01'
    request_ip_v6_0 = b'\x00\x01\x01\x10\x00\x01\x00\x00\x00\x00\x00\x00\tylvapedia\x04wiki\x00\x00\x1c\x00\x01'
    response_ip_v4_0 = (
        b'\x00\x02\x81\x80\x00\x01\x00\x02\x00\x00\x00\x00\tylvapedia\x04wiki'
        b'\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x01\x0f\x00\x04\xbcr`'
        b'\x00\xc0\x0c\x00\x01\x00\x01\x00\x00\x01\x0f\x00\x04\xbcra\x00'
    )
    response_ip_v6_0 = (
        b'\x00\x01\x81\x80\x00\x01\x00\x02\x00\x00\x00\x00\tylvapedia\x04wiki'
        b'\x00\x00\x1c\x00\x01\xc0\x0c\x00\x1c\x00\x01\x00\x00\x01\x0f\x00\x10*\x06\x98\xc11 '
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc0\x0c\x00\x1c\x00\x01\x00\x00\x01\x0f'
        b'\x00\x10*\x06\x98\xc11!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03'
    )
    
    request_ip_v4_1 = b'\x00\x00\x01\x10\x00\x01\x00\x00\x00\x00\x00\x00\tylvapedia\x04wiki\x00\x00\x01\x00\x01'
    request_ip_v6_1 = b'\x00\x00\x01\x10\x00\x01\x00\x00\x00\x00\x00\x00\tylvapedia\x04wiki\x00\x00\x1c\x00\x01'
    response_ip_v4_1 = (
        b'\x00\x00\x81\x80\x00\x01\x00\x02\x00\x00\x00\x00\tylvapedia\x04wiki'
        b'\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x01\x0f\x00\x04\xbcr`'
        b'\x00\xc0\x0c\x00\x01\x00\x01\x00\x00\x01\x0f\x00\x04\xbcra\x00'
    )
    response_ip_v6_1 = (
        b'\x00\x00\x81\x80\x00\x01\x00\x02\x00\x00\x00\x00\tylvapedia\x04wiki'
        b'\x00\x00\x1c\x00\x01\xc0\x0c\x00\x1c\x00\x01\x00\x00\x01\x0f\x00\x10*\x06\x98\xc11 '
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc0\x0c\x00\x1c\x00\x01\x00\x00\x01\x0f'
        b'\x00\x10*\x06\x98\xc11!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03'
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
        'No input',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_NO_NAME,
        'Name and service not known.',
        resolve_configuration_0,
        None,
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'input host, no port',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
            (True, len(response_ip_v4_0).to_bytes(2, 'big') + response_ip_v4_0),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('188.114.97.0', 0)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'Input host and port (string)',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
            (True, len(response_ip_v4_0).to_bytes(2, 'big') + response_ip_v4_0),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3120::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3120::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3121::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3121::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.96.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.96.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 443)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        'https',
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'Input host and port (int)',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
            (True, len(response_ip_v4_0).to_bytes(2, 'big') + response_ip_v4_0),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3120::3', 123, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3120::3', 123, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3121::3', 123, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3121::3', 123, 0, 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.96.0', 123)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.96.0', 123)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 123)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 123)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        123,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'Input host and port (wrong type)',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_SERVICE,
        'Port can be either `None`, `int` or `str`, got type(port) = float; port = 12.6.',
        resolve_configuration_0,
        'ylvapedia.wiki',
        12.6,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'Input host and port, use udp',
        [
            request_ip_v6_0,
            request_ip_v4_0,
        ],
        [
            (True, response_ip_v6_0),
            (True, response_ip_v4_0),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3120::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3120::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3121::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3121::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.96.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.96.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 443)),
        ],
        0,
        '',
        resolve_configuration_3,
        'ylvapedia.wiki',
        'https',
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'Input ip and port',
        None,
        None,
        [
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 443)),
        ],
        0,
        '',
        resolve_configuration_0,
        '188.114.97.0',
        'https',
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'Input ip and port, claim it is an ip',
        None,
        None,
        [
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 443)),
        ],
        0,
        '',
        resolve_configuration_0,
        '188.114.97.0',
        'https',
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        ADDRESS_INFO_NUMERIC_HOST,
    )
    
    yield (
        'Input host and port, claim it is an ip',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_NO_NAME,
        'Name and service not known.',
        resolve_configuration_0,
        'ylvapedia.wiki',
        'https',
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        ADDRESS_INFO_NUMERIC_HOST,
    )
    
    yield (
        'input host, ip v4',
        [
            len(request_ip_v4_1).to_bytes(2, 'big') + request_ip_v4_1,
        ],
        [
            (True, len(response_ip_v4_1).to_bytes(2, 'big') + response_ip_v4_1),
        ],
        [
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('188.114.97.0', 0)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_IP_V4,
        0,
        0,
        0,
    )
    
    yield (
        'input host, ip v6',
        [
            len(request_ip_v6_1).to_bytes(2, 'big') + request_ip_v6_1,
        ],
        [
            (True, len(response_ip_v6_1).to_bytes(2, 'big') + response_ip_v6_1),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_IP_V6,
        0,
        0,
        0,
    )
    
    yield (
        'input host, wrong family',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_FAMILY,
        'Socket family not supported; socket_family = 999.',
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        999,
        0,
        0,
        0,
    )
    
    yield (
        'input host, type datagram',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
            (True, len(response_ip_v4_0).to_bytes(2, 'big') + response_ip_v4_0),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3120::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3121::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.96.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 443)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        'https',
        SOCKET_FAMILY_UNSPECIFIED,
        SOCKET_TYPE_DATAGRAM,
        0,
        0,
    )
    
    yield (
        'input host, type stream',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
            (True, len(response_ip_v4_0).to_bytes(2, 'big') + response_ip_v4_0),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3120::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3121::3', 443, 0, 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.96.0', 443)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 443)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        'https',
        SOCKET_FAMILY_UNSPECIFIED,
        SOCKET_TYPE_STREAM,
        0,
        0,
    )
    
    yield (
        'input host, type wrong',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_SOCKET_TYPE,
        'Socket type not supported; socket_type = 999.',
        resolve_configuration_0,
        'ylvapedia.wiki',
        'https',
        SOCKET_FAMILY_UNSPECIFIED,
        999,
        0,
        0,
    )
    
    yield (
        'input host, protocol udp',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
            (True, len(response_ip_v4_0).to_bytes(2, 'big') + response_ip_v4_0),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 0)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        SOCKET_OPTION_LEVEL_UDP,
        0,
    )
    
    yield (
        'input host, protocol tcp',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
            (True, len(response_ip_v4_0).to_bytes(2, 'big') + response_ip_v4_0),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 0)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        SOCKET_OPTION_LEVEL_TCP,
        0,
    )
    
    yield (
        'input host, protocol ip; equals to default, so does nothing',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, len(response_ip_v6_0).to_bytes(2, 'big') + response_ip_v6_0),
            (True, len(response_ip_v4_0).to_bytes(2, 'big') + response_ip_v4_0),
        ],
        [
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('2a06:98c1:3120::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V6, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('2a06:98c1:3121::3', 0, 0, 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('188.114.96.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_DATAGRAM, SOCKET_OPTION_LEVEL_UDP, '', ('188.114.97.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_STREAM, SOCKET_OPTION_LEVEL_TCP, '', ('188.114.97.0', 0)),
            (SOCKET_FAMILY_IP_V4, SOCKET_TYPE_RAW, SOCKET_OPTION_LEVEL_IP, '', ('188.114.97.0', 0)),
        ],
        0,
        '',
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        SOCKET_OPTION_LEVEL_IP,
        0,
    )
    
    yield (
        'input host, type & protocol udp mismatch',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_SERVICE,
        (
            f'Protocol not supported for socket type; socket_type = {SOCKET_TYPE_STREAM!r}; '
            f'socket_protocol = {SOCKET_OPTION_LEVEL_UDP!r}.'
        ),
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        SOCKET_TYPE_STREAM,
        SOCKET_OPTION_LEVEL_UDP,
        0,
    )
    
    yield (
        'unsupported configuration -> address info address configuration',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
        (
            f'Non recoverable failure in name resolution; Unsupported socket flags given: '
            f'{ADDRESS_INFO_ADDRESS_CONFIGURATION!r} / {ADDRESS_INFO_IP_V4_MAPPED!r}; '
            f'socket_flags = {ADDRESS_INFO_ADDRESS_CONFIGURATION!r}.'
        ),
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        ADDRESS_INFO_ADDRESS_CONFIGURATION,
    )
    
    yield (
        'unsupported configuration -> ip v4 mapped',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
        (
            f'Non recoverable failure in name resolution; Unsupported socket flags given: '
            f'{ADDRESS_INFO_ADDRESS_CONFIGURATION!r} / {ADDRESS_INFO_IP_V4_MAPPED!r}; '
            f'socket_flags = {ADDRESS_INFO_IP_V4_MAPPED!r}.'
        ),
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        ADDRESS_INFO_IP_V4_MAPPED,
    )
    
    yield (
        'no name server configuration',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
        'No name server to query from.',
        resolve_configuration_1,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'tls query type, but no name servers support it',
        None,
        None,
        None,
        ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
        (
            'Permanent failure in name resolution; '
            'Transport type TLS has been specified, but non of the name servers support it.'
        ),
        resolve_configuration_4,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'tls query type, name server fails to support it (x1 query)',
        None,
        [
            (False, ConnectionRefusedError(ERROR_CODE_CONNECTION_REFUSED, 'message')),
        ],
        None,
        ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
        (
            'Permanent failure in name resolution; '
            'Transport type TLS has been specified, but non of the name servers support it.'
        ),
        resolve_configuration_5,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_IP_V4,
        0,
        0,
        0,
    )
    
    yield (
        'tls query type, name server fails to support it (x2 query)',
        None,
        [
            (False, ConnectionRefusedError(ERROR_CODE_CONNECTION_REFUSED, 'message')),
            (False, ConnectionRefusedError(ERROR_CODE_CONNECTION_REFUSED, 'message')),
        ],
        None,
        ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
        (
            'Permanent failure in name resolution; '
            'Transport type TLS has been specified, but non of the name servers support it.'
        ),
        resolve_configuration_5,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'input host, no port, all result fails to be parsed.',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, b'\x01\x00\x00'),
            (True, b'\x01\x00\x00'),
        ],
        None,
        ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
        'Temporary failure in name resolution.',
        resolve_configuration_0,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )
    
    yield (
        'input host, no port, all result fails to be parsed with raise.',
        [
            len(request_ip_v6_0).to_bytes(2, 'big') + request_ip_v6_0,
            # len(request_ip_v4_0).to_bytes(2, 'big') + request_ip_v4_0,
        ],
        [
            (True, b'\x01\x00\x00'),
            # (True, b'\x01\x00\x00'),
        ],
        None,
        ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
        'Parsing dns response failed.',
        resolve_configuration_2,
        'ylvapedia.wiki',
        None,
        SOCKET_FAMILY_UNSPECIFIED,
        0,
        0,
        0,
    )


@vampytest._(vampytest.call_from(_iter_options()).named_first())
async def test__get_address_info_async(
    expected_request_data,
    response_datas,
    expected_output,
    expected_error_code,
    expected_error_message,
    resolve_configuration,
    host_name,
    port,
    socket_family,
    socket_type,
    socket_protocol,
    socket_flags,
):
    """
    Tests whether ``get_address_info_async`` works as intended.
    
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
    
    host_name : `None | str`
        Host name to query for.
    
    port : `None | int | str`
        Port to query for.
    
    socket_family : `int`
        Socket family to query for.
    
    socket_type : `int`
        Socket type to query for.
    
    socket_protocol : `int`
        Socket protocol to query for.
    
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
        get_address_info_async,
        2,
        _get_next_id = _get_next_id,
    )
    
    with patch_event_loop(event_loop):
        try:
            output = await mocked(
                event_loop,
                host_name,
                port,
                socket_family = socket_family,
                socket_type = socket_type,
                socket_protocol = socket_protocol,
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
