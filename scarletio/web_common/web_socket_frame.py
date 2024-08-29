__all__ = ('WebSocketFrame', )

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


class WebSocketFrame:
    """
    Represents a web socket frame.
    
    Attributes
    ----------
    data : `bytes`
        The data of the frame.
    head_1 : `int`
        The first bytes of web socket frame's, because it holds all the required data needed.
    """
    __slots__ = ('data', 'head_1',)
    
    def __init__(self, is_final, operation_code, data):
        """
        Creates a web socket frame.
        
        Parameters
        -----------
        is_final : `bool`
            Whether this web socket frame is a final web socket frame.
            When sending web socket frames, the data of frames it collected, till a final frame is received.
        operation_code : `int`
            The operation code of the web socket frame.
            
            Can be 1 of the following:
            
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
        self.data = data
        self.head_1 = (is_final << 7) | operation_code
    
    @property
    def is_final(self):
        """
        Returns whether the web socket frame is final.
        
        Returns
        -------
        is_final : `bool`
        """
        return (self.head_1 & 0b10000000) >> 7
    
    
    @property
    def rsv1(self):
        """
        Returns the first reserved bit of the web socket frame's head.
        
        Defaults to `0˙
        
        Returns
        -------
        rsv1 : `int`
        """
        return (self.head_1 & 0b01000000) >> 6
    
    
    @property
    def rsv2(self):
        """
        Returns the second reserved bit of the web socket frame's head.
        
        Defaults to `0˙
        
        Returns
        -------
        rsv2 : `int`
        """
        return (self.head_1 & 0b00100000) >> 5
    
    
    @property
    def rsv3(self):
        """
        Returns the third reserved bit of the web socket frame's head.
        
        Defaults to `0˙
        
        Returns
        -------
        rsv3 : `int`
        """
        return (self.head_1 & 0b00010000) >> 4
    
    
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
        return  self.head_1 & 0b00001111
    
    
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
        if self.head_1 & 0b01110000:
            raise WebSocketProtocolError('Reserved bits must be `0`.')
        
        operation_code = self.head_1 & 0b00001111
        if operation_code in WEB_SOCKET_DATA_OPERATIONS:
            return
        
        if operation_code in WEB_SOCKET_CONTROL_OPERATIONS:
            if len(self.data) > 125:
                raise WebSocketProtocolError('Control frame too long.')
            if not self.head_1 & 0b10000000:
                raise WebSocketProtocolError('Fragmented control frame.')
            return
        
        raise WebSocketProtocolError(f'Invalid operation_code: {operation_code}.')
    
    
    @classmethod
    def _from_fields(cls, data, head_1):
        """
        Creates a new web socket frame instance.
        
        Parameters
        ----------
        data : `bytes`
            The data of the frame.
        head_1 : `int`
            The first bytes of web socket frame's, because it holds all the required data needed.
        
        Returns
        -------
        self : ``WebSocketFrame``
        """
        self = object.__new__(cls)
        self.data = data
        self.head_1 = head_1
        return self
