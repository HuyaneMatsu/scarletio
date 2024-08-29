__all__ = ()

from itertools import islice

from ..core import LOOP_TIME
from ..utils import RichAttributeErrorBaseType

from .constants import HOST_INFO_CACHE_TIMEOUT
from .host_info import HostInfo


class HostInfoBasket(RichAttributeErrorBaseType):
    """
    Holds ``HostInfo`` instances and rotates them.
    
    Attributes
    ----------
    expiration : `int`
        Monotonic time determining when the goods in the basket will expire
    
    host_infos : `tuple<HostInfo>`
        A list of the contained host information.
    
    rotation_start_index : `int`
        An index to determine where the next rotation will start. Used to cycle host infos.
    """
    __slots__ = ('expiration', 'host_infos', 'rotation_start_index')
    
    
    def __new__(cls, host_infos):
        """
        Creates a new host info basket.
        
        Parameters
        ----------
        host_infos : `iterable<HostInfo>`
            Host infos to basket up.
        """
        self = object.__new__(cls)
        self.expiration = LOOP_TIME() + HOST_INFO_CACHE_TIMEOUT
        self.host_infos = tuple(host_infos)
        self.rotation_start_index = 0
        return self
    
    
    @classmethod
    def from_address_infos(cls, host_name, address_infos):
        """
        Creates a new host info basket from the given address infos.
        
        Parameters
        ----------
        host_name : `str`
            The host's name.
        
        address_infos : `list<(AddressFamily, SocketKind, int, str, (str, int) | (str, int, int, int))>`
            Address infos returned by `get_address_info`.
        """
        self = object.__new__(cls)
        self.expiration = LOOP_TIME() + HOST_INFO_CACHE_TIMEOUT
        self.host_infos = (*(HostInfo.from_address_info(host_name, address_info) for address_info in address_infos),)
        self.rotation_start_index = 0
        return self
    
    
    def __repr__(self):
        """Returns the host info basket's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # host_infos <- this is the most valuable field
        repr_parts.append(' host_infos = ')
        repr_parts.append(repr(self.host_infos))
        
        # expiration
        repr_parts.append(', expiration = ')
        repr_parts.append(repr(self.expiration))
        
        # rotation_start_index
        repr_parts.append(', rotation_start_index = ')
        repr_parts.append(repr(self.rotation_start_index))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __mod__(self, other):
        """Returns whether the two host infos are alike."""
        if type(self) is not type(other):
            return NotImplemented
        
        return {*self.host_infos} == {*other.host_infos}
    
    
    def __contains__(self, host_info):
        """Returns whether the basket contains the given host info."""
        return host_info in self.host_infos
    
    
    # Note:
    # Do not add `__eq__` and `__hash__` because it is expected that these object change in haste.
    
    
    def is_expired(self):
        """
        Returns whether the host info basket expired.
        
        Returns
        -------
        expired : `bool`
        """
        return self.expiration < LOOP_TIME()
    
    
    def iter_next_rotation(self):
        """
        Gets the next rotated host infos from the basket.
        
        This function is an iterable generator.
        
        Yields
        ------
        result : `list<HostInfo>`
        """
        host_infos = self.host_infos
        length = len(host_infos)
        
        rotation_start_index = self.rotation_start_index
        
        new_rotation_start_index = rotation_start_index + 1
        if new_rotation_start_index == length:
            new_rotation_start_index = 0
        self.rotation_start_index = new_rotation_start_index
        
        yield from islice(host_infos, rotation_start_index, length)
        yield from islice(host_infos, 0, rotation_start_index)
