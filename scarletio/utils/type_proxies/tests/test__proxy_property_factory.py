import vampytest

from ..field_factories import proxy_property_factory
from ..proxy_base import ProxyBase


def test__proxy_property_factory__get__0():
    """
    Tests whether `proxy_property_factory` getter returns value of the proxied instance.
    
    Case: No overwrite.
    """
    class TestType(ProxyBase):
        __doc__ = proxy_property_factory('__doc__')
    
    value = object()
    instance = TestType(value)
    vampytest.assert_eq(instance.__doc__, value.__doc__)


def test__proxy_property_factory__get__1():
    """
    Tests whether `proxy_property_factory` getter returns value of the proxied instance.
    
    Case: Overwrite.
    """
    class TestType(ProxyBase):
        __doc__ = proxy_property_factory('__doc__')
    
    value = object()
    value_1 = 'hello world'
    instance = TestType(value)
    instance._set_overwrite('__doc__', value_1)
    vampytest.assert_eq(instance.__doc__, value_1)


def test__proxy_property_factory__set():
    """
    Tests whether `proxy_property_factory` setter sets the value value to the proxy.
    """
    class TestType(ProxyBase):
        __doc__ = proxy_property_factory('__doc__')
    
    value = object()
    value_1 = 'hello world'
    instance = TestType(value)
    
    instance.__doc__ = value_1
    vampytest.assert_eq(instance.__doc__, value_1)


def test__proxy_property_factory__del():
    """
    Tests whether `proxy_property_factory` deller sets the value value to the proxy.
    """
    class TestType(ProxyBase):
        __doc__ = proxy_property_factory('__doc__')
    
    value = object()
    value_1 = 'hello world'
    instance = TestType(value)
    
    instance.__doc__ = value_1
    del instance.__doc__
    
    vampytest.assert_ne(instance.__doc__, value_1)
