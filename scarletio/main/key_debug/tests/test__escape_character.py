import vampytest

from ..command import _escape_character


def _iter_options():
    yield '\U0002ffff', '\\U0002ffff'
    yield '\u01ff', '\\u01ff'
    yield '\x0f', '\\x0f'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__escape_character(input_value):
    """
    Tests whether ``_escape_character`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        The value to represent.
    
    Returns
    -------
    output : `str`
    """
    output = _escape_character(input_value)
    vampytest.assert_instance(output, str)
    return output
