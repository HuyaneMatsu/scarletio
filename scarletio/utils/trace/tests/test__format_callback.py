from functools import partial as partial_func

import vampytest

from ...function_tools import alchemy_incendiary

from ..formatters import format_callback


def _test_function():
    pass


def _iter_options():
    yield sum, None, None, 'sum()'
    yield _test_function, None, None, '_test_function()'
    yield object.__init__, None, None, 'object.__init__()'
    yield [], None, None, 'list()'
    yield sum, ('12', '23'), {'default': ''}, 'sum(\'12\', \'23\', default = \'\')'
    yield alchemy_incendiary(sum, ('12', '23'), {'default': ''}), None, None, 'sum(\'12\', \'23\', default = \'\')'
    yield partial_func(sum, '12', '23', default = ''), None, None, 'sum(\'12\', \'23\', default = \'\')'
    
    yield (
        alchemy_incendiary(sum, ('12', '23'), {'default': ''}),
        ('hey', 'mister'),
        {'orin': 'okuu'},
        'sum(\'12\', \'23\', default = \'\')',
    )
    
    yield (
        partial_func(sum, '12', '23', default = ''),
        ('hey', 'mister'),
        {'orin': 'okuu', 'default': 'hell'},
        'sum(\'12\', \'23\', \'hey\', \'mister\', default = \'hell\', orin = \'okuu\')',
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test_format_callback(value, positional_parameters, keyword_parameters):
    """
    Tests whether ``format_callback`` works as intended.
    
    Parameters
    ----------
    function : `callable`
        The callback to format.
    positional_parameters : `None | tuple<object>` = `None`, Optional
        Additional parameters to call the `function` with.
    keyword_parameters : `None | dict<str, object>` = `None`, Optional
        Additional keyword parameters to call the `function` with.
    
    Returns
    -------
    output : `str`
    """
    return format_callback(value, positional_parameters, keyword_parameters)
