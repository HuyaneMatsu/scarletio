from socket import AddressFamily, SocketKind

import vampytest

from ...core import LOOP_TIME

from ..constants import HOST_INFO_CACHE_TIMEOUT
from ..host_info import HostInfo
from ..host_info_basket import HostInfoBasket


def _assert_fields_set(host_info_basket):
    """
    Asserts whether every fields are set of the host info basket
    
    Parameters
    ----------
    host_info_basket : ``HostInfoBasket``
        The host info basket to check.
    """
    vampytest.assert_instance(host_info_basket, HostInfoBasket)
    vampytest.assert_instance(host_info_basket.expiration, float)
    vampytest.assert_instance(host_info_basket.host_infos, tuple)
    vampytest.assert_instance(host_info_basket.rotation_start_index, int)


def test__HostInfoBasket__new():
    """
    Tests whether ``HostInfoBasket.__new__`` works as intended.
    """
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    
    host_info_0 = HostInfo(
        family_0,
        0,
        host_0,
        'orindance.party',
        port_0,
        protocol_0,
    )
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    
    host_info_1 = HostInfo(
        family_1,
        1,
        host_1,
        'orindance.party',
        port_1,
        protocol_1,
    )
    
    host_info_basket = HostInfoBasket(
        [host_info_0, host_info_1],
    )
    _assert_fields_set(host_info_basket)
    
    vampytest.assert_true(host_info_basket.expiration > LOOP_TIME())
    vampytest.assert_eq(
        host_info_basket.host_infos,
        (host_info_0, host_info_1),
    )
    vampytest.assert_eq(host_info_basket.rotation_start_index, 0)


def test__HostInfoBasket__from_address_infos():
    """
    Tests whether ``HostInfoBasket.from_address_infos`` works as intended.
    """
    host_name = 'orin'
    
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    address_info_0 = (family_0, SocketKind.SOCK_STREAM, protocol_0, '', (host_0, port_0))
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    address_info_1 = (family_1, SocketKind.SOCK_STREAM, protocol_1, '', (host_1, port_1))
    
    host_info_basket = HostInfoBasket.from_address_infos(
        host_name,
        [address_info_0, address_info_1],
    )
    _assert_fields_set(host_info_basket)
    
    vampytest.assert_true(host_info_basket.expiration > LOOP_TIME())
    vampytest.assert_eq(
        host_info_basket.host_infos,
        (HostInfo.from_address_info(host_name, address_info_0), HostInfo.from_address_info(host_name, address_info_1),),
    )
    vampytest.assert_eq(host_info_basket.rotation_start_index, 0)


def test__HostInfoBasket__repr():
    """
    Tests whether ``HostInfoBasket.__repr__`` works as intended.
    """
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    
    host_info_0 = HostInfo(
        family_0,
        0,
        host_0,
        'orindance.party',
        port_0,
        protocol_0,
    )
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    
    host_info_1 = HostInfo(
        family_1,
        1,
        host_1,
        'orindance.party',
        port_1,
        protocol_1,
    )
    
    host_info_basket = HostInfoBasket(
        [host_info_0, host_info_1],
    )
    
    output = repr(host_info_basket)
    vampytest.assert_instance(output, str)


def test__HostInfoBasket__is_expired():
    """
    Tests whether ``HostInfoBasket.is_expired`` works as intended.
    """
    host_name = 'orin'
    
    host_info_basket = HostInfoBasket.from_address_infos(host_name, [])
    
    output = host_info_basket.is_expired()
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
    
    mocked = vampytest.mock_globals(
        type(host_info_basket).is_expired,
        LOOP_TIME = (lambda : LOOP_TIME() + HOST_INFO_CACHE_TIMEOUT + 1.0),
    )
    output = mocked(host_info_basket)
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__HostInfo__iter_next_rotation():
    """
    Tests whether ``HostInfoBasket.iter_next_rotation`` works as intended.
    """
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    host_info_0 = HostInfo(
        family_0,
        0,
        host_0,
        'orindance.party',
        port_0,
        protocol_0,
    )
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    
    host_info_1 = HostInfo(
        family_1,
        1,
        host_1,
        'orindance.party',
        port_1,
        protocol_1,
    )
    
    family_2 = AddressFamily.AF_CAN
    host_2 = '2.2.2.2'
    port_2 = 98
    protocol_2 = 225
    
    host_info_2 = HostInfo(
        family_2,
        2,
        host_2,
        'orindance.party',
        port_2,
        protocol_2,
    )
    
    host_info_basket = HostInfoBasket(
        [host_info_0, host_info_1, host_info_2],
    )
    
    vampytest.assert_eq([*host_info_basket.iter_next_rotation()], [host_info_0, host_info_1, host_info_2])
    vampytest.assert_eq([*host_info_basket.iter_next_rotation()], [host_info_1, host_info_2, host_info_0])
    vampytest.assert_eq([*host_info_basket.iter_next_rotation()], [host_info_2, host_info_0, host_info_1])
    vampytest.assert_eq([*host_info_basket.iter_next_rotation()], [host_info_0, host_info_1, host_info_2])


def _iter_options__mod():
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    host_info_0 = HostInfo(
        family_0,
        0,
        host_0,
        'orindance.party',
        port_0,
        protocol_0,
    )
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    
    host_info_1 = HostInfo(
        family_1,
        1,
        host_1,
        'orindance.party',
        port_1,
        protocol_1,
    )
    
    yield [host_info_0, host_info_1], [host_info_0, host_info_1], True
    yield [host_info_0, host_info_1], [host_info_0], False
    yield [host_info_0, host_info_1], [host_info_1], False
    yield [host_info_0, host_info_1], [], False


@vampytest._(vampytest.call_from(_iter_options__mod()).returning_last())
def test__HostInfoBasket__mod(host_infos_0, host_infos_1):
    """
    Tests whether ``HostInfoBasket.__mod__`` works as intended.
    
    Parameters
    ----------
    host_infos_0 : `list<HostInfo>`
        Host infos to create instance with.
    host_infos_1 : `list<HostInfo>`
        Host infos to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    host_info_basket_0 = HostInfoBasket(host_infos_0)
    host_info_basket_1 = HostInfoBasket(host_infos_1)
    
    output = host_info_basket_0 % host_info_basket_1
    vampytest.assert_instance(output, bool)
    
    return output


def _iter_options__contains():
    family_0 = AddressFamily.AF_INET
    host_0 = '1.1.1.1'
    port_0 = 96
    protocol_0 = 123
    host_info_0 = HostInfo(
        family_0,
        0,
        host_0,
        'orindance.party',
        port_0,
        protocol_0,
    )
    
    family_1 = AddressFamily.AF_INET6
    host_1 = '1.1.1.2'
    port_1 = 97
    protocol_1 = 124
    
    host_info_1 = HostInfo(
        family_1,
        1,
        host_1,
        'orindance.party',
        port_1,
        protocol_1,
    )
    
    yield [host_info_0, host_info_1], host_info_0, True
    yield [host_info_0, host_info_1], host_info_1, True
    yield [host_info_0], host_info_1, False


@vampytest._(vampytest.call_from(_iter_options__contains()).returning_last())
def test__HostInfoBasket__contains(host_infos_0, host_info):
    """
    Tests whether ``HostInfoBasket.__contains__`` works as intended.
    
    Parameters
    ----------
    host_infos_0 : `list<HostInfo>`
        Host infos to create instance with.
    host_info : ``HostInfo``
        Host info to test with.
    
    Returns
    -------
    output : `bool`
    """
    host_info_basket = HostInfoBasket(host_infos_0)
    
    output = host_info in host_info_basket
    vampytest.assert_instance(output, bool)
    
    return output
