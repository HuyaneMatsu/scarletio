__all__ = ('CoroutineTypeProxy',)

from types import CoroutineType

from ..async_utils import is_coroutine

from .field_factories import proxy_method_factory, proxy_property_factory
from .proxy_base import ProxyBase


class CoroutineTypeProxy(ProxyBase):
    """
    Coroutine function proxy.
    
    Attributes
    ----------
    _overwrites : `None`, `dict` of (`str`, `object`) items
        Field overwrites.
    _proxied : `CoroutineType`
        The proxied coroutine function.
    """
    __slots__ = ()
    
    def __new__(cls, coroutine):
        """
        Creates a new coroutine proxy.
        
        Parameters
        ----------
        to_proxy : `instance<cls>`, `CoroutineType`
            The coroutine function ot proxy.
        """
        if isinstance(coroutine, cls):
            return coroutine._copy_self_deep()
        
        if is_coroutine(coroutine):
            self = object.__new__(cls)
            self._proxied = coroutine
            self._overwrites = None
            return self
        
        raise TypeError(
            f'`coroutine` can be either a coroutine or `{cls.__name__}`, '
            f'got {coroutine.__class__.__name__}.'
        )
    
    
    __qualname__ = CoroutineType.__qualname__
    
    __class__ = proxy_property_factory('__class__')
    __doc__ = proxy_property_factory('__doc__')
    __name__ = proxy_property_factory('__name__')
    
    __await__ = proxy_method_factory('__await__')
    __reduce__ = proxy_method_factory('__reduce__')
    __reduce_ex__ = proxy_method_factory('__reduce_ex__')
    __sizeof__ = proxy_method_factory('__sizeof__')
    cr_await = proxy_property_factory('cr_await')
    cr_code = proxy_property_factory('cr_code')
    cr_frame = proxy_property_factory('cr_frame')
    cr_origin = proxy_property_factory('cr_origin')
    cr_running = proxy_property_factory('cr_running')
    
    send = proxy_method_factory('send')
    throw = proxy_method_factory('throw')
    close = proxy_method_factory('close')
