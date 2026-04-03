import vampytest

from ..headers import (
    METHOD_ANY, METHOD_CONNECT, METHOD_HEAD, METHOD_DELETE, METHOD_GET, METHOD_OPTIONS, METHOD_PATCH, METHOD_POST,
    METHOD_PUT, METHOD_TRACE
)
from ..helpers import should_request_method_have_empty_payload


def _iter_options():
    yield METHOD_ANY, False
    yield METHOD_CONNECT, False
    yield METHOD_HEAD, True
    yield METHOD_GET, False
    yield METHOD_DELETE, False
    yield METHOD_OPTIONS, False
    yield METHOD_PATCH, False
    yield METHOD_POST, False
    yield METHOD_PUT, False
    yield METHOD_TRACE, False


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__should_request_method_have_empty_payload(status):
    """
    Tests whether ``should_request_method_have_empty_payload`` works as intended.
    
    Parameters
    ----------
    status : `str`
        Http status code.
    
    Returns
    -------
    should_have_empty_payload : `bool`
    """
    output = should_request_method_have_empty_payload(status)
    vampytest.assert_instance(output, bool)
    return output
