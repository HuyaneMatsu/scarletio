import vampytest

from ..url import _create_host
from ..url_host_info import URLHostInfo


def _iter_options():
    yield (
        ('koishi%20', None, None, None, None, None, None, None, None),
        True,
        URLHostInfo.create_from_local_ip_v4_encoded('koishi%20'),
    )
    yield (
        ('koishi ', None, None, None, None, None, None, None, None),
        False,
        URLHostInfo.create_from_local_ip_v4_decoded('koishi '),
    )
    
    yield (
        (None, 'koishi%20', None, None, None, None, None, None, None),
        True,
        URLHostInfo.create_from_local_name_encoded('koishi%20', False),
    )
    yield (
        (None, 'koishi ', None, None, None, None, None, None, None, None),
        False,
        URLHostInfo.create_from_local_name_decoded('koishi ', False),
    )
    
    yield (
        (None, 'koishi%20', '.', None, None, None, None, None, None),
        True,
        URLHostInfo.create_from_local_name_encoded('koishi%20', True),
    )
    yield (
        (None, 'koishi ', '.', None, None, None, None, None, None, None),
        False,
        URLHostInfo.create_from_local_name_decoded('koishi ', True),
    )
    
    yield (
        (None, None, None, 'koishi%20', None, None, None, None, None),
        True,
        URLHostInfo.create_from_external_ip_v4_encoded('koishi%20'),
    )
    yield (
        (None, None, None, 'koishi ', None, None, None, None, None, None),
        False,
        URLHostInfo.create_from_external_ip_v4_decoded('koishi '),
    )
    
    yield (
        (None, None, None, None, 'koishi%20', None, None, None, None),
        True,
        URLHostInfo.create_from_external_ip_v6_encoded('koishi%20'),
    )
    yield (
        (None, None, None, None, 'koishi ', None, None, None, None),
        False,
        URLHostInfo.create_from_external_ip_v6_decoded('koishi '),
    )
    
    yield (
        (None, None, None, None, None, 'koishi%20', 'satori%20', 'orin%20', None),
        True,
        URLHostInfo.create_from_external_name_encoded('koishi%20', 'satori%20', 'orin%20', False),
    )
    yield (
        (None, None, None, None, None, 'koishi ', 'satori ', 'orin ', None),
        False,
        URLHostInfo.create_from_external_name_decoded('koishi ', 'satori ', 'orin ', False),
    )
    
    yield (
        (None, None, None, None, None, 'koishi%20', 'satori%20', 'orin%20', '.'),
        True,
        URLHostInfo.create_from_external_name_encoded('koishi%20', 'satori%20', 'orin%20', True),
    )
    yield (
        (None, None, None, None, None, 'koishi ', 'satori ', 'orin ', '.'),
        False,
        URLHostInfo.create_from_external_name_decoded('koishi ', 'satori ', 'orin ', True),
    )
    
    yield (
        (None, None, None, None, None, None, None, None, None),
        True,
        None,
    )
    
    yield (
        (None, None, None, None, None, None, None, None, None),
        False,
        None,
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__create_host(input_value, encoded):
    """
    Tests whether ``_create_host`` works as intended.
    
    Parameters
    ----------
    input_value : `(None | str, None | str, None | str, None | str, None | str, None | str)`
        Value to create host from.
    
    encoded : `bool`
        Whether the value is already encoded.
    
    Returns
    -------
    output : `None | URLHostInfo`
    """
    output = _create_host(iter(input_value), encoded)
    vampytest.assert_instance(output, URLHostInfo, nullable = True)
    return output
