import vampytest

from ..quoting import unquote


def _iter_options():
    yield (
        None,
        None,
        False,
        None,
    )
    
    yield (
        '',
        None,
        False,
        '',
    )
    
    yield (
        'hey%20mister',
        None,
        False,
        'hey mister',
    )
    
    yield (
        'hey+mister',
        None,
        True,
        'hey mister',
    )
    
    yield (
        'hey%20mister',
        ' ',
        False,
        'hey%20mister',
    )
    
    yield (
        '%C5%B1',
        ' ',
        False,
        'ű',
    )
    
    yield (
        '%20',
        None,
        False,
        ' ',
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__unquote(input_value, unsafe, query_string):
    """
    Tests whether ``unquote`` works as intended.
    
    Parameters
    ----------
    input_value : `None | str`
        Value to unquote.
    
    unsafe : `None | str`
        Additional not percentage encoding safe characters, which should not be contained by potentially percent
        encoded characters.
    
    query_string : `bool`
        Whether the `value` is a query string value.
    
    Returns
    -------
    output : `None | str`
    """
    output = unquote(input_value, unsafe, query_string)
    vampytest.assert_instance(output, str, nullable = True)
    return output
