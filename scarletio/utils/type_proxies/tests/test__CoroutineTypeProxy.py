import sys

import vampytest

from ...async_utils import to_coroutine

from ..coroutine_type import CoroutineTypeProxy


PYTHON_37 = sys.version_info >= (3, 7, 0)


def test__CoroutineTypeProxy__new__0():
    """
    Tests whether ``CoroutineTypeProxy.__new__`` works as intended.
    
    Case: coroutine function given.
    """
    async def test_function():
        pass
    
    test_coroutine = test_function()
    try:
        output = CoroutineTypeProxy(test_coroutine)
        vampytest.assert_instance(output, CoroutineTypeProxy)
        vampytest.assert_is(output._proxied, test_coroutine)
    finally:
        test_coroutine.close()


def test__CoroutineTypeProxy__new__1():
    """
    Tests whether ``CoroutineTypeProxy.__new__`` works as intended.
    
    Case: proxied coroutine function given.
    """
    async def test_function():
        pass
    
    test_coroutine = test_function()
    
    try:
        output = CoroutineTypeProxy(CoroutineTypeProxy(test_coroutine))
        vampytest.assert_instance(output, CoroutineTypeProxy)
        vampytest.assert_is(output._proxied, test_coroutine)
    finally:
        test_coroutine.close()


def test__CoroutineTypeProxy__new__2():
    """
    Tests whether ``CoroutineTypeProxy.__new__`` works as intended.
    
    Case: `TypeError`
    """
    with vampytest.assert_raises(TypeError):
        CoroutineTypeProxy(object())


def test__CoroutineTypeProxy__await():
    """
    Tests whether ``CoroutineTypeProxy.__await__`` works as intended.
    """
    expected_output = object()
    
    async def test_function():
        nonlocal expected_output
        return expected_output
    
    test_coroutine = test_function()
    
    try:
        test_coroutine_proxied = CoroutineTypeProxy(test_coroutine)
        
        try:
            test_coroutine_proxied.send(None)
        except StopIteration as err:
            received_exception = err
            received_value = received_exception.value
        else:
            received_exception = None
            received_value = None
        
        vampytest.assert_is_not(received_exception, None)
        vampytest.assert_is(expected_output, received_value)
    
    finally:
        test_coroutine.close()


def test__CoroutineTypeProxy__send():
    """
    Tests whether ``CoroutineTypeProxy.send`` works as intended.
    """
    expected_output = object()
    
    @to_coroutine
    def yield_value():
        yield expected_output
    
    async def test_function():
        nonlocal yield_value
        await yield_value()
        return expected_output
    
    test_coroutine = test_function()
    
    try:
        test_coroutine_proxied = CoroutineTypeProxy(test_coroutine)
        
        try:
            output = test_coroutine_proxied.send(None)
        except StopIteration as err:
            received_exception = err
            output = None
        else:
            received_exception = None
        
        vampytest.assert_is(received_exception, None)
        vampytest.assert_is(output, expected_output)
    
    finally:
        test_coroutine.close()


def test__CoroutineTypeProxy__throw():
    """
    Tests whether ``CoroutineTypeProxy.throw`` works as intended.
    """
    thrown_exception = ValueError('hello')
    
    @to_coroutine
    def yield_value():
        yield
    
    async def test_function():
        nonlocal yield_value
        await yield_value()
        return
    
    test_coroutine = test_function()
    
    try:
        test_coroutine_proxied = CoroutineTypeProxy(test_coroutine)
        
        try:
            test_coroutine_proxied.throw(thrown_exception)
        except type(thrown_exception) as err:
            received_exception = err
        else:
            received_exception = None
        
        vampytest.assert_is(received_exception, thrown_exception)
    
    finally:
        test_coroutine.close()


def test__CoroutineTypeProxy__close():
    """
    Tests whether ``CoroutineTypeProxy.close`` works as intended.
    """
    generator_exited = False
    
    @to_coroutine
    def yield_value():
        yield
    
    async def test_function():
        nonlocal yield_value
        nonlocal generator_exited
        
        try:
            await yield_value()
        except GeneratorExit:
            generator_exited = True
            raise
    
    
    test_coroutine = test_function()
    
    try:
        test_coroutine_proxied = CoroutineTypeProxy(test_coroutine)
        test_coroutine_proxied.send(None)
        test_coroutine_proxied.close()
        
        vampytest.assert_true(generator_exited)
    
    finally:
        test_coroutine.close()


def test__CoroutineTypeProxy__proxies():
    """
    Tests whether ``CoroutineTypeProxy``'s proxies works as intended.
    """
    async def test_function():
        pass
    
    test_coroutine = test_function()
    
    try:
        test_coroutine_proxied = CoroutineTypeProxy(test_coroutine)
        
        vampytest.assert_eq(type(test_coroutine_proxied).__qualname__, type(test_coroutine).__qualname__)
        vampytest.assert_eq(test_coroutine_proxied.__class__, test_coroutine.__class__)
        vampytest.assert_eq(test_coroutine_proxied.__doc__, test_coroutine.__doc__)
        vampytest.assert_eq(test_coroutine_proxied.__name__, test_coroutine.__name__)
    
        
        vampytest.assert_eq(test_coroutine_proxied.cr_await, test_coroutine.cr_await)
        vampytest.assert_eq(test_coroutine_proxied.cr_code, test_coroutine.cr_code)
        vampytest.assert_eq(test_coroutine_proxied.cr_frame, test_coroutine.cr_frame)
        vampytest.assert_eq(test_coroutine_proxied.cr_running, test_coroutine.cr_running)
        
        if PYTHON_37:
            vampytest.assert_eq(test_coroutine_proxied.cr_origin, test_coroutine.cr_origin)
        
        # Skip the rest
        # vampytest.assert_eq(test_coroutine_proxied.__reduce__(), test_coroutine.__reduce__())
        # vampytest.assert_eq(test_coroutine_proxied.__reduce_ex__(), test_coroutine.__reduce_ex__())
        # vampytest.assert_eq(test_coroutine_proxied.__sizeof__, test_coroutine.__sizeof__)
    finally:
        test_coroutine.close()
