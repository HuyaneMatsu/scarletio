import vampytest

from ..representation_helpers import _are_exception_constructors_default


class _TestType_0(ValueError):
    pass


class _TestType_1(ValueError):
    __new__ = object.__new__
    __init__ = object.__init__


class _TestType_2(ValueError):
    def __new__(cls):
        self = ValueError.__new__(cls)
        return self


class _TestType_3(ValueError):
    def __init__(self):
        pass


def _iter_options():
    yield ValueError(), True
    yield _TestType_0(), True
    yield _TestType_1(), True
    yield _TestType_2(), False
    yield _TestType_3(), False


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__are_exception_constructors_default(input_value):
    """
    Tests whether ``_are_exception_constructors_default`` works as intended.
    
    Parameters
    ----------
    input_value : `BaseException`
        Exception to test with.
    
    Returns
    -------
    output : `bool`
    """
    output = _are_exception_constructors_default(input_value)
    vampytest.assert_instance(output, bool, accept_subtypes = False)
    return output
