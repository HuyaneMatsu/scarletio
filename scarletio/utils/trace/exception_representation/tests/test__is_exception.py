import vampytest

from ..exception_helpers import is_exception


def _iter_options():
    yield None, False
    yield object(), False
    yield BaseException(), True


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__is_exception(input_value):
    """
    Tests whether ``is_exception`` works as intended.
    
    Parameters
    ----------
    input_value : `object`
        The value to test with.
    
    Returns
    -------
    output : `bool`
    """
    output = is_exception(input_value)
    vampytest.assert_instance(output, bool)
    return output
