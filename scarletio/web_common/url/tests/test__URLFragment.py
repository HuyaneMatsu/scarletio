import vampytest

from ..url_fragment import URLFragment


def _iter_options__encode():
    yield None, None
    yield 'koishi', 'koishi'
    yield 'hey/mister', 'hey/mister'


@vampytest._(vampytest.call_from(_iter_options__encode()).returning_last())
def test__URLFragment__encode(value):
    """
    Tests whether ``URLFragment._encode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to encode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLFragment._encode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__decode():
    yield None, None
    yield 'hey/mister', 'hey/mister'


@vampytest._(vampytest.call_from(_iter_options__decode()).returning_last())
def test__URLFragment__decode(value):
    """
    Tests whether ``URLFragment._decode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to decode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLFragment._decode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output
