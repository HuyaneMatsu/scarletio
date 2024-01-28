__all__ = ('AttributeError', 'RichAttributeErrorBaseType',)


ATTRIBUTE_ERROR_HAS_RICH_SLOTS = hasattr(AttributeError, 'obj') and hasattr(AttributeError, 'name')


class AttributeError(AttributeError):
    """
    Represents a rich attribute error.
    
    Parameters
    ----------
    attribute_name : `str`
        The attribute's name that was not found.
    instance : `object`
        The instance that does not have the respective attribute.
    """
    if ATTRIBUTE_ERROR_HAS_RICH_SLOTS:
        __slots__ = ()
        
        attribute_name = AttributeError.name
        instance = AttributeError.obj
    else:
        __slots__ = ('attribute_name', 'instance')
    
    def __new__(cls, instance, attribute_name):
        self = Exception.__new__(cls, instance, attribute_name)
        self.instance = instance
        self.attribute_name = attribute_name
        return self
    
    __init__ = object.__init__
    
    
    def __repr__(self):
        """Returns the attribute error's representations."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' instance = ')
        repr_parts.append(repr(self.instance))
        
        repr_parts.append(', attribute_name = ')
        repr_parts.append(repr(self.attribute_name))
        
        repr_parts.append('>')
        return ''.join(repr_parts)


class RichAttributeErrorBaseType:
    """
    Base type for generating rich attribute error messages.
    """
    __slots__ = ()
    
    def __getattr__(self, attribute_name):
        """Drops a rich attribute error."""
        raise AttributeError(self, attribute_name)
