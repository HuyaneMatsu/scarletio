import vampytest

from ..trace import format_coroutine


def _example_generator_function():
    return
    yield

async def _example_coroutine_function():
    pass

async def _example_coroutine_generator_function():
    return
    yield


def test__format_coroutine__0():
    """
    Tests whether `format_coroutine` acts correctly for generators.
    """
    generator = _example_generator_function()
    
    try:
        result = format_coroutine(generator)
        
        vampytest.assert_in(_example_generator_function.__name__, result)
        vampytest.assert_in('defined', result)
        vampytest.assert_in('blocked', result)
        
    finally:
        generator.close()


def test__format_coroutine__1():
    """
    Tests whether `format_coroutine` acts correctly for coroutines.
    """
    coroutine = _example_coroutine_function()
    
    try:
        result = format_coroutine(coroutine)
        
        vampytest.assert_in(_example_coroutine_function.__name__, result)
        vampytest.assert_in('defined', result)
        vampytest.assert_in('blocked', result)
        
    finally:
        coroutine.close()


def test__format_coroutine__2():
    """
    Tests whether `format_coroutine` acts correctly for coroutine generators.
    """
    coroutine_generator = _example_coroutine_generator_function()
    
    try:
        result = format_coroutine(coroutine_generator)
        
        vampytest.assert_in(_example_coroutine_generator_function.__name__, result)
        vampytest.assert_in('defined', result)
        vampytest.assert_in('blocked', result)
        
    finally:
        coroutine_generator.aclose()


def test__format_coroutine__3():
    """
    Tests whether `format_coroutine` acts correctly for random objects.
    """
    result = format_coroutine(object())
    
    vampytest.assert_in(object.__name__, result)
    vampytest.assert_in('defined', result)
    vampytest.assert_in('unknown state', result)
    vampytest.assert_in('unknown location', result)


def test__format_coroutine__4():
    """
    Tests whether `format_coroutine` shows that the coroutine is stopped.
    """
    coroutine = _example_coroutine_function()
    coroutine.close()
    
    result = format_coroutine(coroutine)
    
    vampytest.assert_in('finished', result)



def _check_state_in_generator_itself():
    try:
        self = yield
        
        result = format_coroutine(self)
        vampytest.assert_in('running', result)
        
        yield
    finally:
        self = None


def test__format_coroutine__5():
    """
    Tests whether `format_coroutine` shows that the coroutine is running.
    """
    generator = _check_state_in_generator_itself()
    try:
        generator.send(None)
        generator.send(generator)
    
    finally:
        generator.close()
