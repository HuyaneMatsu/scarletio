import vampytest

from ..quoting import quote


def _iter_options():
    yield (
        None,
        None,
        None,
        False,
        None,
    )
    
    yield (
        '',
        None,
        None,
        False,
        '',
    )
    
    yield (
        'hey mister',
        None,
        None,
        False,
        'hey%20mister',
    )
    
    yield (
        'hey mister',
        None,
        None,
        True,
        'hey+mister',
    )
    
    yield (
        'hey mister',
        ' ',
        None,
        False,
        'hey mister',
    )
    
    yield (
        'ű',
        ' ',
        None,
        False,
        '%C5%B1',
    )
    
    yield (
        '100%',
        None,
        None,
        False,
        '100%25',
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__quote(input_value, safe, protected, query_string):
    """
    Tests whether ``quote`` works as intended.
    
    Parameters
    ----------
    input_value : `None | str`
        Value to quote.
    
    safe : `None | str`
        Additional not percentage encoding safe characters, which should not be contained by potentially percent
        encoded characters.
    
    protected : `None | str`
        Additional characters, which should not be percentage encoded.
    
    query_string : `bool`
        Whether the `value` is a query string value.
    
    Returns
    -------
    output : `None | str`
    """
    output = quote(input_value, safe, protected, query_string)
    vampytest.assert_instance(output, str, nullable = True)
    return output
