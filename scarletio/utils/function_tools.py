__all__ = ('alchemy_incendiary', 'call', 'copy_func',)

from types import FunctionType

from .docs import has_docs
from .trace import ignore_frame


ignore_frame(__spec__.origin, '__call__', 'return self.func(*self.args)', )
ignore_frame(__spec__.origin, '__call__', 'return self.func(*self.args, **kwargs)', )

@has_docs
def call(function):
    """
    Calls the function returning itself.
    
    Parameters
    ----------
    function : `Any`
        The function to call
    
    Returns
    -------
    function : `Any`
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
    args : `tuple` of `Any`
        Parameters to call `func` with.
    func : `callable`
        The function to call.
    kwargs : `None` of `dict` of (`str`, `Any`) items
        Keyword parameters to call func with if applicable.
    """
    __slots__ = ('args', 'func', 'kwargs',)
    
    @has_docs
    def __init__(self, func, args, kwargs=None):
        """
        Creates a new `alchemy_incendiary` with the given parameters.
        
        Parameters
        ----------
        func : `callable`
            The function to call.
        args : `tuple` of `Any`
            Parameters to call `func` with.
        kwargs : `None` of `dict` of (`str`, `Any`) items = `None`, Optional
            Keyword parameters to call func with if applicable.
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    @has_docs
    def __call__(self):
        """
        Calls the ``alchemy_incendiary``'s inner function with t's parameters and keyword parameters.
        
        Returns
        -------
        result : `Any`
            The returned value by ``.func``.
        
        Raises
        ------
        BaseException
            The raised exception by ``.func``.
        """
        kwargs = self.kwargs
        if kwargs is None:
            return self.func(*self.args)
        
        return self.func(*self.args, **kwargs)


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
    new = FunctionType(old.__code__, old.__globals__, name=old.__name__, argdefs=old.__defaults__,
        closure=old.__closure__)
    new.__kwdefaults__ = old.__kwdefaults__
    return new
