import vampytest

from ..exception_representation_generic import ExceptionRepresentationGeneric


def _assert_fields_set(exception_representation):
    """
    Asserts whether every fields are set of the exception representation.
    
    Parameters
    ----------
    exception_representation : ``ExceptionRepresentationGeneric``
        The exception representation to test.
    """
    vampytest.assert_instance(exception_representation, ExceptionRepresentationGeneric)
    vampytest.assert_instance(exception_representation.representation, str)
    

def test__ExceptionRepresentationGeneric__new():
    """
    Tests whether ``ExceptionRepresentationGeneric.__new__`` works as intended.
    """
    exception = Exception()
    
    exception_representation = ExceptionRepresentationGeneric(exception, None)
    _assert_fields_set(exception_representation)
    
    vampytest.assert_eq(exception_representation.representation, 'Exception')


def test__ExceptionRepresentationGeneric__from_fields__no_fields():
    """
    Tests whether ``ExceptionRepresentationGeneric.from_fields`` works as intended.
    
    Case: No fields given.
    """
    exception_representation = ExceptionRepresentationGeneric.from_fields()
    _assert_fields_set(exception_representation)


def test__ExceptionRepresentationGeneric__from_fields__all_fields():
    """
    Tests whether ``ExceptionRepresentationGeneric.from_fields`` works as intended.
    
    Case: all fields given.
    """
    representation = 'Exception()'
    
    exception_representation = ExceptionRepresentationGeneric.from_fields(representation = representation)
    _assert_fields_set(exception_representation)
    
    vampytest.assert_eq(exception_representation.representation, representation)


def test__ExceptionRepresentationGeneric__repr():
    """
    Tests whether ``ExceptionRepresentationGeneric.__repr__`` works as intended.
    """
    representation = 'Exception()'
    
    exception_representation = ExceptionRepresentationGeneric.from_fields(representation = representation)
    
    output = repr(exception_representation)
    vampytest.assert_instance(output, str)
    
    vampytest.assert_in('representation', output)
    vampytest.assert_in(representation, output)


def test__ExceptionRepresentationGeneric__eq():
    """
    Tests whether ``ExceptionRepresentationGeneric.__eq__`` works as intended.
    """
    representation = 'Exception()'
    
    keyword_parameters = {
        'representation': representation,
    }
    
    exception_representation = ExceptionRepresentationGeneric.from_fields(**keyword_parameters)
    vampytest.assert_eq(exception_representation, exception_representation)
    vampytest.assert_ne(exception_representation, object())
    
    for field_name, field_value in (
        ('representation', 'Exception("hey mister")'),
    ):
        test_exception_representation = ExceptionRepresentationGeneric.from_fields(
            **{**keyword_parameters, field_name: field_value}
        )
        vampytest.assert_ne(exception_representation, test_exception_representation)
