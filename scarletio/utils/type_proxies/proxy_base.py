__all__ = ()

from ..rich_attribute_error import RichAttributeErrorBaseType


class ProxyBase(RichAttributeErrorBaseType):
    """
    Base type for object proxies.
    
    Attributes
    ----------
    _overwrites : `None`, `dict` of (`str`, `object`) items
        Field overwrites.
    _proxied : `object`
        The proxied object.
    """
    __slots__ = ('_overwrites', '_proxied')
    
    def __new__(cls, to_proxy):
        """
        Creates a new proxy object.
        
        Parameters
        ----------
        to_proxy : `instance<cls>`, `object`
            The object to proxy.
        """
        if isinstance(to_proxy, cls):
            return to_proxy._copy_self_deep()
        
        self = object.__new__(cls)
        self._overwrites = None
        self._proxied = to_proxy
        return self
    
    
    def _copy_self_deep(self):
        """
        Copies self with also copying the overwrites.
        
        Returns
        -------
        new : `instance<type<self>>`
        """
        new = object.__new__(type(self))
        overwrites = self._overwrites
        if (overwrites is not None):
            overwrites = overwrites.copy()
        new._overwrites = overwrites
        new._proxied = self._proxied
        return new
    
    
    def _copy_self_clean(self):
        """
        Copies self without copying the overwrites.
        
        Returns
        -------
        new : `instance<type<self>>`
        """
        new = object.__new__(type(self))
        new._overwrites = None
        new._proxied = self._proxied
        return new
    
    
    def _set_overwrite(self, name, value):
        """
        Sets an overwrite for the given name.
        
        Parameters
        ----------
        name : `str`
            Attribute name.
        value : `object`
            Attribute value.
        """
        overwrites = self._overwrites
        if overwrites is None:
            overwrites = {}
            self._overwrites = overwrites
        
        overwrites[name] = value
    
    
    def _get_overwrite(self, name):
        """
        Gets an overwrite for the given name.
        
        Returns
        -------
        name : `str`
            The attribute's name.
        
        Returns
        -------
        found : `bool`
            Whether the field has an overwrite.
        value : `object`
            Field value. Defaults to `None` if not found.
        """
        overwrites = self._overwrites
        if overwrites is None:
            found = False
            value = None
        
        else:
            try:
                value = overwrites[name]
            except KeyError:
                found = False
                value = None
            else:
                found = True
        
        return found, value
    
    
    def _get_value(self, name):
        """
        Gets value for the given name.
        
        Returns
        -------
        name : `str`
            The attribute's name.
        
        Returns
        -------
        value : `object`
            Attribute value.
        """
        found, value = self._get_overwrite(name)
        if not found:
            value = getattr(self._proxied, name)
        
        return value
    
    
    def _del_overwrite(self, name):
        """
        Deletes an overwrite for the given name.
        
        Parameters
        ----------
        name : `str`
            Attribute name.
        """
        overwrites = self._overwrites
        if overwrites is not None:
            try:
                del overwrites[name]
            except KeyError:
                pass
            else:
                if not overwrites:
                    self._overwrites = None
    
    
    def __repr__(self):
        """Returns the proxy's representation."""
        return f'<{type(self).__name__} to {self._proxied!r}>'
    
    
    def __hash__(self):
        return hash(self._proxied)
    
    
    def __eq__(self, other):
        """Returns whether the two proxies are equal."""
        self_value = self._proxied
        
        if isinstance(other, type(self)):
            other_value = other._proxied
        else:
            other_value = other
        
        return self_value.__eq__(other_value)
