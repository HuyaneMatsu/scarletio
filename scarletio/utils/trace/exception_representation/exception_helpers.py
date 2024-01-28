__all__ = ()


def is_exception(exception):
    """
    Returns whether the given value is an exception.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to check.
    
    Returns
    -------
    is_exception : `bool`
    """
    return issubclass(type(exception), BaseException)
