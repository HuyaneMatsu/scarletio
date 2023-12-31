import vampytest

from ..parsing import _normalize_and_dedent


def _iter_options():
    yield [], []
    yield ['hey   ', 'mister     '], ['hey', 'mister']
    yield ['    hey', '        mister'], ['hey', '    mister']


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__normalize_and_dedent(lines):
    """
    Tests whether ``_normalize_and_dedent`` works as intended.
    
    Parameters
    ----------
    lines : `list<str>`
        The lines to normalize.
    
    Returns
    -------
    output : `list<str>`
    """
    lines = lines.copy()
    _normalize_and_dedent(lines)
    return lines
