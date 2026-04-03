import vampytest

from ..keep_alive_info import KeepAliveInfo
from ..constants import (
    KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT, KEEP_ALIVE_CONNECTION_TIMEOUT_KEY, KEEP_ALIVE_MAX_REQUESTS_DEFAULT,
    KEEP_ALIVE_MAX_REQUESTS_KEY
)


def _assert_fields_set(keep_alive_info):
    """
    Tests whether the given keep-alive info has all of its fields set.
    
    Parameters
    ----------
    keep_alive_info : ``KeepAliveInfo``
        Keep alive info to test.
    """
    vampytest.assert_instance(keep_alive_info, KeepAliveInfo)
    vampytest.assert_instance(keep_alive_info.connection_timeout, float)
    vampytest.assert_instance(keep_alive_info.max_requests, int)


def test__KeepAliveInfo__new():
    """
    Tests whether ``KeepAliveInfo.__new__`` works as intended.
    """
    connection_timeout = 5.0
    max_requests = 1000
    
    keep_alive_info = KeepAliveInfo(connection_timeout, max_requests)
    _assert_fields_set(keep_alive_info)
    vampytest.assert_eq(keep_alive_info.max_requests, max_requests)
    vampytest.assert_eq(keep_alive_info.connection_timeout, connection_timeout)


def test__KeepAliveInfo__repr():
    """
    Tests whether ``KeepAliveInfo.__repr__`` works as intended.
    """
    connection_timeout = 5.0
    max_requests = 1000
    
    keep_alive_info = KeepAliveInfo(connection_timeout, max_requests)
    
    output = repr(keep_alive_info)
    vampytest.assert_instance(output, str)
    
    vampytest.assert_in(f'max_requests = {max_requests!r}', output)
    vampytest.assert_in(f'connection_timeout = {connection_timeout!r}', output)


def test__KeepAliveInfo__hash():
    """
    Tests whether ``KeepAliveInfo.__hash__`` works as intended.
    """
    connection_timeout = 5.0
    max_requests = 1000
    
    keep_alive_info = KeepAliveInfo(connection_timeout, max_requests)
    
    output = hash(keep_alive_info)
    vampytest.assert_instance(output, int)


def _iter_options__eq():
    connection_timeout = 5.0
    max_requests = 1000
    
    keyword_parameters = {
        'connection_timeout': connection_timeout,
        'max_requests': max_requests,
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
            'max_requests': 500,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'connection_timeout': 10.0,
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__KeepAliveInfo__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``KeepAliveInfo.__eq__`` works as intended.
    
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
    keep_alive_info_0 = KeepAliveInfo(**keyword_parameters_0)
    keep_alive_info_1 = KeepAliveInfo(**keyword_parameters_1)

    output = keep_alive_info_0 == keep_alive_info_1
    vampytest.assert_instance(output, bool)
    return output


def test__KeepAliveInfo__create_default():
    """
    Tests whether ``KeepAliveInfo.create_default``
    """
    keep_alive_info = KeepAliveInfo.create_default()
    _assert_fields_set(keep_alive_info)


def _iter_options__from_header_value():
    yield (
        None,
        (
            KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT,
            KEEP_ALIVE_MAX_REQUESTS_DEFAULT,
        ),
    )
    
    yield (
        '',
        (
            KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT,
            KEEP_ALIVE_MAX_REQUESTS_DEFAULT,
        ),
    )
    
    yield (
        f'{KEEP_ALIVE_CONNECTION_TIMEOUT_KEY}=5, {KEEP_ALIVE_MAX_REQUESTS_KEY}=1000',
        (
            5.0,
            1000,
        ),
    )
    
    yield (
        f'{KEEP_ALIVE_MAX_REQUESTS_KEY}=1000, {KEEP_ALIVE_CONNECTION_TIMEOUT_KEY}=5',
        (
            5.0,
            1000,
        ),
    )
    
    yield (
        f'{KEEP_ALIVE_MAX_REQUESTS_KEY}=aya, {KEEP_ALIVE_CONNECTION_TIMEOUT_KEY}=ya',
        (
            KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT,
            KEEP_ALIVE_MAX_REQUESTS_DEFAULT,
        ),
    )
    
    yield (
        f'nyan=13',
        (
            KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT,
            KEEP_ALIVE_MAX_REQUESTS_DEFAULT,
        ),
    )
    
    yield (
        f'{KEEP_ALIVE_CONNECTION_TIMEOUT_KEY}=5',
        (
            5.0,
            KEEP_ALIVE_MAX_REQUESTS_DEFAULT,
        ),
    )
    
    yield (
        f'{KEEP_ALIVE_MAX_REQUESTS_KEY}=1000',
        (
            KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT,
            1000,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options__from_header_value()).returning_last())
def test__KeepAliveInfo__from_header_value(input_value):
    """
    Tests whether ``KeepAliveInfo.from_header_value`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to parse.
    
    Returns
    -------
    output : `(float, int)`
    """
    keep_alive_info = KeepAliveInfo.from_header_value(input_value)
    _assert_fields_set(keep_alive_info)
    
    return (
        keep_alive_info.connection_timeout,
        keep_alive_info.max_requests,
    )


def _iter_options__to_header_value():
    yield (
        KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT,
        KEEP_ALIVE_MAX_REQUESTS_DEFAULT,
        None,
    )
    
    yield (
        5.0,
        KEEP_ALIVE_MAX_REQUESTS_DEFAULT,
        f'{KEEP_ALIVE_CONNECTION_TIMEOUT_KEY}=5',
    )
    
    yield (
        KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT,
        1000,
        f'{KEEP_ALIVE_MAX_REQUESTS_KEY}=1000',
    )
    
    yield (
        5.0,
        1000,
        f'{KEEP_ALIVE_CONNECTION_TIMEOUT_KEY}=5,{KEEP_ALIVE_MAX_REQUESTS_KEY}=1000',
    )


@vampytest._(vampytest.call_from(_iter_options__to_header_value()).returning_last())
def test__KeepAliveInfo__to_header_value(connection_timeout, max_requests):
    """
    Tests whether ``KeepAliveInfo.to_header_value`` works as intended.
    
    Parameters
    ----------
    connection_timeout : `float`
        The connection's timeout.
    
    max_requests : `int`
        The amount of maximal allowed requests.
    
    Returns
    -------
    output : `None | str`
    """
    keep_alive_info = KeepAliveInfo(connection_timeout, max_requests)
    output = keep_alive_info.to_header_value()
    vampytest.assert_instance(output, str, nullable = True)
    return output
