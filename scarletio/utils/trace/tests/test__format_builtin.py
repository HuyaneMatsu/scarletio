import vampytest

from ..formatters import format_builtin


def _test_function():
    pass


def _iter_options():
    yield sum, 'sum()'
    yield _test_function, '_test_function()'
    yield object.__init__, 'object.__init__()'
    yield [], 'list()'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test_format_builtin(value):
    """
    Tests whether ``format_builtin`` works as intended.
    
    Parameters
    ----------
    value : `object`
        Value to format.
    
    Returns
    -------
    output : `str`
    """
    return format_builtin(value)
