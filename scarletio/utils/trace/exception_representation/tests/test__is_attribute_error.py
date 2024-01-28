import vampytest

from ....rich_attribute_error import AttributeError as RichAttributeError

from ..attribute_error_helpers import is_attribute_error


def _iter_options():
    yield RichAttributeError(None, None), False
    yield RichAttributeError(None, 'mister'), True
    yield AttributeError(None, 'mister'), False
    yield ValueError(None, 'mister'), False


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__is_attribute_error(exception):
    """
    Tests whether ``is_attribute_error`` works as intended.
    
    Parameters
    ----------
    exception : `object`
        The exception to check whether is it an attribute error.
    
    Returns
    -------
    output : `bool`
    """
    output = is_attribute_error(exception)
    vampytest.assert_instance(output, bool)
    return output
