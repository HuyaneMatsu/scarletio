__all__ = ('CoroutineFunctionTypeProxy',)

from types import FunctionType, MethodType

from ..async_utils import is_coroutine_function

from .coroutine_type import CoroutineTypeProxy
from .field_factories import proxy_method_factory, proxy_property_factory
from .proxy_base import ProxyBase


class CoroutineFunctionTypeProxy(ProxyBase):
    """
    Coroutine function proxy.
    
    Attributes
    ----------
    _overwrites : `None`, `dict` of (`str`, `object`) items
        Field overwrites.
    _proxied : `CoroutineFunctionType`
        The proxied coroutine function.
    """
    __slots__ = ()
    
    def __new__(cls, coroutine_function):
        """
        Creates a new coroutine function proxy.
        
        Parameters
        ----------
        to_proxy : `instance<cls>`, `CoroutineFunctionType`
            The coroutine function ot proxy.
        """
        if isinstance(coroutine_function, cls):
            return coroutine_function._copy_self_deep()
        
        if is_coroutine_function(coroutine_function):
            self = object.__new__(cls)
            self._proxied = coroutine_function
            self._overwrites = None
            return self
        
        raise TypeError(
            f'`coroutine_function` can be either a coroutine function or `{cls.__name__}`, '
            f'got {coroutine_function.__class__.__name__}.'
        )
    
    
    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        
        return MethodType(self.__call__, instance)
    
    
    def __call__(self, *positional_parameters, **keyword_parameters):
        return CoroutineTypeProxy(self._proxied(*positional_parameters, **keyword_parameters))
    
    
    __qualname__ = FunctionType.__qualname__
    
    __annotations__ = proxy_property_factory('__annotations__')
    __class__ = proxy_property_factory('__class__')
    __closure__ = proxy_property_factory('__closure__')
    __code__ = proxy_property_factory('__code__')
    __defaults__ = proxy_property_factory('__defaults__')
    __dict__ = proxy_property_factory('__dict__')
    __doc__ = proxy_property_factory('__doc__')
    __globals__ = proxy_property_factory('__globals__')
    __kwdefaults__ = proxy_property_factory('__kwdefaults__')
    __name__ = proxy_property_factory('__name__')
    
    
    __reduce__ = proxy_method_factory('__reduce__')
    __reduce_ex__ = proxy_method_factory('__reduce_ex__')
    __sizeof__ = proxy_method_factory('__sizeof__')
