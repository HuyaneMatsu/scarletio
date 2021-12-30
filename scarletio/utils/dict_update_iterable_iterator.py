__all__ = ()

def _dict_update_iterable_iterator(iterable):
    """
    Iterates over the elements of the given `iterable`. With each loop yields 2 elements, a key-value pair.
    
    This method is an iterable generator.
    
    Parameters
    ----------
    iterable : `iterable`
        An iterable to add it's elements to a list.
    
    Yields
    ------
    item : `tuple` (`object`, `object`)
    
    Raises
    ------
    TypeError
        An element's type is incorrect.
    """
    index = - 1
    for item in iterable:
        index += 1
        
        try:
            iterator = iter(item)
        except TypeError:
            raise TypeError(
                f'Cannot convert dictionary update sequence element #{index} to a sequence; '
                f'got item={item!r}; iterable={iterable!r}.'
            ) from None
        
        try:
            key = next(iterator)
        except StopIteration:
            raise ValueError(
                f'Dictionary update sequence element #{index} has length `0`; 2 is required; '
                f'got item={item!r}; iterable={iterable!r}.'
            ) from None
        
        try:
            value = next(iterator)
        except StopIteration:
            raise ValueError(
                f'Dictionary update sequence element #{index} has length `1`; 2 is required; '
                f'got item={item!r}; iterable={iterable!r}.'
            ) from None
        
        try:
            next(iterator)
        except StopIteration:
            pass
        else:
            length = 3
            for _ in iterator:
                length += 1
                if length > 9000:
                    break
            
            if length > 9000:
                length = 'OVER 9000!'
            else:
                length = repr(length)
            
            raise ValueError(
                f'Dictionary update sequence element #{index} has length {length}; 2 is required; '
                f'got item={item!r}; iterable={iterable!r}.'
            )
        
        yield key, value
