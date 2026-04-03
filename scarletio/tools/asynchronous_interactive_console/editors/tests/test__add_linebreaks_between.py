import vampytest

from ..display_state import _add_linebreaks_between


def _iter_options():
    yield [], []
    yield ['hey', 'mister'], ['hey', '\n', 'mister']
    yield ['good', 'morning', 'sisters'], ['good', '\n', 'morning', '\n', 'sisters']


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__add_linebreaks_between(lines):
    """
    Tests whether ``_add_linebreaks_between`` works as intended.
    
    Parameters
    ----------
    lines : `list<str>`
        Lines to add spaces between.
    
    Returns
    -------
    output : `list<str>`
    """
    output = _add_linebreaks_between(lines)
    
    vampytest.assert_instance(output, list)
    for value in output:
        vampytest.assert_instance(value, str)
    
    return output
