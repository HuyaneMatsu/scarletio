__all__ = ()

from ..utils import RichAttributeErrorBaseType

from .constants import (
    KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT, KEEP_ALIVE_CONNECTION_TIMEOUT_KEY, KEEP_ALIVE_HEADER_RP,
    KEEP_ALIVE_MAX_REQUESTS_DEFAULT, KEEP_ALIVE_MAX_REQUESTS_KEY
)


class KeepAliveInfo(RichAttributeErrorBaseType):
    """
    Keep-alive information of a connection.
    
    Attributes
    ----------
    connection_timeout : `float`
        The connection's timeout.
    
    max_requests : `int`
        The amount of maximal allowed requests.
    """
    __slots__ = ('connection_timeout', 'max_requests')
    
    def __new__(cls, connection_timeout, max_requests):
        """
        Creates a new keep-alive info.
        
        Parameters
        ----------
        connection_timeout : `float`
            The connection's timeout.
        
        max_requests : `int`
            The amount of maximal allowed requests.
        """
        self = object.__new__(cls)
        self.connection_timeout = connection_timeout
        self.max_requests = max_requests
        return self
    
    
    def __repr__(self):
        """Returns the keep-alive's representation"""
        repr_parts = ['<', type(self).__name__]
        
        field_added = False
        
        # connection_timeout
        connection_timeout = self.connection_timeout
        if connection_timeout:
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' connection_timeout = ')
            repr_parts.append(repr(connection_timeout))
        
        # max_requests
        max_requests = self.max_requests
        if max_requests != KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT:
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' max_requests = ')
            repr_parts.append(repr(max_requests))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two keep-alives are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # connection_timeout
        if self.connection_timeout != other.connection_timeout:
            return False
        
        if self.max_requests != other.max_requests:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns the keep-alive's hash value."""
        hash_value = 0
        
        # connection_timeout
        connection_timeout = self.connection_timeout
        if connection_timeout != KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT:
            hash_value ^= hash(connection_timeout)
        
        # max_requests
        max_requests = self.max_requests
        if max_requests != KEEP_ALIVE_MAX_REQUESTS_DEFAULT:
            hash_value ^= max_requests << 8
        
        return hash_value
    
    
    @classmethod
    def create_default(cls):
        """
        Creates a default keep-alive information.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.connection_timeout = KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT
        self.max_requests = KEEP_ALIVE_MAX_REQUESTS_DEFAULT
        return self
    
    
    @classmethod
    def from_header_value(cls, header_value):
        """
        Creates a new keep-alive information from the given header value.
        
        Parameters
        ----------
        header_value : `None | str`
            Header value.
        
        Returns
        -------
        self : `instance<cls>`
        """
        connection_timeout = KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT
        max_requests = KEEP_ALIVE_MAX_REQUESTS_DEFAULT
        
        if (header_value is not None):
            for match in KEEP_ALIVE_HEADER_RP.finditer(header_value):
                key, value = match.groups()
                key = key.casefold()
                
                if key == KEEP_ALIVE_CONNECTION_TIMEOUT_KEY:
                    try:
                        connection_timeout = float(value)
                    except ValueError:
                        pass
                    
                    continue
                
                if key == KEEP_ALIVE_MAX_REQUESTS_KEY:
                    try:
                        max_requests = int(value)
                    except ValueError:
                        pass
                    
                    continue
                
                # unknown key, ignore it.
        
        self = object.__new__(cls)
        self.connection_timeout = connection_timeout
        self.max_requests = max_requests
        return self
    
    
    def to_header_value(self):
        """
        Converts the keepa-live information to its header value representation.
        
        Returns
        -------
        header_value : `None | str`
        """
        output_parts = None
        
        # connection_timeout
        connection_timeout = self.connection_timeout
        if connection_timeout != KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT:
            if output_parts is None:
                output_parts = []
            
            output_parts.append(KEEP_ALIVE_CONNECTION_TIMEOUT_KEY)
            output_parts.append('=')
            output_parts.append(format(connection_timeout, '.0f'))
        
        # max_requests
        max_requests = self.max_requests
        if max_requests != KEEP_ALIVE_MAX_REQUESTS_DEFAULT:
            if output_parts is None:
                output_parts = []
            else:
                output_parts.append(',')
            
            output_parts.append(KEEP_ALIVE_MAX_REQUESTS_KEY)
            output_parts.append('=')
            output_parts.append(str(max_requests))
        
        # Build
        if (output_parts is not None):
            return ''.join(output_parts)
