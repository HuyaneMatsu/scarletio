import vampytest

from ..helpers import should_status_code_have_empty_payload


def _iter_options():
    yield 99, False
    yield 100, True
    yield 101, True
    yield 199, True
    yield 200, False
    yield 201, False
    
    yield 203, False
    yield 204, True
    yield 205, False
    
    yield 303, False
    yield 304, True
    yield 305, False


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__should_status_code_have_empty_payload(status):
    """
    Tests whether ``should_status_code_have_empty_payload`` works as intended.
    
    Parameters
    ----------
    status : `int`
        Http status code.
    
    Returns
    -------
    should_have_empty_payload : `bool`
    """
    output = should_status_code_have_empty_payload(status)
    vampytest.assert_instance(output, bool)
    return output
