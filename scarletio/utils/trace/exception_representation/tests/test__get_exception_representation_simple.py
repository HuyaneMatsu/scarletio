import vampytest

from ..representation_helpers import _get_exception_representation_simple


class _TestType(ValueError):
    def __init__(self):
        pass


def _iter_options():
    yield ValueError(), 'ValueError'
    yield ValueError(12), 'ValueError: 12'
    yield ValueError('12'), 'ValueError: 12'
    yield ValueError(12, 46), None
    yield _TestType(), None


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_exception_representation_simple(input_value):
    """
    Tests whether ``_get_exception_representation_simple`` works as intended.
    
    Parameters
    ----------
    input_value : ``BaseException``
        Exception to test with.
    
    Returns
    -------
    output : `None | str`
    """
    output = _get_exception_representation_simple(input_value)
    vampytest.assert_instance(output, str, accept_subtypes = False, nullable = True)
    return output
