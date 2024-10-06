import vampytest

from ..exceptions import WebSocketProtocolError
from ..web_socket_frame import (
    WEB_SOCKET_OPERATION_BINARY, WEB_SOCKET_OPERATION_CLOSE, WEB_SOCKET_OPERATION_CONTINUOUS, WEB_SOCKET_OPERATION_PING,
    WEB_SOCKET_OPERATION_PONG, WEB_SOCKET_OPERATION_TEXT, WebSocketFrame
)


def _assert_fields_set(web_socket_frame):
    """
    Tests whether the given web socket frame has all of its attributes set.
    
    Parameters
    ----------
    web_socket_frame : ``WebSocketFrame``
        The web socket frame to check.
    """
    vampytest.assert_instance(web_socket_frame, WebSocketFrame)
    vampytest.assert_instance(web_socket_frame.data, bytes)
    vampytest.assert_instance(web_socket_frame.head_0, int)


def test__WebSocketFrame__new():
    """
    Tests whether ``WebSocketFrame.__new__`` works as intended.
    """
    final = True
    operation_code = 10
    data = b'hey mister'
    
    web_socket_frame = WebSocketFrame(final, operation_code, data)
    _assert_fields_set(web_socket_frame)
    
    vampytest.assert_eq(web_socket_frame.final, final)
    vampytest.assert_eq(web_socket_frame.operation_code, operation_code)
    vampytest.assert_eq(web_socket_frame.data, data)


def test__WebSocketFrame__repr():
    """
    Tests whether ``WebSocketFrame.__repr__`` works as intended.
    """
    final = True
    operation_code = WEB_SOCKET_OPERATION_BINARY
    data = b'hey mister'
    
    web_socket_frame = WebSocketFrame(final, operation_code, data)
    
    output = repr(web_socket_frame)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    final = True
    operation_code = WEB_SOCKET_OPERATION_BINARY
    data = b'hey mister'
    
    keyword_parameters = {
        'final': final,
        'operation_code': operation_code,
        'data': data,
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
            'final': False,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'operation_code': 9,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'data': b'hey sister',
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__WebSocketFrame__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``WebSocketFrame.__eq__`` works as intended.
    
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
    web_socket_frame_0 = WebSocketFrame(**keyword_parameters_0)
    web_socket_frame_1 = WebSocketFrame(**keyword_parameters_1)
    
    output = web_socket_frame_0 == web_socket_frame_1
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__final():
    yield 1 << 7, True
    yield 0 << 7, False


@vampytest._(vampytest.call_from(_iter_options__final()).returning_last())
def test__WebSocketFrame__final(head_0):
    """
    Tests whether ``WebSocketFrame.final`` works as intended.
    
    Parameters
    ----------
    head_0 : `int`
        Byte 0 to create web socket frame with.
    
    Returns
    -------
    output : `bool`
    """
    web_socket_frame = WebSocketFrame._from_fields(head_0, b'')
    output = web_socket_frame.final
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__operation_code():
    yield WEB_SOCKET_OPERATION_BINARY, WEB_SOCKET_OPERATION_BINARY
    yield 0, 0


@vampytest._(vampytest.call_from(_iter_options__operation_code()).returning_last())
def test__WebSocketFrame__operation_code(head_0):
    """
    Tests whether ``WebSocketFrame.operation_code`` works as intended.
    
    Parameters
    ----------
    head_0 : `int`
        Byte 0 to create web socket frame with.
    
    Returns
    -------
    output : `int`
    """
    web_socket_frame = WebSocketFrame._from_fields(head_0, b'')
    output = web_socket_frame.operation_code
    vampytest.assert_instance(output, int)
    return output


def _iter_options__check__failing():
    # reserved bits
    yield 1 << 6, b''
    yield 1 << 5, b''
    yield 1 << 4, b''

    # Not allowed for control
    yield WEB_SOCKET_OPERATION_CLOSE | (0 << 7), b''
    
    # big size (control)
    yield WEB_SOCKET_OPERATION_CLOSE, b'a' * 126
    yield WEB_SOCKET_OPERATION_PING, b'a' * 126
    yield WEB_SOCKET_OPERATION_PONG, b'a' * 126
    
    # invalid operation
    yield 12, b''


def _iter_options__check__passing():
    
    # Should be 0 for control operations (so allowed for data)
    yield WEB_SOCKET_OPERATION_CONTINUOUS | (0 << 7), b''
    
    # big size (data)
    yield WEB_SOCKET_OPERATION_CONTINUOUS, b'a' * 126
    yield WEB_SOCKET_OPERATION_TEXT, b'a' * 126
    yield WEB_SOCKET_OPERATION_BINARY, b'a' * 126


@vampytest._(vampytest.call_from(_iter_options__check__failing()).raising(WebSocketProtocolError))
@vampytest._(vampytest.call_from(_iter_options__check__passing()))
def test__WebSocketFrame__check(head_0, data):
    """
    Tests whether ``WebSocketFrame.check`` works as intended.
    
    Parameters
    ----------
    head_0 : `int`
        Byte 0 to create web socket frame with.
    
    data : `bytes`
        Data to create the web socket frame with.
    
    Raising
    -------
    output : `int`
    """
    web_socket_frame = WebSocketFrame._from_fields(head_0, data)
    web_socket_frame.check()


def test__WebSocketFrame__from_fields():
    """
    Tests whether ``WebSocketFrame._from_fields`` works as intended.
    """
    final = True
    operation_code = WEB_SOCKET_OPERATION_BINARY
    data = b'hey mister'
    
    web_socket_frame = WebSocketFrame(final, operation_code, data)
    web_socket_frame = WebSocketFrame._from_fields(web_socket_frame.head_0, web_socket_frame.data)
    _assert_fields_set(web_socket_frame)
    
    vampytest.assert_eq(web_socket_frame.final, final)
    vampytest.assert_eq(web_socket_frame.operation_code, operation_code)
    vampytest.assert_eq(web_socket_frame.data, data)
