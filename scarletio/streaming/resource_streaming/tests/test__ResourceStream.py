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


def _iter_options__eq():
    async def function_0(positional, *, keyword):
        return
        yield
    
    async def function_1(positional, *, keyword):
        return
        yield
    
    
    yield (
        function_0,
        (12,),
        {'keyword': 24},
        function_0,
        (12,),
        {'keyword': 24},
        True,
    )
    
    yield (
        function_0,
        (12,),
        {'keyword': 24},
        function_1,
        (12,),
        {'keyword': 24},
        False,
    )
    
    yield (
        function_0,
        (12,),
        {'keyword': 24},
        function_0,
        (13,),
        {'keyword': 24},
        False,
    )
    
    yield (
        function_0,
        (12,),
        {'keyword': 24},
        function_0,
        (12,),
        {'keyword': 25},
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__ResourceStream__eq(
    function_0,
    positional_parameters_0,
    keyword_parameters_0,
    function_1,
    positional_parameters_1,
    keyword_parameters_1,
):
    """
    Tests whether ``ResourceStream.__eq__`` works as intended.
    
    Parameters
    ----------
    function_0 : `CoroutineGeneratorFunctionType`
        Coroutine generator function to create instance with.
    
    positional_parameters_0 : `tuple<object>`
        Positional parameters to create instance with.
    
    keyword_parameters_0 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    function_1 : `CoroutineGeneratorFunctionType`
        Coroutine generator function to create instance with.
    
    positional_parameters_1 : `tuple<object>`
        Positional parameters to create instance with.
    
    keyword_parameters_1 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    resource_stream_0 = ResourceStream(function_0, *positional_parameters_0, **keyword_parameters_0)
    resource_stream_1 = ResourceStream(function_1, *positional_parameters_1, **keyword_parameters_1)
    
    output = resource_stream_0 == resource_stream_1
    vampytest.assert_instance(output, bool)
    return output
