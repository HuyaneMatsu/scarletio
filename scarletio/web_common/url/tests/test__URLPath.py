import vampytest

from ..url_path import URLPath


def _iter_options__encode():
    yield None, None
    yield 'koishi', 'koishi'
    yield 'hey mister', 'hey%20mister'
    yield 'hey/mister', 'hey/mister'


@vampytest._(vampytest.call_from(_iter_options__encode()).returning_last())
def test__URLPath__encode(value):
    """
    Tests whether ``URLPath._encode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to encode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLPath._encode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__decode():
    yield None, None
    yield 'hey%20mister', 'hey mister'
    yield 'hey/mister', 'hey/mister'


@vampytest._(vampytest.call_from(_iter_options__decode()).returning_last())
def test__URLPath__decode(value):
    """
    Tests whether ``URLPath._decode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to decode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLPath._decode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__parse():
    yield None, False, None
    yield None, True, None
    yield '', False, None
    yield '', True, None
    yield '/', False, None
    yield '/', True, None
    yield '//', False, ('',)
    yield '//', True, ('',)
    yield 'koishi ', False, ('koishi ',)
    yield 'koishi%20', True, ('koishi ',)
    yield '/koishi ', False, ('koishi ',)
    yield '/koishi%20', True, ('koishi ',)
    yield 'hey/mister ', False, ('hey', 'mister ')
    yield 'hey/mister%20', True, ('hey', 'mister ')


@vampytest._(vampytest.call_from(_iter_options__parse()).returning_last())
def test__URLPath__parse(value, encoded):
    """
    Tests whether ``URLPath._parse`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to parse.
    
    encoded : `bool`
        Whether an encoded value is passed
    
    Returns
    -------
    output : `None | tuple<str>`
    """
    output = URLPath._parse(value, encoded)
    vampytest.assert_instance(output, tuple, nullable = True)
    return output


def _iter_options__serialize():
    yield None, False, None
    yield None, True, None
    yield (), False, '/'
    yield (), True, '/'
    yield ('koishi ',), False, '/koishi '
    yield ('koishi ',), True, '/koishi%20'
    yield ('hey', 'mister '), False, '/hey/mister '
    yield ('hey', 'mister '), True, '/hey/mister%20'


@vampytest._(vampytest.call_from(_iter_options__serialize()).returning_last())
def test__URLPath__serialize(value, encoded):
    """
    Tests whether ``URLPath._serialize`` works as intended.
    
    Parameters
    ----------
    value : `None | tuple<str>`
        Value to serialize.
    
    encoded : `bool`
        Whether an encoded value is requested.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLPath._serialize(value, encoded)
    vampytest.assert_instance(output, str, nullable = True)
    return output
