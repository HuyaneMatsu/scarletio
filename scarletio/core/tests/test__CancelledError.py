import vampytest

from ..exceptions import CancelledError


def test__CancelledError():
    """
    Tests whether ``CancelledError`` is a base exception.
    """
    vampytest.assert_subtype(CancelledError, BaseException)
    vampytest.assert_subtype(CancelledError, Exception, reverse = True)
