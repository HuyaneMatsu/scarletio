__all__ = ('alchemy_incendiary', 'call', 'copy_func',)

from types import FunctionType

from .docs import has_docs


@has_docs
def call(function):
    """
    Calls the function returning itself.
    
    Parameters
    ----------
    function : `object`
        The function to call
    
    Returns
    -------
    function : `object`
        The function itself.
    """
    function()
    return function


@has_docs
class alchemy_incendiary:
    """
    Function wrapper familiar to `functools.partial`.
    
    Used by hata to run functions inside of executors.
    
    Attributes
    ----------
    positional_parameters : `tuple` of `object`
        Parameters to call `func` with.
    function : `callable`
        The function to call.
    keyword_parameters : `None` of `dict` of (`str`, `object`) items
        Keyword parameters to call func with if applicable.
    """
    __slots__ = ('positional_parameters', 'function', 'keyword_parameters',)
    
    
    @has_docs
    def __init__(self, function, positional_parameters, keyword_parameters = None):
        """
        Creates a new `alchemy_incendiary` with the given parameters.
        
        Parameters
        ----------
        function : `callable`
            The function to call.
        positional_parameters : `tuple<object>`
            Parameters to call `func` with.
        keyword_parameters : `None | dict<str, object>` = `None`, Optional
            Keyword parameters to call func with if applicable.
        """
        self.function = function
        self.positional_parameters = positional_parameters
        self.keyword_parameters = keyword_parameters
    
    
    @has_docs
    def __call__(self):
        """
        Calls the ``alchemy_incendiary``'s inner function with t's parameters and keyword parameters.
        
        Returns
        -------
        result : `object`
            The returned value by ``.func``.
        
        Raises
        ------
        BaseException
            The raised exception by ``.func``.
        """
        keyword_parameters = self.keyword_parameters
        if keyword_parameters is None:
            return self.function(*self.positional_parameters)
        
        return self.function(*self.positional_parameters, **keyword_parameters)


@has_docs
def copy_func(old):
    """
    Copies the given function.
    
    Parameters
    ----------
    old : `function`
        The function to copy.
    
    Returns
    -------
    new : `functions`
        The new created function.
    """
    new = FunctionType(
        old.__code__,
        old.__globals__,
        name = old.__name__,
        argdefs = old.__defaults__,
        closure = old.__closure__,
    )
    new.__kwdefaults__ = old.__kwdefaults__
    return new
