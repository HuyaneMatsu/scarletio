import vampytest

from ....utils import MultiValueDictionary

from ..url_query import parse_query


def _iter_options():
    # No query (null)
    yield (
        None,
        False,
        None,
    )
    
    # No query (empty string)
    yield (
        '',
        False,
        None,
    )
    
    # Empty query (1)
    yield (
        '&',
        False,
        None,
    )
    
    # Empty query (1+)
    yield (
        '&&&&&&',
        False,
        None,
    )
    
    # Query (1)
    yield (
        'hey=mister',
        False,
        MultiValueDictionary([
            ('hey', 'mister'),
        ]),
    )
    
    # Query (2)
    yield (
        'hey=mister&see=you',
        False,
        MultiValueDictionary([
            ('hey', 'mister'),
            ('see', 'you'),
        ]),
    )
    
    # Query (1 key + 2 values)
    yield (
        'hey=mister&hey=sister',
        False,
        MultiValueDictionary([
            ('hey', 'mister'),
            ('hey', 'sister'),
        ]),
    )
    
    # Query (empty key)
    yield (
        '=mister',
        False,
        MultiValueDictionary([
            ('', 'mister'),
        ]),
    )
    
    # Query (empty value)
    yield (
        'hey=',
        False,
        MultiValueDictionary([
            ('hey', ''),
        ]),
    )
    
    # Query (encoded)
    yield (
        'hey%20=mister%20',
        True,
        MultiValueDictionary([
            ('hey ', 'mister '),
        ]),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__parse_query(value, encoded):
    """
    Tests whether ``parse_query`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to parse.
    
    encoded : `bool`
        Whether an encoded value is passed.
    
    Returns
    -------
    output : `None | MultiValueDictionary<str, str>`
    """
    output = parse_query(value, encoded)
    vampytest.assert_instance(output, MultiValueDictionary, nullable = True)
    return output
