import vampytest

from ..command import _escape_string


def _iter_options():
    yield '\U0002ffff', '\\U0002ffff'
    yield '\u01ff', '\\u01ff'
    yield '\x0f', '\\x0f'
    yield 'aa', '\\x61\\x61' 


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__escape_string(input_value):
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
    output = _escape_string(input_value)
    vampytest.assert_instance(output, str)
    return output
