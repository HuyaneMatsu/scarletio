import vampytest

from ..command import _determine_input_name


def _iter_options():
    yield '\x03', 'keyboard interrupt'
    yield '\U0002ffff', '\\U0002ffff'
    yield 'a', 'a'
    yield 'pudding', 'pudding'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__determine_input_name(input_value):
    """
    Tests whether ``_determine_input_name`` works as intended.
    
    Parameters
    ----------
    input_value : `str`
        The value to represent.
    
    Returns
    -------
    output : `str`
    """
    output = _determine_input_name(input_value)
    vampytest.assert_instance(output, str)
    return output
