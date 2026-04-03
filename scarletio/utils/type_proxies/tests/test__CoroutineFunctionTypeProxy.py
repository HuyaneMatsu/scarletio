import vampytest

from ..coroutine_function_type import CoroutineFunctionTypeProxy
from ..coroutine_type import CoroutineTypeProxy


def test__CoroutineFunctionTypeProxy__new__0():
    """
    Tests whether ``CoroutineFunctionTypeProxy.__new__`` works as intended.
    
    Case: coroutine function given.
    """
    async def test_function():
        pass
    
    output = CoroutineFunctionTypeProxy(test_function)
    vampytest.assert_instance(output, CoroutineFunctionTypeProxy)
    vampytest.assert_is(output._proxied, test_function)


def test__CoroutineFunctionTypeProxy__new__1():
    """
    Tests whether ``CoroutineFunctionTypeProxy.__new__`` works as intended.
    
    Case: proxied coroutine function given.
    """
    async def test_function():
        pass
    
    output = CoroutineFunctionTypeProxy(CoroutineFunctionTypeProxy(test_function))
    vampytest.assert_instance(output, CoroutineFunctionTypeProxy)
    vampytest.assert_is(output._proxied, test_function)


def test__CoroutineFunctionTypeProxy__new__2():
    """
    Tests whether ``CoroutineFunctionTypeProxy.__new__`` works as intended.
    
    Case: `TypeError`
    """
    with vampytest.assert_raises(TypeError):
        CoroutineFunctionTypeProxy(object())


def test__CoroutineFunctionTypeProxy__call__0():
    """
    Tests whether ``CoroutineFunctionTypeProxy.__call__`` works as intended.
    
    Case: function.
    """
    async def test_function(p0):
        pass
    
    test_function_proxied = CoroutineFunctionTypeProxy(test_function)
    
    output = None
    test_value = None
    
    try:
        output = test_function_proxied(6)
        vampytest.assert_instance(output, CoroutineTypeProxy)
        
        test_value = test_function(6)
        vampytest.assert_eq(output.cr_code, test_value.cr_code)
    
    finally:
        if (output is not None):
            output.close()
        
        if (test_value is not None):
            test_value.close()


def test__CoroutineFunctionTypeProxy__call__1():
    """
    Tests whether ``CoroutineFunctionTypeProxy.__call__`` works as intended.
    
    Case: Method.
    """
    class TestType:
        async def test_function(self, p0):
            pass
        
        test_function_proxied = CoroutineFunctionTypeProxy(test_function)
    
    instance = TestType()
    
    output = None
    test_value = None
        
    try:
        output = instance.test_function_proxied(6)
        vampytest.assert_instance(output, CoroutineTypeProxy)
        
        test_value = instance.test_function(6)
        vampytest.assert_eq(output.cr_code, test_value.cr_code)
    
    finally:
        if (output is not None):
            output.close()
        
        if (test_value is not None):
            test_value.close()


def test__CoroutineFunctionTypeProxy__proxies():
    """
    Tests whether ``CoroutineFunctionTypeProxy``'s proxies works as intended.
    """
    async def test_function():
        pass
    
    test_function_proxied = CoroutineFunctionTypeProxy(test_function)
    
    vampytest.assert_eq(type(test_function_proxied).__qualname__, type(test_function).__qualname__)
    vampytest.assert_eq(test_function_proxied.__annotations__, test_function.__annotations__)
    vampytest.assert_eq(test_function_proxied.__class__, test_function.__class__)
    vampytest.assert_eq(test_function_proxied.__closure__, test_function.__closure__)
    vampytest.assert_eq(test_function_proxied.__code__, test_function.__code__)
    vampytest.assert_eq(test_function_proxied.__defaults__, test_function.__defaults__)
    vampytest.assert_eq(test_function_proxied.__dict__, test_function.__dict__)
    vampytest.assert_eq(test_function_proxied.__doc__, test_function.__doc__)
    vampytest.assert_eq(test_function_proxied.__globals__, test_function.__globals__)
    vampytest.assert_eq(test_function_proxied.__kwdefaults__, test_function.__kwdefaults__)
    vampytest.assert_eq(test_function_proxied.__name__, test_function.__name__)
    
    # Skip the rest
    # vampytest.assert_eq(test_function_proxied.__reduce__(), test_function.__reduce__())
    # vampytest.assert_eq(test_function_proxied.__reduce_ex__(), test_function.__reduce_ex__())
    # vampytest.assert_eq(test_function_proxied.__sizeof__, test_function.__sizeof__)
