import vampytest

from ..editor_base import _validate_buffer


def _iter_options__passing():
    yield None, []
    yield [], []
    yield ['hey', 'mister'], ['hey', 'mister']


def _iter_options__type_error():
    yield 12.6


@vampytest._(vampytest.call_from(_iter_options__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__type_error()).raising(TypeError))
def test__validate_buffer(input_value):
    """
    Tests whether ``_validate_buffer`` works as intended.
    
    Parameters
    ----------
    input_value : `object`
        Value to validate.
    
    Returns
    -------
    output : `list<str>`
    
    Raises
    ------
    TypeError
    """
    return _validate_buffer(input_value)
