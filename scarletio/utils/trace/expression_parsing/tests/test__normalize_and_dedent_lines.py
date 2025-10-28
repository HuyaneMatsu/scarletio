import vampytest

from ..expression_info import normalize_and_dedent_lines


def _iter_options():
    yield (
        [],
        (
            0,
            [],
        ),
    )
    
    yield (
        ['hey   ', 'mister     '],
        (
            0,
            ['hey', 'mister'],
        ),
    )
    
    yield (
        ['    hey', '        mister'],
        (
            4,
            ['hey', '    mister'],
        ),
    )
    
    yield (
        ['    hey'],
        (
            4,
            ['hey'],
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__normalize_and_dedent_lines(lines):
    """
    Tests whether ``normalize_and_dedent_lines`` works as intended.
    
    Parameters
    ----------
    lines : `list<str>`
        The lines to normalize.
    
    Returns
    -------
    output : `(int, list<str>)`
    """
    lines = lines.copy()
    output = normalize_and_dedent_lines(lines)
    vampytest.assert_instance(output, int)
    return output, lines
