import vampytest

from ..prefix_trimming import trim_console_prefix

def test__trim_console_prefix():
    """
    Tests whether ``trim_console_prefix`` trims every string as expected.
    """
    for input_string, expected_output in (
        (
            'owo',
            None,
        ), (
            'In [0]: rwr',
            'rwr',
        ), (
            '>>> owo',
            'owo',
        ), (
            '>>>> cwc',
            'cwc',
        ), (
            '>>>  uwu',
            ' uwu',
        ), (
            '   ...: qwq',
            'qwq',
        ), (
            '... pwp',
            'pwp',
        ), (
            '... ewe',
            'ewe',
        ), (
            '   ...:',
            '',
        ), (
            '...',
            None,
        ), (
            '....',
            '',
        ), (
            'In [12323]: awa',
            'awa',
        ), (
            'In [0]: ',
            '',
        ), (
            'In [0]: owo\n'
            '   ...: uwu',
            'owo\n'
            'uwu',
        ), (
            '   ...: owo\n'
            '   ...: uwu',
            'owo\n'
            'uwu',
        ), (
            '   ...:  owo\n'
            '   ...: ',
            ' owo\n'
            '',
        ), (
            '   ...: \n'
            '   ...: ',
            '',
        ), (
            ' owo\n'
            '   ...: uwu',
            ' owo\n'
            'uwu',
        ), (
            'in [0]: owo ',
            None,
        ), (
            'In [ab]: owo',
            None,
        )
    ):
        output = trim_console_prefix(input_string)
        vampytest.assert_eq(output, expected_output)
