import vampytest

from ....utils import MultiValueDictionary

from ..url_query import serialize_query


def _iter_options():
    # No query (null)
    yield (
        None,
        False,
        None,
    )
    
    # No query (empty)
    yield (
        MultiValueDictionary(),
        False,
        None,
    )
    
    # Query (1)
    yield (
        MultiValueDictionary([
            ('hey', 'mister'),
        ]),
        False,
        'hey=mister',
    )
    
    # Query (2)
    yield (
        MultiValueDictionary([
            ('hey', 'mister'),
            ('see', 'you'),
        ]),
        False,
        'hey=mister&see=you',
    )
    
    # Query (2, different order)
    yield (
        MultiValueDictionary([
            ('see', 'you'),
            ('hey', 'mister'),
        ]),
        False,
        'hey=mister&see=you',
    )
    
    # Query (1 key + 2 values)
    yield (
        MultiValueDictionary([
            ('hey', 'mister'),
            ('hey', 'sister'),
        ]),
        False,
        'hey=mister&hey=sister',
    )
    
    # Query (empty key)
    yield (
        MultiValueDictionary([
            ('', 'mister'),
        ]),
        False,
        '=mister',
    )
    
    # Query (empty value)
    yield (
        MultiValueDictionary([
            ('hey', ''),
        ]),
        False,
        'hey=',
    )
    
    # Query (encoded)
    yield (
        MultiValueDictionary([
            ('hey ', 'mister '),
        ]),
        True,
        'hey+=mister+',
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__serialize_query(value, encoded):
    """
    Tests whether ``serialize_query`` works as intended.
    
    Parameters
    ----------
    value : `None | MultiValueDictionary<str, str>`
        Query value
    
    encoded : `bool`
        Whether an encoded value is requested.
    
    Returns
    -------
    output : `None | str`
    """
    output = serialize_query(value, encoded)
    vampytest.assert_instance(output, str, nullable = True)
    return output
