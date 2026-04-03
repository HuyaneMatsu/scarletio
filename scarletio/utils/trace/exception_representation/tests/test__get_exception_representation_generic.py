import vampytest

from ..representation_helpers import get_exception_representation_generic


class _TestType_0(ValueError):
    def __repr__(self):
        raise AttributeError


def _iter_options():
    yield ValueError(), 'ValueError'
    yield ValueError(12), 'ValueError: 12'
    yield ValueError(12, 46), 'ValueError(12, 46)'
    yield _TestType_0(12, 46), '> repr(exception) raised, using fallback representation.\n_TestType_0(12, 46)'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_exception_representation_generic(input_value):
    """
    Tests whether ``get_exception_representation_generic`` works as intended.
    
    Parameters
    ----------
    input_value : `BaseException`
        Exception to test with.
    
    Returns
    -------
    output : `str`
    """
    output = get_exception_representation_generic(input_value)
    vampytest.assert_instance(output, str, accept_subtypes = False)
    return output
