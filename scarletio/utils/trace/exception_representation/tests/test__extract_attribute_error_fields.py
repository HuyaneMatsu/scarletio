import vampytest

from ....rich_attribute_error import AttributeError as RichAttributeError

from ..attribute_error_helpers import extract_attribute_error_fields


def test__extract_attribute_error_fields():
    """
    Tests whether ``extract_attribute_error_fields`` works as intended.
    """
    instance = object()
    attribute_name = 'mister'
    
    exception = RichAttributeError(instance, attribute_name)
    
    output = extract_attribute_error_fields(exception)
    
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    
    vampytest.assert_instance(output[0], type(instance))
    vampytest.assert_is(output[0], instance)
    
    vampytest.assert_instance(output[1], str)
    vampytest.assert_is(output[1], attribute_name)
