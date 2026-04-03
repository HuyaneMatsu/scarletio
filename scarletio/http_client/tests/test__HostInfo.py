from socket import AddressFamily, SocketKind

import vampytest

from ..host_info import HostInfo


def _assert_fields_set(host_info):
    """
    Asserts whether every fields are set of the given host info.
    
    Parameters
    ----------
    host_info : ``HostInfo``
        The host info to check.
    """
    vampytest.assert_instance(host_info, HostInfo)
    vampytest.assert_instance(host_info.family, AddressFamily)
    vampytest.assert_instance(host_info.flags, int)
    vampytest.assert_instance(host_info.host, str)
    vampytest.assert_instance(host_info.host_name, str)
    vampytest.assert_instance(host_info.port, int)
    vampytest.assert_instance(host_info.protocol, int)


def test__HostInfo__new():
    """
    Tests whether ``HostInfo.__new__`` works as intended.
    """
    family = AddressFamily.AF_INET
    flags = 3
    host = '1.1.1.1'
    host_name = 'orin'
    port = 96
    protocol = 123
    
    host_info = HostInfo(
        family,
        flags,
        host,
        host_name,
        port,
        protocol,
    )
    _assert_fields_set(host_info)
    
    vampytest.assert_eq(host_info.family, family)
    vampytest.assert_eq(host_info.flags, flags)
    vampytest.assert_eq(host_info.host, host)
    vampytest.assert_eq(host_info.host_name, host_name)
    vampytest.assert_eq(host_info.port, port)
    vampytest.assert_eq(host_info.protocol, protocol)


def test__HostInfo__from_ip():
    """
    Tests whether ``HostInfo.from_ip`` works as intended.
    """
    family = AddressFamily.AF_INET
    host = '1.1.1.1'
    port = 96
    
    host_info = HostInfo.from_ip(
        host,
        port,
        family,
    )
    _assert_fields_set(host_info)
    
    vampytest.assert_eq(host_info.family, family)
    vampytest.assert_eq(host_info.host, host)
    vampytest.assert_eq(host_info.host_name, host)
    vampytest.assert_eq(host_info.port, port)


def test__HostInfo__from_address_info():
    """
    Tests whether ``HostInfo.from_address_info`` works as intended.
    """
    family = AddressFamily.AF_INET
    host = '1.1.1.1'
    host_name = 'orin'
    port = 96
    protocol = 123
    address_info = (family, SocketKind.SOCK_STREAM, protocol, '', (host, port))
    
    host_info = HostInfo.from_address_info(
        host_name,
        address_info,
    )
    _assert_fields_set(host_info)
    
    vampytest.assert_eq(host_info.family, family)
    vampytest.assert_eq(host_info.host, host)
    vampytest.assert_eq(host_info.host_name, host_name)
    vampytest.assert_eq(host_info.port, port)
    vampytest.assert_eq(host_info.protocol, protocol)


def test__HostInfo__repr():
    """
    Tests whether ``HostInfo.__repr__`` works as intended.
    """
    family = AddressFamily.AF_INET
    flags = 3
    host = '1.1.1.1'
    host_name = 'orin'
    port = 96
    protocol = 123
    
    host_info = HostInfo(
        family,
        flags,
        host,
        host_name,
        port,
        protocol,
    )
    
    output = repr(host_info)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    family = AddressFamily.AF_INET
    flags = 3
    host = '1.1.1.1'
    host_name = 'orin'
    port = 96
    protocol = 123
    
    keyword_parameters = {
        'family': family,
        'flags': flags,
        'host': host,
        'host_name': host_name,
        'port': port,
        'protocol': protocol,
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
            'family': AddressFamily.AF_INET6,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'flags': 4,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'host': '1.1.1.2',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'host_name': 'okuu',
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'port': 97,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'protocol': 124,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__HostInfo__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``HostInfo.__eq__`` works as intended.
    
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
    host_info_0 = HostInfo(**keyword_parameters_0)
    host_info_1 = HostInfo(**keyword_parameters_1)
    
    output = host_info_0 == host_info_1
    vampytest.assert_instance(output, bool)
    return output


def test__HostInfo__hash():
    """
    Tests whether ``HostInfo.__hash__`` works as intended.
    """
    family = AddressFamily.AF_INET
    flags = 3
    host = '1.1.1.1'
    host_name = 'orin'
    port = 96
    protocol = 123
    
    host_info = HostInfo(
        family,
        flags,
        host,
        host_name,
        port,
        protocol,
    )
    
    output = hash(host_info)
    vampytest.assert_instance(output, int)
