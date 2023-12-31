import sys
from os.path import sep as PATH_SEPARATOR

import vampytest

from ..formatters import _cut_file_name


def _iter_options():
    # Nothing
    yield None, None
    yield '', None
    
    # relative? Do nothing
    yield 'orin.py', 'orin.py'
    
    path = sys.path[0]
    yield path, path
    
    # Missing path separator
    yield f'{path!s}orin.py', f'{path!s}orin.py'
    
    # Good cat
    yield f'{path!s}{PATH_SEPARATOR!s}orin.py', f'...{PATH_SEPARATOR!s}orin.py'



@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__cut_file_name(input_value):
    """
    Tests whether ``_cut_file_name`` works as intended.
    
    Parameters
    ----------
    input_value : `None | str`
        Value to test with.
    
    Returns
    -------
    output : `None | str`
    """
    return _cut_file_name(input_value)
