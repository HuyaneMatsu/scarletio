import vampytest

from ..helpers_familiarity import _get_familiar_names


def _iter_options():
    yield {'hey_mister', 'hey_master', 'mister_hey'}, 'hey_mister', ['mister_hey', 'hey_mister', 'hey_master']
    yield {'Koishi', 'koishi', 'satori'}, 'Koishi', ['Koishi', 'koishi']
    yield {'koishi', 'orin', 'okuu'}, 'satori', []
    
    # Test for duplication
    yield {'_A__ayaya'}, '_a__ayaya', ['_A__ayaya']


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_familiar_names(names, name):
    """
    Tests whether ``_get_familiar_names`` works as intended.
    
    Parameters
    ----------
    names : `set<str>`
        Names to get suggestions from.
    name : `str`
        Name to get suggestions for.
    
    Returns
    -------
    output : `list<str>`
    """
    output = _get_familiar_names(names, name)
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output
