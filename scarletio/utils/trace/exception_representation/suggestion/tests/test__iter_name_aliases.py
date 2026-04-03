import vampytest

from ..helpers_familiarity import _iter_name_aliases


def _iter_options():
    yield 'hey_mister', {'hey_mister', 'mister_hey'}
    yield 'koishi', {'koishi'}
    yield 'KomeijiKoishi', {'komeiji_koishi', 'koishi_komeiji'}


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__iter_name_aliases(input_value):
    """
    Tests whether ``_iter_name_aliases`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        Value to get aliases of.
    
    Returns
    -------
    output : `set<str>`
    """
    output = {*_iter_name_aliases(input_value)}
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output
