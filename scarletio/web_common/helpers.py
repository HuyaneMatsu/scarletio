__all__ = ('HttpVersion', 'HttpVersion10', 'HttpVersion11', 'freeze_headers',)

from re import I as re_ignore_case, compile as re_compile
import socket as module_socket
from collections import namedtuple

from ..core import CancelledError, Task
from ..utils import IgnoreCaseMultiValueDictionary, include

from .exceptions import PayloadError


RawRequestMessage = include('RawRequestMessage')
RawResponseMessage = include('RawResponseMessage')


HttpVersion = namedtuple('HttpVersion', ('major', 'minor'))
HttpVersion10 = HttpVersion(1, 0)
HttpVersion11 = HttpVersion(1, 1)


BASIC_AUTH_DEFAULT_ENCODING = 'latin1'


_ipv4_pattern = '^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
_ipv6_pattern = (
    '^(?:(?:(?:[A-F0-9]{1,4}:){6}|(?=(?:[A-F0-9]{0,4}:){0,6}'
    '(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$)(([0-9A-F]{1,4}:){0,5}|:)'
    '((:[0-9A-F]{1,4}){1,5}:|:)|::(?:[A-F0-9]{1,4}:){5})'
    '(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\\.){3}'
    '(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])|(?:[A-F0-9]{1,4}:){7}'
    '[A-F0-9]{1,4}|(?=(?:[A-F0-9]{0,4}:){0,7}[A-F0-9]{0,4}$)'
    '(([0-9A-F]{1,4}:){1,7}|:)((:[0-9A-F]{1,4}){1,7}|:)|(?:[A-F0-9]{1,4}:){7}'
    ':|:(:[A-F0-9]{1,4}){7})$'
)

_ipv4_regex = re_compile(_ipv4_pattern)
_ipv6_regex = re_compile(_ipv6_pattern, flags = re_ignore_case)
_ipv4_regex_b = re_compile(_ipv4_pattern.encode('utf-8'))
_ipv6_regex_b = re_compile(_ipv6_pattern.encode('utf-8'), flags = re_ignore_case)

del _ipv4_pattern, _ipv6_pattern


def is_ip_address(host):
    """
    Returns whether the given `host` is an ip address.
    
    Parameters
    ----------
    host : None | str | bytes-like`
        Host value.
    
    Returns
    -------
    is_ip_address : `bool`
    
    Raises
    ------
    TypeError
        - If `host`'s type is invalid.
    """
    if host is None:
        return False
    
    if isinstance(host, str):
        if _ipv4_regex.fullmatch(host) is not None:
            return True
        
        if _ipv6_regex.fullmatch(host) is not None:
            return True
        
        return False
        
    if isinstance(host, (bytes, bytearray, memoryview)):
        if _ipv4_regex_b.fullmatch(host) is not None:
            return True
        
        if _ipv6_regex_b.fullmatch(host) is not None:
            return True
        
        return False
    
    raise TypeError(
        f'`host` can be `None`, `str`, `bytes-like`, got {type(host).__name__}; {host!r}.'
    )


def is_ipv4_address(host):
    """
    Returns whether the given host is an `ipv4` ip address.
    
    Parameters
    ----------
    host : None | str | bytes-like`
        Host value.
    
    Returns
    -------
    is_ipv4_address : `bool`
    
    Raises
    ------
    TypeError
        - If `host`'s type is invalid.
    """
    if host is None:
        return False
    
    if isinstance(host, str):
        if _ipv4_regex.fullmatch(host) is not None:
            return True
        
        return False
    
    if isinstance(host, (bytes, bytearray, memoryview)):
        if _ipv4_regex_b.fullmatch(host) is not None:
            return True
        
        return False
    
    raise TypeError(
        f'`host` can be `None`, `str`, `bytes-like`, got {type(host).__name__}; {host!r}.'
    )


def is_ipv6_address(host):
    """
    Returns whether the given host is an `ipv6` ip address.
    
    Parameters
    ----------
    host : None | str | bytes-like`
        Host value.
    
    Returns
    -------
    is_ipv6_address : `bool`
    
    Raises
    ------
    TypeError
        - If `host`'s type is invalid.
    """
    if host is None:
        return False
    
    if isinstance(host, str):
        if _ipv6_regex.fullmatch(host) is not None:
            return True
        
        return False
    
    if isinstance(host, (bytes, bytearray, memoryview)):
        if _ipv6_regex_b.fullmatch(host) is not None:
            return True
        
        return False
    
    raise TypeError(
        f'`host` can be `None`, `str`, `bytes-like`, got {type(host).__name__}; {host!r}.'
    )


TIMEOUT_STATE_NONE = 0
TIMEOUT_STATE_TIMED_OUT = 1
TIMEOUT_STATE_CANCELLED = 2
TIMEOUT_STATE_EXITED = 3

class Timeout:
    """
    Implements async timeout feature as a context manager.
    
    Attributes
    ----------
    _handle : `None`, ``TimerHandle``
        Timer handle to cancel the respective task when it occurs. After timeout occurs, or the timeouter is
        cancelled, set as `None`.
    _loop : ``EventThread``
        The event loop to what the timeouter is bound to.
    _task : `None`, ``Task``
        The respective task what will be cancelled. Set as `None` at creation and when cancelled or exited.
    _state : `int`
        The timeouter's state.
        
        Can be one of the following:
        +---------------------------+-------+
        | Respective name           | Value |
        +===========================+=======+
        | TIMEOUT_STATE_NONE        | 0     |
        +---------------------------+-------+
        | TIMEOUT_STATE_TIMED_OUT   | 1     |
        +---------------------------+-------+
        | TIMEOUT_STATE_CANCELLED   | 2     |
        +---------------------------+-------+
        | TIMEOUT_STATE_EXITED      | 3     |
        +---------------------------+-------+
    """
    __slots__ = ('_handle', '_loop', '_task', '_state')
    
    def __new__(cls, loop, timeout):
        """
        Creates a new timeouter instance bound to the given loop.
        
        The timeout starts when the timeouter is created.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the timeouter will be bound to.
        timeout : `float`
            Time in seconds after the task is cancelled. When the cancellation reaches the context manager, raises
            `TimeoutError` instead.
        """
        self = object.__new__(cls)
        self._loop = loop
        self._handle = loop.call_after(timeout, cls._timeout, self)
        self._task = None
        self._state = TIMEOUT_STATE_NONE
        return self
    
    
    def cancel(self):
        """
        Cancels the timeouter.
        
        If already cancelled, does nothing.
        """
        if self._state == TIMEOUT_STATE_CANCELLED:
            return
        
        self._state = TIMEOUT_STATE_CANCELLED
        
        handle = self._handle
        if (handle is not None):
            self._handle = None
            handle.cancel()
        
        self._task = None
    
    
    def __enter__(self):
        """
        Enters the timeouter as a context manager.
        
        Returns
        -------
        self : ``Timeout``
        
        Raises
        ------
        RuntimeError
            ``Timeout`` entered outside of a ``Task``.
        TimeoutError
            Timeout already occurred.
        """
        task = self._loop.current_task
        if (task is None):
            raise RuntimeError(
                f'`{type(self).__name__}` entered outside of a `{Task.__name__}`!'
            )
        
        state = self._state
        if state == TIMEOUT_STATE_NONE:
            self._task = task
        elif state == TIMEOUT_STATE_TIMED_OUT:
            raise TimeoutError
        elif state == TIMEOUT_STATE_CANCELLED:
            pass
        else:
            raise RuntimeError(
                f'`{type(self).__name__}` already used.'
            )
        
        return self
    
    
    def _timeout(self):
        """
        Timeouts the timeouter if not yet timed out nor cancelled.
        """
        if self._state != TIMEOUT_STATE_NONE:
            return
        
        self._state = TIMEOUT_STATE_TIMED_OUT
        
        handle = self._handle
        if (handle is not None):
            self._handle = None
        
        task = self._task
        if (task is not None):
            task.cancel()
    
    
    def __exit__(self, exception_type, exception_value, exception_traceback):
        """
        Exits from the timeouter. If the timeout occurs, then raises ``TimeoutError`` from the received cancellation.
        """
        handle = self._handle
        if (handle is not None):
            self._handle = None
            handle.cancel()
        
        self._task = None
        
        state = self._state
        self._state = TIMEOUT_STATE_EXITED
        if (state == TIMEOUT_STATE_TIMED_OUT) and isinstance(exception_type, CancelledError):
            raise TimeoutError from None
        
        return False
    
    
    def __repr__(self):
        """Returns the timeout's representation."""
        return f'<{type(self).__name__}>'


def set_tcp_nodelay(transport, value):
    """
    Sets or removes tcp nodelay socket option to the given transport's socket if applicable.
    
    Parameters
    ----------
    transport : ``AbstractTransportLayerBase``
        Asynchronous transport implementation.
    value : `bool`
        Value to set tcp nodelay to.
    """
    socket = transport.get_extra_info('socket')
    if socket is None:
        return
    
    if socket.family not in (module_socket.AF_INET, module_socket.AF_INET6):
        return
    
    # socket may be closed already, on windows OSError get raised
    try:
        socket.setsockopt(module_socket.IPPROTO_TCP, module_socket.TCP_NODELAY, value)
    except OSError:
        pass


def freeze_headers(headers):
    """
    Creates a frozen version of the given headers.
    
    Parameters
    ----------
    headers : `None | IgnoreCaseMultiValueDictionary`
        Proxy headers.
    
    Returns
    -------
    proxy_headers_frozen : `None | tuple<(str, tuple<str>)>`
    """
    if (headers is not None) and headers:
        return (*((key, tuple(headers.get_all(key, ()))) for key in sorted(headers.keys())),)


HTTP_STATUS_RP = re_compile(b'[ \t]*HTTP/(\\d+)\\.(\\d+)[ \t]+(\\d\\d\\d)(?:[ \t]+(.*?))?[ \t]*(?:\r\n|$)')
HTTP_REQUEST_RP = re_compile(b'[ \t]*([^ \t]+)[ \t]+([^ \t]+)[ \t]+HTTP/(\\d+)\\.(\\d+)[ \t]*(?:\r\n|$)')


def parse_http_response(data):
    """
    Parses http response message.
    
    Parameters
    ----------
    data : `bytes`
        Data to parse from.
    
    Returns
    -------
    response_message : ``RawResponseMessage``
    
    Raises
    ------
    PayloadError
        Invalid data received.
    """
    parsed = HTTP_STATUS_RP.match(data, 0)
    if parsed is None:
        line_end = data.find(b'\r\n')
        if line_end == -1:
            line_end = len(data)
        
        raise PayloadError(f'Invalid status line: {data[0 : line_end]!r}.')
    
    offset = parsed.end()
    major, minor, status, reason = parsed.groups()
    if reason is None:
        pass
    if not reason:
        reason = None
    else:
        reason = reason.decode('utf-8', errors = 'surrogateescape')
    
    headers = parse_http_headers(data, offset)
    return RawResponseMessage(HttpVersion(int(major), int(minor)), int(status), reason, headers)


def parse_http_request(data):
    """
    Parses http request message.
    
    Parameters
    ----------
    data : `bytes`
        Data to parse from.
    
    Returns
    -------
    request_message : ``RawRequestMessage``
    
    Raises
    ------
    PayloadError
        Invalid data received.
    """
    parsed = HTTP_REQUEST_RP.match(data, 0)
    if parsed is None:
        line_end = data.find(b'\r\n')
        if line_end == -1:
            line_end = len(data)
        
        raise PayloadError(f'Invalid request line: {data[0 : line_end]!r}.')
    
    offset = parsed.end()
    method, path, major, minor = parsed.groups()
    method = method.decode('utf-8', 'surrogateescape').upper()
    path = path.decode('utf-8', 'surrogateescape')

    headers = parse_http_headers(data, offset)
    return RawRequestMessage(HttpVersion(int(major), int(minor)), method, path, headers)


def parse_http_headers(data, offset):
    """
    Parses http headers from the given data.
    
    Parameters
    ----------
    data : `bytes`
        Data to parse from.
    
    offset : `int`
        Position to start parsing at.
    
    Returns
    -------
    headers : ``IgnoreCaseMultiValueDictionary``
    
    Raises
    ------
    PayloadError
        Invalid data received.
    """
    headers = IgnoreCaseMultiValueDictionary()
    while True:
        end_index = data.find(b'\r\n', offset)
        if end_index == -1:
            end_index = len(data)
        
        # Found \r\n instantly, we done!
        # The case, when there is nothing inside of the headers.
        if end_index <= offset:
            return headers
        
        # At this case something is in the line, but is it a header?
        middle_index = data.find(b':', offset, end_index)
        if middle_index <= offset:
            raise PayloadError(f'Invalid header line: {data[offset : end_index]!r}.')
        
        name = data[offset : middle_index].lstrip()
        value = data[middle_index + 1 : end_index].strip()
        offset = end_index + 2
            
        name = name.decode('utf-8', 'surrogateescape')
        
        # continuous?
        if (len(data) > offset) and data[offset] in (b'\t'[0], b' '[0]):
            value_continuous = [value]
            while True:
                end_index = data.find(b'\r\n', offset)
                if end_index == -1:
                    end_index = len(data)
                
                # find \r\n
                value_continuous.append(data[offset : end_index].strip())
                # add \r\n shift
                offset = end_index + 2
                
                # continuous again?
                if (len(data) > offset) and data[offset] in (b'\t'[0], b' '[0]):
                    continue
                break
            
            value = b' '.join(value_continuous)
            value_continuous = None
        
        # Store, nice!
        headers[name] = value.decode('utf-8', 'surrogateescape')
