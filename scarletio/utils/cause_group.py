__all__ = ('CauseGroup',)



def _iter_validate_causes(causes):
    """
    Validates the given causes.
    
    Parameters
    ----------
    causes : `tuple` of (`BaseException`, `type<BaseException>`)
        Exception causes.
    
    Raises
    ------
    TypeError
        If a cause is not `BaseException` instance.
    """
    for cause in causes:
        if isinstance(cause, BaseException):
            yield cause
            continue
        
        if isinstance(cause, type) and issubclass(cause, BaseException):
            yield cause()
            continue
        
        raise TypeError(
            f'Causes can be `{BaseException.__name__}`, got {cause.__class__.__name__}; {cause!r}.'
        )


class CauseGroup(BaseException):
    """
    Allows an exception to have multiple causes.
    
    Example
    -------
    ```py3
    raise Exception from CauseGroup(...)
    ```
    
    Attributes
    ----------
    causes : `tuple` of ``BaseException``
        Exception causes.
    """
    __slots__ = ('causes',)
    
    def __new__(cls, *causes):
        """
        Stops ``CauseGroup`` to be created if a cause is not `BaseException` instance.
        
        Parameters
        ----------
        *causes : `BaseException`, `type<BaseException>`
            Exception causes.
        
        Raises
        ------
        TypeError
            If a cause is not `BaseException` instance.
        
        Returns
        -------
        case : `None`, `BaseException`, `CauseGroup`
            Only returns a cause group if there are at least 2 exceptions to group.
        """
        cause_count = len(causes)
        
        if cause_count == 0:
            return None
        
        if cause_count == 1:
            return causes[0]
        
        causes = tuple(_iter_validate_causes(causes))
        
        self = BaseException.__new__(cls)
        self.causes = causes
        return self
    
    
    __init__ = object.__init__
    
    
    def __iter__(self):
        """
        Iterates over the causes of the cause group.
        
        This method is an iterable generator.
        
        Yields
        ------
        cause : `BaseException`
        """
        yield from self.causes
    
    
    def __len__(self):
        """
        Returns how much exception the cause group contains.
        
        Returns
        -------
        length : `int`
        """
        return len(self.causes)
    
    
    def __eq__(self, other):
        """Returns whether the two cause groups are equal."""
        if type(self) is not type(other):
            return NotImplemented
        
        return self.causes == other.causes
    
    
    def __repr__(self):
        """Returns the cause groups representation."""
        repr_parts = [type(self).__name__, '(']
        
        causes = self.causes
        limit = len(causes)
        if limit:
            index = 0
            
            while True:
                cause = causes[index]
                repr_parts.append(repr(cause))
                
                index += 1
                if index == limit:
                    break
                
                repr_parts.append(', ')
                continue
        
        repr_parts.append(')')
        return ''.join(repr_parts)
    
    
    __str__ = __repr__
