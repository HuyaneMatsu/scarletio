__all__ = ('WebSocketFrame', )

from warnings import warn

from ..utils import RichAttributeErrorBaseType

from .exceptions import WebSocketProtocolError


WEB_SOCKET_OPERATION_CONTINUOUS = 0
WEB_SOCKET_OPERATION_TEXT = 1
WEB_SOCKET_OPERATION_BINARY = 2

WEB_SOCKET_OPERATION_CLOSE = 8
WEB_SOCKET_OPERATION_PING = 9
WEB_SOCKET_OPERATION_PONG = 10

WEB_SOCKET_DATA_OPERATIONS = (WEB_SOCKET_OPERATION_CONTINUOUS,  WEB_SOCKET_OPERATION_TEXT, WEB_SOCKET_OPERATION_BINARY)
WEB_SOCKET_CONTROL_OPERATIONS = (WEB_SOCKET_OPERATION_CLOSE, WEB_SOCKET_OPERATION_PING, WEB_SOCKET_OPERATION_PONG)

# TODO: whats the fastest way on pypy ? casting 64 bit ints -> xor -> replace?
# You can do `data = memoryview(data).cast('Q', (size,))` and then index max, but that is still 3 times slower
# I use pypy3.6 tho, so perhaps on newer versions it is faster

_XOR_TABLE = [bytes(a ^ b for a in range(256)) for b in range(256)]


def apply_web_socket_mask(mask, data):
    """
    Applies web socket mask on the given data and returns a new instance.
    
    Parameters
    ----------
    data : `bytes-like`
        Data to apply the mask to.
    mask : `bytes`
        `uint32` web socket mask in bytes.
    """
    data_bytes = bytearray(data)
    for index in range(4):
        data_bytes[index::4] = data_bytes[index::4].translate(_XOR_TABLE[mask[index]])
    return data_bytes


class WebSocketFrame(RichAttributeErrorBaseType):
    """
    Represents a web socket frame.
    
    Attributes
    ----------
    data : `bytes`
        The data of the frame.
    
    head_0 : `int`
        The first byte of the web socket frame.
    """
    __slots__ = ('data', 'head_0')
    
    def __new__(cls, final, operation_code, data):
        """
        Creates a web socket frame.
        
        Parameters
        -----------
        final : `bool`
            Whether this web socket frame is a final web socket frame.
            When sending web socket frames, the data of frames it collected, till a final frame is received.
        
        operation_code : `int`
            The operation code of the web socket frame.
            
            Can be any of the following:
            
            +-----------------------------------+-------+
            | Respective name                   | Value |
            +===================================+=======+
            | WEB_SOCKET_OPERATION_CONTINUOUS   | 0     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_TEXT         | 1     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_BINARY       | 2     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_CLOSE        | 8     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_PING         | 9     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_PONG         | 10    |
            +-----------------------------------+-------+
        
        data : `bytes`
            The data to ship with the web socket frame.
        """
        self = object.__new__(cls)
        self.data = data
        self.head_0 = (final << 7) | operation_code
        return self
    
    
    def __eq__(self, other):
        """Returns whether the two websocket frames are equal."""
        if type(self) is not type(self):
            return NotImplemented
        
        if self.head_0 != other.head_0:
            return False
        
        if self.data != other.data:
            return False
        
        return True
    
    
    def __repr__(self):
        """Returns the websocket frame's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # final
        repr_parts.append(' final = ')
        repr_parts.append(repr(self.final))
        
        repr_parts.append(', operation_code = ')
        repr_parts.append(repr(self.operation_code))
        
        repr_parts.append(', data (length) = ')
        repr_parts.append(repr(len(self.data)))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
        
    
    @property
    def final(self):
        """
        Returns whether the web socket frame is final.
        
        Returns
        -------
        is_final : `bool`
        """
        return True if (self.head_0 & 0b10000000) else False
    
    
    @property
    def rsv1(self):
        """
        Returns the first reserved bit of the web socket frame's head.
        
        Returns
        -------
        rsv1 : `int`
        """
        warn(
            f'`{type(self).__name__}.rsv1` is deprecated and will be removed in 2025 October.',
            FutureWarning,
            stacklevel = 2,
        )
        
        return True if (self.head_0 & 0b01000000) else False
    
    
    @property
    def rsv2(self):
        """
        Returns the second reserved bit of the web socket frame's head.
        
        Returns
        -------
        rsv2 : `int`
        """
        warn(
            f'`{type(self).__name__}.rsv2` is deprecated and will be removed in 2025 October.',
            FutureWarning,
            stacklevel = 2,
        )
        
        return True if (self.head_0 & 0b00100000) else False
    
    
    @property
    def rsv3(self):
        """
        Returns the third reserved bit of the web socket frame's head.
        
        Returns
        -------
        rsv3 : `int`
        """
        warn(
            f'`{type(self).__name__}.rsv3` is deprecated and will be removed in 2025 October.',
            FutureWarning,
            stacklevel = 2,
        )
        
        return True if (self.head_0 & 0b00010000) else False
    
    
    @property
    def operation_code(self):
        """
        Returns the web socket frame's operation_code.
        
        Returns
        -------
        operation_code : `int`
            Can be one of the following values:
            
            +-----------------------------------+-------+
            | Respective name                   | Value |
            +===================================+=======+
            | WEB_SOCKET_OPERATION_CONTINUOUS   | 0     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_TEXT         | 1     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_BINARY       | 2     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_CLOSE        | 8     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_PING         | 9     |
            +-----------------------------------+-------+
            | WEB_SOCKET_OPERATION_PONG         | 10    |
            +-----------------------------------+-------+
        """
        return self.head_0 & 0b00001111
    
    
    def check(self):
        """
        Check that this frame contains acceptable values.
        
        Raises
        ------
        WebSocketProtocolError
            - If the reserved bits are not `0`.
            - If the frame is a control frame, but is too long for one.
            - If the web socket frame is fragmented frame. (Might be supported if people request is.)
            - If the frame operation_code is not any of the expected ones.
        """
        if self.head_0 & 0b01110000:
            raise WebSocketProtocolError('Reserved bits must be `0`.')
        
        operation_code = self.head_0 & 0b00001111
        if operation_code in WEB_SOCKET_DATA_OPERATIONS:
            return
        
        if operation_code in WEB_SOCKET_CONTROL_OPERATIONS:
            if len(self.data) > 125:
                raise WebSocketProtocolError('Control frame too long.')
            if not self.head_0 & 0b10000000:
                raise WebSocketProtocolError('Fragmented control frame.')
            return
        
        raise WebSocketProtocolError(f'Invalid operation_code: {operation_code}.')
    
    
    @classmethod
    def _from_fields(cls, head_0, data):
        """
        Creates a new web socket frame instance.
        
        Parameters
        ----------
        head_0 : `int`
            The 0th byte of web socket frame. It holds all the required data.
        
        data : `bytes`
            The data of the frame.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.head_0 = head_0
        self.data = data
        return self
    
    
    @property
    def head_1(self):
        """
        Deprecated and will be removed in 2025 october.
        """
        warn(
            (
                f'`{type(self).__name__}.head_1` is deprecated and will be removed in 2025 October. '
                f'Please use `.head_0` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        
        return self.head_0
    
    
    @property
    def is_final(self):
        """
        Deprecated and will be removed in 2025 october.
        """
        warn(
            (
                f'`{type(self).__name__}.is_final` is deprecated and will be removed in 2025 October. '
                f'Please use `.final` instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        
        return self.final
