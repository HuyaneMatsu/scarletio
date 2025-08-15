import vampytest

from ..ansi import stream_split_ansi_format_codes


def _iter_options():
    yield (
        '',
        [],
    )
    
    yield (
        [
            '\033[1mmiau\033[0;1;2;3mhey',
        ],
        [
            (True, '\x1b[1m'),
            (False, 'miau'),
            (True, '\x1b[0;1;2;3m'),
            (False, 'hey'),
        ],
    )
    
    yield (
        [
            'miau\033[0Kmiau',
        ],
        [
            (False, 'miau'),
            (True, '\x1b[0K'),
            (False, 'miau'),
        ],
    )
    
    yield (
        [
            '\033[0.miau',
        ],
        [
            (True, '\x1b[0'),
            (False, '.miau'),
        ],
    )
    
    yield (
        [
            '\033[.miau',
        ],
        [
            (True, '\x1b['),
            (False, '.miau'),
        ],
    )
    
    yield (
        [
            'miau\033.miau',
        ],
        [
            (False, 'miau'),
            (True, '\x1b'),
            (False, '.miau'),
        ],
    )
    
    yield (
        [
            '\033[0m',
        ],
        [
            (True, '\x1b[0m'),
        ],
    )
    
    yield (
        [
            '\033[0',
        ],
        [
            (True, '\x1b[0'),
        ],
    )
    
    yield (
        [
            '\033[',
        ],
        [
            (True, '\x1b['),
        ],
    )
    
    yield (
        [
            '\033',
        ],
        [
            (True, '\x1b'),
        ],
    )
    
    yield (
        [
            '\033[0mmiau',
        ],
        [
            (True, '\x1b[0m'),
            (False, 'miau'),
        ],
    )
    
    yield (
        [
            '\033', '[', '1', 'm', 'm', 'i', 'a', 'u', '\033', '[', '0', ';', '1', ';', '2', ';', '3', 'm', 'h', 'e', 'y',
        ],
        [
            (True, '\x1b'),
            (True, '['),
            (True, '1'),
            (True, 'm'),
            (False, 'm'),
            (False, 'i'),
            (False, 'a'),
            (False, 'u'),
            (True, '\x1b'),
            (True, '['),
            (True, '0'),
            (True, ';'),
            (True, '1'),
            (True, ';'),
            (True, '2'),
            (True, ';'),
            (True, '3'),
            (True, 'm'),
            (False, 'h'),
            (False, 'e'),
            (False, 'y'),
        ],
    )
    
    # This is how it will usually look like:
    yield (
        [
            'miau',
            '\033[',
            '0',
            'K',
            'miau',
        ],
        [
            (False, 'miau'),
            (True, '\x1b['),
            (True, '0'),
            (True, 'K'),
            (False, 'miau'),
        ],
    )
    
    # Or this:
    yield (
        [
            'miau',
            '\033[0K',
            'miau',
        ],
        [
            (False, 'miau'),
            (True, '\x1b[0K'),
            (False, 'miau'),
        ],
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__stream_split_ansi_format_codes(input_iterable):
    output = [*stream_split_ansi_format_codes(iter(input_iterable))]
    
    for element in output:
        vampytest.assert_instance(element, tuple)
        vampytest.assert_eq(len(element), 2)
        vampytest.assert_instance(element[0], bool)
        vampytest.assert_instance(element[1], str)
    
    return output

