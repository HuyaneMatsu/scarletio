import vampytest

from ..ansi import iter_split_ansi_format_codes


def _iter_options():
    yield (
        '',
        [],
    )
    
    yield (
        '\033[1mmiau\033[0;1;2;3mhey',
        [
            (True, '\x1b[1m'),
            (False, 'miau'),
            (True, '\x1b[0;1;2;3m'),
            (False, 'hey'),
        ],
    )
    
    yield (
        'miau\033[0Kmiau',
        [
            (False, 'miau'),
            (True, '\x1b[0K'),
            (False, 'miau'),
        ],
    )
    
    yield (
        '\033[0.miau',
        [
            (True, '\x1b[0'),
            (False, '.miau'),
        ],
    )
    
    yield (
        '\033[.miau',
        [
            (True, '\x1b['),
            (False, '.miau'),
        ],
    )
    
    yield (
        'miau\033.miau',
        [
            (False, 'miau'),
            (True, '\x1b'),
            (False, '.miau'),
        ],
    )
    
    yield (
        '\033[0m',
        [
            (True, '\x1b[0m'),
        ],
    )
    
    yield (
        '\033[0',
        [
            (True, '\x1b[0'),
        ],
    )
    
    yield (
        '\033[',
        [
            (True, '\x1b['),
        ],
    )
    
    yield (
        '\033',
        [
            (True, '\x1b'),
        ],
    )
    
    yield (
        '\033[0mmiau',
        [
            (True, '\x1b[0m'),
            (False, 'miau'),
        ],
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__iter_split_ansi_format_codes(string):
    """
    Tests whether ``iter_split_ansi_format_codes`` works as intended.
    
    Parameters
    ----------
    string : `str`
        The string to split.
    
    Returns
    -------
    output : `list<(bool, str)>`
    """
    return [*iter_split_ansi_format_codes(string)]
