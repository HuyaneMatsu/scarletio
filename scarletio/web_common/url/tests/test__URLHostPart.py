import vampytest

from ..url_host_part import URLHostPart


def _iter_options__encode():
    yield None, None
    yield 'koishi', 'koishi'
    yield 'heyű.mister', 'xn--hey-w1a.mister'


@vampytest._(vampytest.call_from(_iter_options__encode()).returning_last())
def test__URLHostPart__encode(value):
    """
    Tests whether ``URLHostPart._encode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to encode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLHostPart._encode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output


def _iter_options__decode():
    yield None, None
    yield 'xn--hey-w1a.mister', 'heyű.mister'


@vampytest._(vampytest.call_from(_iter_options__decode()).returning_last())
def test__URLHostPart__decode(value):
    """
    Tests whether ``URLHostPart._decode`` works as intended.
    
    Parameters
    ----------
    value : `None | str`
        Value to decode.
    
    Returns
    -------
    output : `None | str`
    """
    output = URLHostPart._decode(value)
    vampytest.assert_instance(output, str, nullable = True)
    return output
