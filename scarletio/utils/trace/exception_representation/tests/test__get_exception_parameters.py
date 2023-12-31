import vampytest

from ..representation_helpers import _get_exception_parameters


class _TestTuple_0(tuple):
    pass


class _TestTuple_1(tuple):
    @property
    def __class__(self):
        return int


class _TestException_0(ValueError):
    @property
    def args(self):
        return None


def _iter_options():
    exception = ValueError('aya', 'ya')
    yield exception, ('aya', 'ya')
    
    # Python does not allow random trash on my version
    """
    exception = ValueError()
    exception.args = object()
    yield exception, None
    """
    
    exception = ValueError('aya', 'ya')
    exception.args = _TestTuple_0(exception.args)
    yield exception, ('aya', 'ya')
    
    # Python converts it to tuple on my version
    """
    exception = ValueError('aya', 'ya')
    exception.args = _TestTuple_1(exception.args)
    yield exception, None
    """
    
    exception = _TestException_0('aya', 'ya')
    yield exception, ('aya', 'ya')


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_exception_parameters(input_value):
    """
    Tests whether ``_get_exception_parameters`` works as intended.
    
    Parameters
    ----------
    input_value : ``BaseException``
        Exception to test with.
    
    Returns
    -------
    output : `None | tuple<object>`
    """
    output = _get_exception_parameters(input_value)
    vampytest.assert_instance(output, tuple, accept_subtypes = False, nullable = True)
    return output
