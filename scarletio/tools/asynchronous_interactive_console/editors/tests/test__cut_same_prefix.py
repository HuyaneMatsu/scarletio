import vampytest

from ..display_state import _cut_same_prefix


def _iter_options():
    yield (
        '',
        '',
        (0, '', ''),
    )
    
    yield (
        'orin',
        'orin',
        (4, '', ''),
    )
    
    yield (
        'orin',
        'miau',
        (0, 'orin', 'miau'),
    )
    
    yield (
        'orin',
        'okuu',
        (1, 'rin', 'kuu'),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__cut_same_prefix(string_0, string_1):
    """
    Tests whether ``_cut_same_prefix`` works as intended.
    
    Parameters
    ----------
    string_0 : `str`
        String to cut.
    string_1 : `str`
        String to cut.
    
    Returns
    -------
    output : `(int, str, str)`
    """
    return _cut_same_prefix(string_0, string_1)
