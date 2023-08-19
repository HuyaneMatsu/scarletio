import vampytest

from ..auto_completer import AutoCompleter


def test__AutoCompleter__new():
    """
    Tests whether ``AutoCompleter.__new__`` works as intended.
    """
    variables = {'koishi': None}
    
    auto_completer = AutoCompleter(variables)
    
    vampytest.assert_instance(auto_completer, AutoCompleter)
    vampytest.assert_instance(auto_completer._variables, dict)
    
    vampytest.assert_is(auto_completer._variables, variables)


def test__AutoCompleter__repr():
    """
    Tests whether ``AutoCompleter.__repr__`` works as intended.
    """
    variables = {'koishi': None}
    
    auto_completer = AutoCompleter(variables)
    
    vampytest.assert_instance(repr(auto_completer), str)


def _iter_options__get_common_prefix():
    yield {'koishi': None}, 'satori', None
    yield {'koishi': None, 'satori_mommy': None}, 'satori', 'satori_mommy'
    yield {'koishi': None, 'satori_mommy': None, 'satori_mama': None}, 'satori', 'satori_m'
    yield {'koishi': None, 'satori_mommy': None, 'satori0mama': None}, 'satori', None
    yield {}, 'Imp', 'Import'
    yield (
        {
            'is_coroutine': None,
            'is_coroutine_function': None,
            'is_coroutine_generator': None,
            'is_coroutine_generator_function': None
        },
        'is_co',
        'is_coroutine',
    )


@vampytest._(vampytest.call_from(_iter_options__get_common_prefix()).returning_last())
def test__AutoCompleter__get_common_prefix(input_variables, to_match):
    """
    Tests whether ``AutoCompleter.get_common_prefix`` works as intended.
    
    Parameters
    ----------
    input_variables : `dict<str, object>`
        Input variables to auto complete from.
    to_match : `str`
        The string to match.
    
    Returns
    -------
    match : `None`, `str`
    """
    auto_completer = AutoCompleter(input_variables)
    return auto_completer.get_common_prefix(to_match)


def test__AutoCompleter__iter_matches():
    """
    Tests whether ``AutoCompleter._iter_matches`` works as intended.
    """
    auto_completer = AutoCompleter({'Imperial': None})
    vampytest.assert_eq({*auto_completer._iter_matches('Imp')}, {'Imperial', 'ImportError', 'ImportWarning'})


def test__AutoCompleter__iter_variable_names():
    """
    Tests whether ``AutoCompleter._iter_variable_names`` works as intended.
    """
    auto_completer = AutoCompleter({'Koishi': None})
    
    output = {*auto_completer._iter_variable_names()}
    
    vampytest.assert_in('Koishi', output)
    vampytest.assert_in('sum', output)
