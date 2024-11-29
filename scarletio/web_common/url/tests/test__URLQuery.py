import vampytest

from ....utils import MultiValueDictionary

from ..url_query import URLQuery


def _iter_options__encode():
    yield None, None
    yield 'koishi', 'koishi'
    yield 'hey mister=sister', 'hey+mister=sister'
    yield 'hey?mister=sister', 'hey?mister=sister'


@vampytest._(vampytest.call_from(_iter_options__encode()).returning_last())
def test__URLQuery__encode(value):
    """
    Tests whether ``URLQuery._encode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to encode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLQuery._encode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__decode():
    yield None, None
    yield 'hey%20mister=sister', 'hey mister=sister'
    yield 'hey+mister=sister', 'hey mister=sister'
    yield 'hey?mister=sister', 'hey?mister=sister'


@vampytest._(vampytest.call_from(_iter_options__decode()).returning_last())
def test__URLQuery__decode(value):
    """
    Tests whether ``URLQuery._decode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to decode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLQuery._decode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__parse():
    yield None, False, None
    yield None, True, None
    yield 'koishi=sister ', False, MultiValueDictionary([('koishi', 'sister ')])
    yield 'koishi=sister+', True, MultiValueDictionary([('koishi', 'sister ')])
    yield 'hey?mister=sister ', False, MultiValueDictionary([('hey?mister', 'sister ')])
    yield 'hey?mister=sister+', True, MultiValueDictionary([('hey?mister', 'sister ')])


@vampytest._(vampytest.call_from(_iter_options__parse()).returning_last())
def test__URLQuery__parse(value, encoded):
    """
    Tests whether ``URLQuery._parse`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to parse.
    
    encoded : `bool`
        Whether an encoded value is passed
    
    Returns
    -------
    output : `None | MultiValueDictionary<str, str>`
    """
    output = URLQuery._parse(value, encoded)
    vampytest.assert_instance(output, MultiValueDictionary, nullable = True)
    return output


def _iter_options__serialize():
    yield None, False, None
    yield None, True, None
    yield MultiValueDictionary([('koishi', 'sister ')]), False, 'koishi=sister '
    yield MultiValueDictionary([('koishi', 'sister ')]), True, 'koishi=sister+'
    yield MultiValueDictionary([('hey?mister', 'sister ')]), False, 'hey?mister=sister '
    yield MultiValueDictionary([('hey?mister', 'sister ')]), True, 'hey?mister=sister+'


@vampytest._(vampytest.call_from(_iter_options__serialize()).returning_last())
def test__URLQuery__serialize(value, encoded):
    """
    Tests whether ``URLQuery._serialize`` works as intended.
    
    Parameters
    ----------
    value : `None | MultiValueDictionary<str, str>`
        Value to serialize.
    
    encoded : `bool`
        Whether an encoded value is requested.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLQuery._serialize(value, encoded)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def test__URLQuery__quote_applied_correctly():
    """
    Tests whether ``URLQuery`` quoting is applied as intended independently from call order.
    """
    output = URLQuery.create_from_parsed(MultiValueDictionary([('hey', 'mister'), ('nyan', 'ers')]))
    vampytest.assert_eq(output.encoded, output.decoded)

    output = URLQuery.create_from_parsed(MultiValueDictionary([('hey', 'mister'), ('nyan', 'ers')]))
    vampytest.assert_eq(output.decoded, output.encoded)
