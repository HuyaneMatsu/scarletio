import vampytest

from ..representation_helpers import _get_exception_representation_fallback


def _iter_options():
    yield ValueError(), '> repr(exception) raised, using fallback representation.\nValueError()'
    yield ValueError(12), '> repr(exception) raised, using fallback representation.\nValueError(12)'
    yield ValueError(12, 46), '> repr(exception) raised, using fallback representation.\nValueError(12, 46)'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_exception_representation_fallback(input_value):
    """
    Tests whether ``_get_exception_representation_fallback`` works as intended.
    
    Parameters
    ----------
    input_value : `BaseException`
        Exception to test with.
    
    Returns
    -------
    output : `str`
    """
    output = _get_exception_representation_fallback(input_value)
    vampytest.assert_instance(output, str, accept_subtypes = False)
    return output
