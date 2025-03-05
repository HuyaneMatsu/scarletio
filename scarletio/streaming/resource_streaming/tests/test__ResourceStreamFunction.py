from types import FunctionType

import vampytest

from ..resource_stream import ResourceStream
from ..resource_stream_function import ResourceStreamFunction


async def function_to_wrap(hello, *, there = None):
    """hello"""
    yield hello
    yield there


def _assert_fields_set(resource_stream_function):
    """
    Checks whether all attributes of the given resource stream function are set.
    
    Parameters
    ----------
    resource_stream_function : ``ResourceStreamFunction``
    """
    vampytest.assert_instance(resource_stream_function, ResourceStreamFunction)
    vampytest.assert_instance(resource_stream_function.__func__, FunctionType)


def test__ResourceStreamFunction__new():
    """
    Tests whether ``ResourceStreamFunction.__new__`` works as intended.
    """
    function = function_to_wrap
    
    resource_stream_function = ResourceStreamFunction(function)
    _assert_fields_set(resource_stream_function)
    
    vampytest.assert_is(resource_stream_function.__func__, function)


def test__ResourceStreamFunction__call():
    """
    Tests whether ``ResourceStreamFunction.__new__`` works as intended.
    """
    function = function_to_wrap
    positional_parameters = (4,)
    keyword_parameters = {'there': 56}
    
    resource_stream_function = ResourceStreamFunction(function)
    
    resource_stream = resource_stream_function(*positional_parameters, **keyword_parameters)
    
    vampytest.assert_instance(resource_stream, ResourceStream)
    vampytest.assert_is(resource_stream.function, function)
    vampytest.assert_eq(resource_stream.positional_parameters, positional_parameters)
    vampytest.assert_eq(resource_stream.keyword_parameters, keyword_parameters)


def test__ResourceStreamFunction__repr():
    """
    Tests whether ``ResourceStreamFunction.__repr__`` works as intended.
    """
    function = function_to_wrap
    
    resource_stream_function = ResourceStreamFunction(function)
    
    output = repr(resource_stream_function)
    vampytest.assert_instance(output, str)
    vampytest.assert_in(type(resource_stream_function).__name__, output)
    vampytest.assert_in(function.__name__, output)


def test__ResourceStreamFunction__doc():
    """
    Tests whether ``ResourceStreamFunction.__repr__`` works as intended.
    """
    function = function_to_wrap
    
    resource_stream_function = ResourceStreamFunction(function)
    
    vampytest.assert_eq(resource_stream_function.__doc__, function.__doc__)
    vampytest.assert_ne(type(resource_stream_function).__doc__, function.__doc__)


def _iter_options__eq():
    async def function_0(positional, *, keyword):
        return
        yield
    
    async def function_1(positional, *, keyword):
        return
        yield
    
    
    yield (
        function_0,
        function_0,
        True,
    )
    
    yield (
        function_0,
        function_1,
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__ResourceStreamFunction__eq(function_0, function_1):
    """
    Tests whether ``ResourceStreamFunction.__eq__`` works as intended.
    
    Parameters
    ----------
    function_0 : `CoroutineGeneratorFunctionType`
        Coroutine generator function to create instance with.
    
    function_1 : `CoroutineGeneratorFunctionType`
        Coroutine generator function to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    resource_stream_function_0 = ResourceStreamFunction(function_0)
    resource_stream_function_1 = ResourceStreamFunction(function_1)
    
    output = resource_stream_function_0 == resource_stream_function_1
    vampytest.assert_instance(output, bool)
    return output
