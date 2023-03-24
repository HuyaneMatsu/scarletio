import vampytest

from ..proxy_base import ProxyBase


def test__ProxyBase__new__0():
    """
    Tests whether ``ProxyBase.__new__`` works as intended.
    
    Case: not-same type given.
    """
    value = object()
    
    proxy = ProxyBase(value)
    vampytest.assert_instance(proxy, ProxyBase)
    vampytest.assert_is(proxy._proxied, value)


def test__ProxyBase__new__1():
    """
    Tests whether ``ProxyBase.__new__`` works as intended.
    
    Case: Double proxy.
    """
    value = object()
    
    proxy = ProxyBase(ProxyBase(value))
    vampytest.assert_instance(proxy, ProxyBase)
    vampytest.assert_is(proxy._proxied, value)


def test__ProxyBase__copy_self_deep():
    """
    Tests whether ``ProxyBase._copy_self_deep`` works as intended.
    
    Case: Double proxy.
    """
    value = object()
    
    proxy = ProxyBase(value)
    proxy._set_overwrite(*'ab')
    
    copy = proxy._copy_self_deep()
    vampytest.assert_instance(copy, ProxyBase)
    vampytest.assert_is(copy._proxied, value)
    vampytest.assert_eq(copy._overwrites, proxy._overwrites)


def test__ProxyBase__copy_self_clean():
    """
    Tests whether ``ProxyBase._copy_self_clean`` works as intended.
    
    Case: Double proxy.
    """
    value = object()
    
    proxy = ProxyBase(value)
    proxy._set_overwrite(*'ab')
    
    copy = proxy._copy_self_clean()
    vampytest.assert_instance(copy, ProxyBase)
    vampytest.assert_is(copy._proxied, value)
    vampytest.assert_ne(copy._overwrites, proxy._overwrites)


def test__ProxyBase__set_overwrite():
    """
    Tests whether ``ProxyBase._set_overwrite`` works as intended.
    
    Case: Double proxy.
    """
    value = object()
    
    name_0 = 'a'
    value_0 = 'b'
    
    proxy = ProxyBase(value)
    proxy._set_overwrite(name_0, value_0)
    vampytest.assert_eq(proxy._overwrites, {name_0: value_0})


def test__ProxyBase__get_overwrite__0():
    """
    Tests whether ``ProxyBase._get_overwrite`` works as intended.
    
    Case: Not found -> no registered.
    """
    value = object()
    
    name_0 = 'a'
    
    proxy = ProxyBase(value)
    
    output = proxy._get_overwrite(name_0)
    vampytest.assert_eq(output, (False, None))


def test__ProxyBase__get_overwrite__1():
    """
    Tests whether ``ProxyBase._get_overwrite`` works as intended.
    
    Case: Not found -> there are registered.
    """
    value = object()
    
    name_0 = 'a'
    
    name_1 = 'd'
    value_1 = 'e'
    
    proxy = ProxyBase(value)
    proxy._set_overwrite(name_1, value_1)
    
    output = proxy._get_overwrite(name_0)
    vampytest.assert_eq(output, (False, None))


def test__ProxyBase__get_overwrite__2():
    """
    Tests whether ``ProxyBase._get_overwrite`` works as intended.
    
    Case: Found.
    """
    value = object()
    
    name_0 = 'a'
    value_0 = 'b'
    
    proxy = ProxyBase(value)
    proxy._set_overwrite(name_0, value_0)
    
    output = proxy._get_overwrite(name_0)
    vampytest.assert_eq(output, (True, value_0))


def test__ProxyBase__get_value__0():
    """
    Tests whether ``ProxyBase._get_value`` works as intended.
    
    Case: Not overwritten.
    """
    value = object()
    
    name_0 = '__str__'
    
    proxy = ProxyBase(value)
    output = proxy._get_value(name_0)
    
    vampytest.assert_eq(output, value.__str__)


def test__ProxyBase__get_value__1():
    """
    Tests whether ``ProxyBase._get_value`` works as intended.
    
    Case: Overwritten.
    """
    value = object()
    
    name_0 = '__str__'
    value_0 = object()
    
    proxy = ProxyBase(value)
    proxy._set_overwrite(name_0, value_0)
    
    output = proxy._get_value(name_0)
    
    vampytest.assert_eq(output, value_0)


def test__ProxyBase__del_overwrite__0():
    """
    Tests whether ``ProxyBase._del_overwrite`` works as intended.
    
    Case: Registered
    """
    value = object()
    
    name_0 = 'a'
    value_1 = 'b'
    
    proxy = ProxyBase(value)
    proxy._set_overwrite(name_0, value_1)
    proxy._del_overwrite(name_0)
    
    vampytest.assert_eq(proxy._get_overwrite(name_0), (False, None))


def test__ProxyBase__del_overwrite__1():
    """
    Tests whether ``ProxyBase._del_overwrite`` works as intended.
    
    Case: Registered.
    """
    value = object()
    
    name_0 = 'a'
    
    proxy = ProxyBase(value)
    proxy._del_overwrite(name_0)
    
    vampytest.assert_eq(proxy._get_overwrite(name_0), (False, None))


def test__ProxyBase__repr():
    """
    Tests whether ``ProxyBase.__repr__`` works as intended.
    """
    proxy = ProxyBase(object())
    
    vampytest.assert_instance(repr(proxy), str)


def test__ProxyBase__hash():
    """
    Tests whether ``ProxyBase.__repr__`` works as intended.
    """
    value = object()
    
    proxy = ProxyBase(value)
    
    output = hash(proxy)
    vampytest.assert_instance(output, int)
    vampytest.assert_eq(output, hash(value))


def test__ProxyBase__eq():
    """
    Tests whether ``ProxyBase.__eq__`` works as intended.
    """
    value = object()
    
    proxy = ProxyBase(value)
    vampytest.assert_eq(proxy, proxy)
    vampytest.assert_eq(proxy, value)
    vampytest.assert_ne(proxy, object())
