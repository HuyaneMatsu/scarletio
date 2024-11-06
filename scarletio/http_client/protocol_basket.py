__all__ = ()

from ..utils import RichAttributeErrorBaseType


class ProtocolBasket(RichAttributeErrorBaseType):
    """
    Basket to hold protocols with details about them.
    
    Attributes
    ----------
    available : `None | list<(AbstractProtocolBase, float, int)>`
        Available protocols.
    
    connection_key : ``ConnectionKey``
        Key representing the connection.
    
    used : `None | set<AbstractProtocolBase>`
        The protocols in use.
    """
    __slots__ = ('available', 'connection_key', 'used')
    
    
    def __new__(cls, connection_key):
        """
        Creates a new protocol basket.
        
        Parameters
        ----------
        connection_key : ``ConnectionKey``
            Key representing the connection.
        """
        self = object.__new__(cls)
        self.available = None
        self.connection_key = connection_key
        self.used = None
        return self
    
    
    def __repr__(self):
        """Returns the protocol basket's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # connection_key
        repr_parts.append(' connection_key = ')
        repr_parts.append(repr(self.connection_key))
        
        # available
        available = self.available
        if (available is not None):
            repr_parts.append(', available = ')
            repr_parts.append(repr(available))
        
        # used
        used = self.used
        if (used is not None):
            repr_parts.append(' used = ')
            repr_parts.append(repr(used))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two protocol baskets are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # available
        if self.available != other.available:
            return False
        
        # connection_key
        if self.connection_key != other.connection_key:
            return False
        
        # used
        if self.used != other.used:
            return False
        
        return True
    
    
    def __bool__(self):
        """Returns whether the protocol basket stores any protocols."""
        return (self.available is not None) or (self.used is not None)
    
    
    def clean_up_expired_protocols(self, now):
        """
        Cleans up the protocols that are expired.
        
        Parameters
        ----------
        now : `bool`
            The current monotonic time.
        """
        available = self.available
        if available is None:
            return
        
        for index in reversed(range(len(available))):
            protocol, expiration, performed_requests = available[index]
            if expiration > now:
                continue
            
            del available[index]
            
            transport = protocol.get_transport()
            if self.connection_key.secure and (transport is not None):
                transport.abort()
        
        if not available:
            self.available = None
    
    
    def close(self):
        """
        Closes all the protocols in the basket.
        """
        available = self.available
        if (available is not None):
            self.available = None
            for protocol, expiration, performed_requests in available:
                protocol.close()
            
        used = self.used
        if (used is not None):
            self.used = None
            for protocol in used:
                protocol.close()
    
    
    def pop_available_protocol(self, now):
        """
        Pops an available protocol.
        
        Parameters
        ----------
        now : `float`
            The current monotonic time.
        
        Returns
        -------
        protocol : `None | AbstractProtocolBase`
            Available protocol.
        
        performed_requests : `int`
            The amount of performed requests on the protocol.
        """
        available = self.available
        if available is None:
            return None, 0
        
        while available:
            protocol, expiration, performed_requests = available.pop()
            
            if (protocol.get_transport() is None):
                continue
            
            if now > expiration:
                transport = protocol.get_transport()
                protocol.close()
                if self.connection_key.secure and (transport is not None):
                    transport.abort()
                continue
            
            break
        
        else:
            protocol = None
            performed_requests = 0
        
        if not available:
            self.available = None
        
        return protocol, performed_requests
    
    
    def add_used_protocol(self, protocol):
        """
        Adds a used protocol to the basket.
        
        Parameters
        ----------
        protocol : ``AbstractProtocolBase``
            The protocol to remove.
        """
        used = self.used
        if used is None:
            used = set()
            self.used = used
        
        used.add(protocol)
    
    
    def remove_used_protocol(self, protocol):
        """
        Removes a used protocol.
        
        Parameters
        ----------
        protocol : ``AbstractProtocolBase``
            The protocol to remove.
        """
        used = self.used
        if used is None:
            return
        
        try:
            used.discard(protocol)
        except KeyError:
            pass
        
        if not used:
            self.used = None
    
    
    def add_available_protocol(self, protocol, now, keep_alive_timeout, performed_requests):
        """
        Adds an available protocol to the basket.
        
        Parameters
        ----------
        protocol : ``AbstractProtocolBase`
            The protocol to add.
        
        now : `float`
            The current monotonic time.
        
        keep_alive_timeout : `float`
            How long the connection can be reused.
        
        performed_requests : `int`
            The amount of performed requests on the connection.
        """
        available = self.available
        if available is None:
            available = []
            self.available = available
        
        available.append((protocol, now + keep_alive_timeout, performed_requests))
    
    
    def get_closest_expiration(self):
        """
        Returns the closest expiration of the protocol basket.
        
        Returns
        -------
        closest_expiration : `float`
            Returns `-1` on failure.
        """
        available = self.available
        if available is None:
            return -1.0
        
        return min(expiration for (protocol, expiration, performed_requests) in available)
