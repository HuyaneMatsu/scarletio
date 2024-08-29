__all__ = ()

from socket import AI_NUMERICHOST as ADDRESS_INFO_NUMERIC_HOST

from ..utils import RichAttributeErrorBaseType


class HostInfo(RichAttributeErrorBaseType):
    """
    Resolved information about a host.
    
    Attributes
    ----------
    family : `AddressFamily`
        Address family.
    
    flags : `int`
        Bit-mask for `get_address_info`.
    
    host : `str`
        The host's ip address.
    
    host_name : `str`
        The hosts' name.
    
    port : `int`
        Port to connect to the host.
    
    protocol : `int`
        Protocol type.
    """
    __slots__ = ('family', 'flags', 'host', 'host_name', 'port', 'protocol')
    
    def __new__(cls, family, flags, host, host_name, port, protocol):
        """
        Creates a new host info.
        
        Parameters
        ----------
        family : `AddressFamily`
            Address family.
        
        flags : `int`
            Bit-mask for `get_address_info`.
        
        host : `str`
            The host's ip address.
        
        host_name : `str`
            The hosts' name.
        
        port : `int`
            Port to connect to the host.
        
        protocol : `int`
            Protocol type.
        """
        self = object.__new__(cls)
        self.family = family
        self.flags = flags
        self.host = host
        self.host_name = host_name
        self.port = port
        self.protocol = protocol
        return self
    
    
    @classmethod
    def from_ip(cls, host, port, family):
        """
        Creates a host info instance from the given parameters.
        Used when `host` is an ip address.
        
        Parameters
        ----------
        host : `str`
            The host's ip address.
        port : `int`
            Port to connect to the host.
        family : `AddressFamily`
            Address family.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.family = family
        self.flags = 0
        self.host = host
        self.host_name = host
        self.port = port
        self.protocol = 0
        return self
    
    
    @classmethod
    def from_address_info(cls, host_name, address_info):
        """
        Creates a host info instance from the given parameters.
        
        Parameters
        ----------
        host_name : `str`
            The host's name.
        
        address_info : `(AddressFamily, SocketKind, int, str, (str, int) | (str, int, int, int))`
            An address info returned by `get_address_info`.
        
        Returns
        -------
        self : `instance<cls>`
        """
        address = address_info[4]
        
        # Construct
        self = object.__new__(cls)
        self.family = address_info[0]
        self.flags = ADDRESS_INFO_NUMERIC_HOST
        self.host = address[0]
        self.host_name = host_name
        self.port = address[1]
        self.protocol = address_info[2]
        
        return self
    
    
    def __repr__(self):
        """Returns the host info's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # family
        family = self.family
        if family:
            repr_parts.append(' family = ')
            repr_parts.append(repr(family))
            
            field_added = True
        else:
            field_added = False
        
        # flags
        flags = self.flags
        if flags:
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' flags = ')
            repr_parts.append(repr(flags))
        
        # host
        if field_added:
            repr_parts.append(',')
        
        host = self.host
        repr_parts.append(' host = ')
        repr_parts.append(repr(host))
        
        # host_name
        host_name = self.host_name
        if (host != host_name):
            repr_parts.append(', host_name = ')
            repr_parts.append(repr(host_name))
        
        # port
        repr_parts.append(', port = ')
        repr_parts.append(repr(self.port))
        
        # protocol
        protocol = self.protocol
        if protocol:
            repr_parts.append(', protocol = ')
            repr_parts.append(repr(protocol))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two host info's are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # family
        if self.family != other.family:
            return False
        
        # flags
        if self.flags != other.flags:
            return False
        
        # host
        if self.host != other.host:
            return False
        
        # host_name
        if self.host_name != other.host_name:
            return False
        
        # port
        if self.port != other.port:
            return False
        
        # protocol
        if self.protocol != other.protocol:
            return False
        
        return True
    
    
    def __hash__(self):
        """Returns the host info's hash value."""
        hash_value = 0
        
        # family
        hash_value ^= hash(self.family)
        
        # flags
        hash_value ^= hash(self.flags)
        
        # host
        host = self.host
        hash_value ^= hash(host)
        
        # host_name
        host_name = self.host_name
        if (host != host_name):        
            hash_value ^= hash(host_name)
        
        # port
        hash_value ^= self.port << 17
        
        # protocol
        hash_value ^= hash(self.protocol)
        
        return hash_value
