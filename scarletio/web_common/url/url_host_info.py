__all__ = ()

from ...utils import RichAttributeErrorBaseType

from .constants import (
    HOST_FLAG_EXTERNAL_IP_V4, HOST_FLAG_EXTERNAL_IP_V6, HOST_FLAG_EXTERNAL_NAME, HOST_FLAG_LOCAL_IP_V4,
    HOST_FLAG_LOCAL_NAME, HOST_FLAG_UNAMBIGUOUS, HOST_MASK_ANY_EXTERNAL, HOST_MASK_ANY_LOCAL, HOST_MASK_IP_ANY,
    HOST_MASK_IP_V4, HOST_MASK_IP_V6, HOST_MASK_NAME_ANY
)
from .url_host_part import URLHostPart


class URLHostInfo(RichAttributeErrorBaseType):
    """
    Represents the host information of an url.
    
    Attributes
    ----------
    _flags : `int`
        Details about how the host.
    
    _main_domain : `None | URLHostPart`
        The main domain. If the host is is an ip address or local host only this field is set. 
    
    _sub_domain : `None | URLHostPart`
        Sub-domain if any.
    
    _top_level_domain : `None | URLHostPart`
        Top level domain (TLD) if any.
    """
    __slots__ = ('_flags', '_main_domain', '_sub_domain', '_top_level_domain')
    
    
    def __new__(cls):
        """
        Use either ``.create_from_decoded`` or ``.create_from_encoded`` instead.
        
        Raises
        ------
        RuntimeError
        """
        raise RuntimeError(
            'Use either `.create_from_local_ip_v4_decoded`, `.create_from_local_ip_v4_encoded`, '
            '`.create_from_local_name_decoded`, `.create_from_local_name_encoded`, '
            '`.create_from_external_ip_v4_decoded`, `.create_from_external_ip_v4_encoded`, '
            '`.create_from_external_ip_v6_decoded`, `.create_from_external_ip_v6_encoded`, '
            '`.create_from_external_name_decoded` or `.create_from_external_name_encoded` instead.'
        )
    
    
    def __repr__(self):
        """Returns the url path's representation."""
        repr_parts = ['<', type(self).__name__]
        
        # flags
        repr_parts.append(' flags = ')
        repr_parts.append(repr(self._flags))
        
        # main_domain_decoded
        main_domain_decoded = self.main_domain_decoded
        if (main_domain_decoded is not None):
            repr_parts.append(', main_domain_decoded = ')
            repr_parts.append(repr(main_domain_decoded))
        
        # sub_domain_decoded
        sub_domain_decoded = self.sub_domain_decoded
        if (sub_domain_decoded is not None):
            repr_parts.append(', sub_domain_decoded = ')
            repr_parts.append(repr(sub_domain_decoded))
        
        # top_level_domain_decoded
        top_level_domain_decoded = self.top_level_domain_decoded
        if (top_level_domain_decoded is not None):
            repr_parts.append(', top_level_domain_decoded = ')
            repr_parts.append(repr(top_level_domain_decoded))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def __eq__(self, other):
        """Returns whether the two url parts are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        # flags
        if self._flags != other._flags:
            return True
        
        # main_domain
        if self._main_domain != other._main_domain:
            return False
        
        # sub_domain
        if self._sub_domain != other._sub_domain:
            return False
        
        # top_level_domain
        if self._top_level_domain != other._top_level_domain:
            return False
        
        return True
    
    
    @classmethod
    def create_from_local_ip_v4_decoded(cls, local_ip_v4):
        """
        Creates a new url host info from local ip (v4).
        
        Parameters
        ----------
        local_ip_v4 : `None | str`
            Local ip (v4).
        
        Returns
        -------
        self : `instance<cls>`
        """
        return cls._create_from_decoded(HOST_FLAG_LOCAL_IP_V4, local_ip_v4, None, None)
    
    
    @classmethod
    def create_from_local_ip_v4_encoded(cls, local_ip_v4):
        """
        Creates a new url host info from local ip (v4).
        
        Parameters
        ----------
        local_ip_v4 : `None | str`
            Local ip (v4).
        
        Returns
        -------
        self : `instance<cls>`
        """
        return cls._create_from_encoded(HOST_FLAG_LOCAL_IP_V4, local_ip_v4, None, None)
    
    
    @classmethod
    def create_from_local_name_decoded(cls, local_host, unambiguous):
        """
        Creates a new url host info from local (host) name.
        
        Parameters
        ----------
        local_host : `None | str`
            Local host.
        
        unambiguous : `bool`
            Whether the host is unambiguous.
        
        Returns
        -------
        self : `instance<cls>`
        """
        flags = HOST_FLAG_LOCAL_NAME
        
        if unambiguous:
            flags |= HOST_FLAG_UNAMBIGUOUS
        
        return cls._create_from_decoded(flags, local_host, None, None)
    
    
    @classmethod
    def create_from_local_name_encoded(cls, local_host, unambiguous):
        """
        Creates a new url host info from local (host) name.
        
        Parameters
        ----------
        local_host : `None | str`
            Local host.
        
        unambiguous : `bool`
            Whether the host is unambiguous.
        
        Returns
        -------
        self : `instance<cls>`
        """
        flags = HOST_FLAG_LOCAL_NAME
        
        if unambiguous:
            flags |= HOST_FLAG_UNAMBIGUOUS
        
        return cls._create_from_encoded(flags, local_host, None, None)
    
    
    @classmethod
    def create_from_external_ip_v4_decoded(cls, external_ip_v4):
        """
        Creates a new url host info from external ip (v4).
        
        Parameters
        ----------
        external_ip_v4 : `None | str`
            External ip (v4).
        
        Returns
        -------
        self : `instance<cls>`
        """
        return cls._create_from_decoded(HOST_FLAG_EXTERNAL_IP_V4, external_ip_v4, None, None)
    
    
    @classmethod
    def create_from_external_ip_v4_encoded(cls, external_ip_v4):
        """
        Creates a new url host info from external ip (v4).
        
        Parameters
        ----------
        external_ip_v4 : `None | str`
            External ip (v4).
        
        Returns
        -------
        self : `instance<cls>`
        """
        return cls._create_from_encoded(HOST_FLAG_EXTERNAL_IP_V4, external_ip_v4, None, None)
    
    
    @classmethod
    def create_from_external_ip_v6_decoded(cls, external_ip_v6):
        """
        Creates a new url host info from external ip (v6).
        
        Parameters
        ----------
        external_ip_v6 : `None | str`
            External ip (v6).
        
        Returns
        -------
        self : `instance<cls>`
        """
        return cls._create_from_decoded(HOST_FLAG_EXTERNAL_IP_V6, external_ip_v6, None, None)
    
    
    @classmethod
    def create_from_external_ip_v6_encoded(cls, external_ip_v6):
        """
        Creates a new url host info from external ip (v6).
        
        Parameters
        ----------
        external_ip_v6 : `None | str`
            External ip (v6).
        
        Returns
        -------
        self : `instance<cls>`
        """
        return cls._create_from_encoded(HOST_FLAG_EXTERNAL_IP_V6, external_ip_v6, None, None)
    
    
    @classmethod
    def create_from_external_name_decoded(cls, sub_domain, main_domain, top_level_domain, unambiguous):
        """
        Creates a new url host info from external (host) name.
        
        Parameters
        ----------
        sub_domain : `None | str`
            Sub-domain if any.
        
        main_domain : `None | str`
            The main domain.
        
        top_level_domain : `None | str`
            Top level domain (TLD) if any.
        
        unambiguous : `bool`
            Whether the host is unambiguous.
        
        Returns
        -------
        self : `instance<cls>`
        """
        flags = HOST_FLAG_EXTERNAL_NAME
        
        if unambiguous:
            flags |= HOST_FLAG_UNAMBIGUOUS
        
        return cls._create_from_decoded(flags, main_domain, sub_domain, top_level_domain)
    
    
    @classmethod
    def create_from_external_name_encoded(cls, sub_domain, main_domain, top_level_domain, unambiguous):
        """
        Creates a new url host info from external (host) name.
        
        Parameters
        ----------
        sub_domain : `None | str`
            Sub-domain if any.
        
        main_domain : `None | str`
            The main domain.
        
        top_level_domain : `None | str`
            Top level domain (TLD) if any.
        
        unambiguous : `bool`
            Whether the host is unambiguous.
        
        Returns
        -------
        self : `instance<cls>`
        """
        flags = HOST_FLAG_EXTERNAL_NAME
        
        if unambiguous:
            flags |= HOST_FLAG_UNAMBIGUOUS
        
        return cls._create_from_encoded(flags, main_domain, sub_domain, top_level_domain)
    
    
    @classmethod
    def _create_from_decoded(cls, flags, main_domain, sub_domain, top_level_domain):
        """
        Creates a new url host info from decoded values.
        
        Parameters
        ----------
        flags : `int`
            Details about how the host.
        
        main_domain : `None | str`
            The main domain. If the host is is an ip address or local host only this field is set. 
        
        sub_domain : `None | str`
            Sub-domain if any.
        
        top_level_domain : `None | str`
            Top level domain (TLD) if any.
        
        Returns
        -------
        self : `instance<cls>`
        """
        if main_domain is None:
            main_domain = None
        else:
            main_domain = URLHostPart.create_from_decoded(main_domain)
        
        if sub_domain is None:
            sub_domain = None
        else:
            sub_domain = URLHostPart.create_from_decoded(sub_domain)
        
        if top_level_domain is None:
            top_level_domain = None
        else:
            top_level_domain = URLHostPart.create_from_decoded(top_level_domain)
        
        self = object.__new__(cls)
        self._flags = flags
        self._main_domain = main_domain
        self._sub_domain = sub_domain
        self._top_level_domain = top_level_domain
        return self
    
    
    @classmethod
    def _create_from_encoded(cls, flags, main_domain, sub_domain, top_level_domain):
        """
        Creates a new url host info from encoded values.
        
        Parameters
        ----------
        flags : `int`
            Details about how the host.
        
        main_domain : `None | str`
            The main domain. If the host is is an ip address or local host only this field is set. 
        
        sub_domain : `None | str`
            Sub-domain if any.
        
        top_level_domain : `None | str`
            Top level domain (TLD) if any.
        
        Returns
        -------
        self : `instance<cls>`
        """
        if main_domain is None:
            main_domain = None
        else:
            main_domain = URLHostPart.create_from_encoded(main_domain)
        
        if sub_domain is None:
            sub_domain = None
        else:
            sub_domain = URLHostPart.create_from_encoded(sub_domain)
        
        if top_level_domain is None:
            top_level_domain = None
        else:
            top_level_domain = URLHostPart.create_from_encoded(top_level_domain)
        
        self = object.__new__(cls)
        self._flags = flags
        self._main_domain = main_domain
        self._sub_domain = sub_domain
        self._top_level_domain = top_level_domain
        return self
    
    
    @property
    def main_domain_decoded(self):
        """
        Returns the host info's decoded main-domain.
        
        Returns
        -------
        main_domain : `None | str`
        """
        main_domain = self._main_domain
        if (main_domain is not None):
            return main_domain.decoded
    
    
    @property
    def sub_domain_decoded(self):
        """
        Returns the host info's decoded sub-domain.
        
        Returns
        -------
        main_domain : `None | str`
        """
        sub_domain = self._sub_domain
        if (sub_domain is not None):
            return sub_domain.decoded

    
    @property
    def top_level_domain_decoded(self):
        """
        Returns the host info's decoded top-level-domain.
        
        Returns
        -------
        main_domain : `None | str`
        """
        top_level_domain = self._top_level_domain
        if (top_level_domain is not None):
            return top_level_domain.decoded
    
    
    @property
    def main_domain_encoded(self):
        """
        Returns the host info's encoded main-domain.
        
        Returns
        -------
        main_domain : `None | str`
        """
        main_domain = self._main_domain
        if (main_domain is not None):
            return main_domain.encoded
    
    
    @property
    def sub_domain_encoded(self):
        """
        Returns the host info's encoded sub-domain.
        
        Returns
        -------
        main_domain : `None | str`
        """
        sub_domain = self._sub_domain
        if (sub_domain is not None):
            return sub_domain.encoded
    
    
    @property
    def top_level_domain_encoded(self):
        """
        Returns the host info's encoded top-level-domain.
        
        Returns
        -------
        main_domain : `None | str`
        """
        top_level_domain = self._top_level_domain
        if (top_level_domain is not None):
            return top_level_domain.encoded
    
    
    def is_ip_v4(self):
        """
        Returns whether the host is an ip v4 address.
        
        Returns
        -------
        is_ip_v4 : `bool`
        """
        return True if self._flags & HOST_MASK_IP_V4 else False
    
    
    def is_ip_v6(self):
        """
        Returns whether the host is an ip v6 address.
        
        Returns
        -------
        is_ip_v6 : `bool`
        """
        return True if self._flags & HOST_MASK_IP_V6 else False
    
    
    def is_ip(self):
        """
        Returns whether the host is an ip address.
        
        Returns
        -------
        is_ip : `bool`
        """
        return True if self._flags & HOST_MASK_IP_ANY else False

    
    def is_name(self):
        """
        Returns whether the host is a (host) name.
        
        Returns
        -------
        is_name : `bool`
        """
        return True if self._flags & HOST_MASK_NAME_ANY else False
    
    
    def is_local(self):
        """
        Returns whether the host referenced a local address or (host) name.
        
        Returns
        -------
        is_local : `bool`
        """
        return True if self._flags & HOST_MASK_ANY_LOCAL else False
    
    
    def is_external(self):
        """
        Returns whether the host referenced an external address or (host) name.
        
        Returns
        -------
        is_external : `bool`
        """
        return True if self._flags & HOST_MASK_ANY_EXTERNAL else False
    
    
    def is_unambiguous(self):
        """
        Returns whether the host is unambiguous.
        
        Returns
        -------
        is_unambiguous : `bool`
        """
        return True if self._flags & HOST_FLAG_UNAMBIGUOUS else False
