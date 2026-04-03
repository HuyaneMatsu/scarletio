import vampytest

from ..constants import IP_TYPE_IP_V4, IP_TYPE_IP_V6
from ..helpers import iter_intermediate_intermediate_addresses_ordered
from ..resolve_configuration import ResolveConfiguration, SortListElement


def _iter_options():
    resolve_configuration = ResolveConfiguration()
    
    yield (
        resolve_configuration,
        [
            (IP_TYPE_IP_V4, 0xffffff12, None, 0),
            (IP_TYPE_IP_V6, 0x12, None, 0),
            (IP_TYPE_IP_V4, 0x12ffff15, None, 0),
        ],
        [
            (IP_TYPE_IP_V4, 0xffffff12, None, 0),
            (IP_TYPE_IP_V6, 0x12, None, 0),
            (IP_TYPE_IP_V4, 0x12ffff15, None, 0),
        ],
    )
    
    resolve_configuration = ResolveConfiguration()
    resolve_configuration.sort_list = (
        SortListElement(
            IP_TYPE_IP_V4,
            0x12ffff00,
            0xffffff00,
        ),
    )
    
    yield (
        resolve_configuration,
        [
            (IP_TYPE_IP_V4, 0xffffff12, None, 0),
            (IP_TYPE_IP_V6, 0x12, None, 0),
            (IP_TYPE_IP_V4, 0x12ffff15, None, 0),
        ],
        [
            (IP_TYPE_IP_V4, 0x12ffff15, None, 0),
            (IP_TYPE_IP_V4, 0xffffff12, None, 0),
            (IP_TYPE_IP_V6, 0x12, None, 0),
        ],
    )
    
    resolve_configuration = ResolveConfiguration()
    resolve_configuration.sort_list = (
        SortListElement(
            IP_TYPE_IP_V4,
            0x12ffff00,
            0xffffff00,
        ),
        SortListElement(
            IP_TYPE_IP_V6,
            0x12,
            0xffffffffffffffffffffffffffffffff,
        ),
    )
    
    yield (
        resolve_configuration,
        [
            (IP_TYPE_IP_V4, 0xffffff12, None, 0),
            (IP_TYPE_IP_V6, 0x12, None, 0),
            (IP_TYPE_IP_V4, 0x12ffff15, None, 0),
        ],
        [
            (IP_TYPE_IP_V4, 0x12ffff15, None, 0),
            (IP_TYPE_IP_V6, 0x12, None, 0),
            (IP_TYPE_IP_V4, 0xffffff12, None, 0),
        ],
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__iter_intermediate_intermediate_addresses_ordered(resolve_configuration, intermediate_addresses):
    """
    Tests whether ``iter_intermediate_intermediate_addresses_ordered`` works as intended.
    
    Parameters
    ----------
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration.
    
    intermediate_addresses : `list<(int, int, None | str, int)>`
        Packed middle step intermediate_addresses.
    
    Returns
    -------
    output : `list<(int, int, None | str, int)>`
    """
    output = [*iter_intermediate_intermediate_addresses_ordered(resolve_configuration, intermediate_addresses)]
    for element in output:
        vampytest.assert_instance(element, tuple)
    return output
