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
    
    
    # What the hell is wrong with `str()` ?
    __str__ = BaseException.__repr__
    
    
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
