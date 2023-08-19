import vampytest

from ..editor_advanced import _get_identifier_to_autocomplete


def _iter_options():
    yield '', 0, None
    yield ' ', 1, None
    yield 'a', 1, 'a'
    yield 'a ', 1, 'a'
    yield 'aa', 1, None
    
    yield 'abc', 3, 'abc'
    yield 'abc ', 3, 'abc'
    yield 'abcd', 3, None
    
    yield '691', 3, None
    yield '_56', 3, '_56'
    yield 'hi.me', 5, None
    yield 'hi. e', 5, None
    yield 'hi me', 5, 'me'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_identifier_to_autocomplete(line, index):
    """
    Tests whether ``_get_identifier_to_autocomplete`` works as intended.
    
    Parameters
    ----------
    line : `str`
        Current line.
    index : `int`
        The cursor's index in the line.
    
    Returns
    -------
    identifier_to_autocomplete : `None`, `str`
    """
    return _get_identifier_to_autocomplete(line, index)
