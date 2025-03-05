from types import FunctionType

import vampytest

from ..resource_stream import ResourceStream


async def function_to_wrap(hello, *, there = None):
    """hello"""
    yield hello
    yield there


def _assert_fields_set(resource_stream):
    """
    Checks whether all attributes of the given resource stream function are set.
    
    Parameters
    ----------
    resource_stream : ``ResourceStream``
    """
    vampytest.assert_instance(resource_stream, ResourceStream)
    vampytest.assert_instance(resource_stream.function, FunctionType)
    vampytest.assert_instance(resource_stream.positional_parameters, tuple)
    vampytest.assert_instance(resource_stream.keyword_parameters, dict)


def test__ResourceStream__new():
    """
    Tests whether ``ResourceStream.__new__`` works as intended.
    """
    function = function_to_wrap
    positional_parameters = (4,)
    keyword_parameters = {'there': 56}
    
    resource_stream = ResourceStream(function, *positional_parameters, **keyword_parameters)
    _assert_fields_set(resource_stream)
    
    vampytest.assert_is(resource_stream.function, function)
    vampytest.assert_eq(resource_stream.positional_parameters, positional_parameters)
    vampytest.assert_eq(resource_stream.keyword_parameters, keyword_parameters)


def test__ResourceStream__from_fields():
    """
    Tests whether ``ResourceStream.from_fields`` works as intended.
    """
    function = function_to_wrap
    positional_parameters = (4,)
    keyword_parameters = {'there': 56}
    
    resource_stream = ResourceStream.from_fields(function, positional_parameters, keyword_parameters)
    _assert_fields_set(resource_stream)
    
    vampytest.assert_is(resource_stream.function, function)
    vampytest.assert_eq(resource_stream.positional_parameters, positional_parameters)
    vampytest.assert_eq(resource_stream.keyword_parameters, keyword_parameters)


def test__ResourceStream__aiter():
    """
    Tests whether ``ResourceStream.__aiter__`` works as intended.
    """
    function = function_to_wrap
    positional_parameters = (4,)
    keyword_parameters = {'there': 56}
    
    resource_stream = ResourceStream.from_fields(function, positional_parameters, keyword_parameters)
    
    for _ in range(2):
        collected = []
        coroutine_generator = resource_stream.__aiter__()
        while True:
            coroutine = coroutine_generator.asend(None)
            
            try:
                while True:
                    coroutine.send(None)
            except StopIteration as exception:
                chunk = exception.value
            
            except StopAsyncIteration:
                break
            
            collected.append(chunk)
        
        vampytest.assert_eq(
            collected,
            [4, 56],
        )


def test__ResourceStream__repr():
    """
    Tests whether ``ResourceStream.__repr__`` works as intended.
    """
    function = function_to_wrap
    positional_parameters = (4,)
    keyword_parameters = {'there': 56}
    
    resource_stream = ResourceStream.from_fields(function, positional_parameters, keyword_parameters)
    
    output = repr(resource_stream)
    vampytest.assert_in(type(resource_stream).__name__, output)
    vampytest.assert_in(function.__name__, output)
    
    for positional_parameter in positional_parameters:
        vampytest.assert_in(repr(positional_parameter), output)
    
    for key, value in keyword_parameters.items():
        vampytest.assert_in(f'{key!s} = {value!r}', output)
