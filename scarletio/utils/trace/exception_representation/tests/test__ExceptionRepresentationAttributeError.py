import vampytest

from ....rich_attribute_error import AttributeError

from ...frame_proxy import FrameProxyVirtual

from ..exception_representation_attribute_error import ExceptionRepresentationAttributeError


class TestType0:
    __slots__ = ()
    
    hey = 'mister'
    komeiji = 'koishi'
    komachi = None


def _assert_fields_set(exception_representation):
    """
    Asserts whether every fields are set of the exception representation.
    
    Parameters
    ----------
    exception_representation : ``ExceptionRepresentationAttributeError``
        The exception representation to test.
    """
    vampytest.assert_instance(exception_representation, ExceptionRepresentationAttributeError)
    vampytest.assert_instance(exception_representation.attribute_name, str)
    vampytest.assert_instance(exception_representation.instance_type_name, str)
    vampytest.assert_instance(exception_representation.suggestion_attribute_exists_just_was_not_set, bool)
    vampytest.assert_instance(exception_representation.suggestion_familiar_attribute_names, list, nullable = True)
    vampytest.assert_instance(exception_representation.suggestion_matching_variable_exists, bool)
    vampytest.assert_instance(exception_representation.suggestion_variable_names_with_attribute, list, nullable = True)
    vampytest.assert_instance(exception_representation.type_name, str)


def test__ExceptionRepresentationAttributeError__new():
    """
    Tests whether ``ExceptionRepresentationAttributeError.__new__`` works as intended.
    """
    instance = TestType0()
    attribute_name = 'komeiji'
    
    frame = FrameProxyVirtual.from_fields(
        locals = {
            '__slots__': None,
            '__module__': None,
            'hey': 'mister',
            'komeiji': 'koishi',
            'komachi': None,
            **{name: None for name in dir(object)}
        }
    )
    
    exception = AttributeError(instance, attribute_name)
    
    exception_representation = ExceptionRepresentationAttributeError(exception, frame)
    _assert_fields_set(exception_representation)
    
    vampytest.assert_eq(exception_representation.attribute_name, attribute_name)
    vampytest.assert_eq(exception_representation.instance_type_name, TestType0.__name__)
    vampytest.assert_eq(exception_representation.suggestion_attribute_exists_just_was_not_set, True)
    vampytest.assert_eq(exception_representation.suggestion_matching_variable_exists, True)
    vampytest.assert_eq(exception_representation.suggestion_familiar_attribute_names, None)
    vampytest.assert_eq(exception_representation.suggestion_variable_names_with_attribute, None)
    vampytest.assert_eq(exception_representation.type_name, AttributeError.__name__)


def test__ExceptionRepresentationAttributeError__from_fields__no_fields():
    """
    Tests whether ``ExceptionRepresentationAttributeError.from_fields`` works as intended.
    
    Case: no fields given.
    """
    exception_representation = ExceptionRepresentationAttributeError.from_fields()
    _assert_fields_set(exception_representation)


def test__ExceptionRepresentationAttributeError__from_fields__all_fields():
    """
    Tests whether ``ExceptionRepresentationAttributeError.from_fields`` works as intended.
    
    Case: all fields given.
    """
    attribute_name = 'komeiji'
    instance_type_name = 'object'
    suggestion_attribute_exists_just_was_not_set = True
    suggestion_variable_names_with_attribute = ['hey', 'mister']
    suggestion_matching_variable_exists = False
    suggestion_familiar_attribute_names = ['koishi']
    type_name = AttributeError.__name__
    
    exception_representation = ExceptionRepresentationAttributeError.from_fields(
        attribute_name = attribute_name,
        instance_type_name = instance_type_name,
        suggestion_attribute_exists_just_was_not_set = suggestion_attribute_exists_just_was_not_set,
        suggestion_variable_names_with_attribute = suggestion_variable_names_with_attribute,
        suggestion_matching_variable_exists = suggestion_matching_variable_exists,
        suggestion_familiar_attribute_names = suggestion_familiar_attribute_names,
        type_name = type_name,
    )
    _assert_fields_set(exception_representation)
    
    vampytest.assert_eq(exception_representation.attribute_name, attribute_name)
    vampytest.assert_eq(exception_representation.instance_type_name, instance_type_name)
    vampytest.assert_eq(exception_representation.suggestion_attribute_exists_just_was_not_set, suggestion_attribute_exists_just_was_not_set)
    vampytest.assert_eq(exception_representation.suggestion_familiar_attribute_names, suggestion_familiar_attribute_names)
    vampytest.assert_eq(exception_representation.suggestion_matching_variable_exists, suggestion_matching_variable_exists)
    vampytest.assert_eq(exception_representation.suggestion_variable_names_with_attribute, suggestion_variable_names_with_attribute)
    vampytest.assert_eq(exception_representation.type_name, type_name)


def test__ExceptionRepresentationAttributeError__repr():
    """
    Tests whether ``ExceptionRepresentationAttributeError.__repr__`` works as intended.
    """
    attribute_name = 'komeiji'
    instance_type_name = 'object'
    suggestion_attribute_exists_just_was_not_set = True
    suggestion_variable_names_with_attribute = ['hey', 'mister']
    suggestion_matching_variable_exists = True
    suggestion_familiar_attribute_names = ['koishi']
    type_name = AttributeError.__name__
    
    exception_representation = ExceptionRepresentationAttributeError.from_fields(
        attribute_name = attribute_name,
        instance_type_name = instance_type_name,
        suggestion_attribute_exists_just_was_not_set = suggestion_attribute_exists_just_was_not_set,
        suggestion_variable_names_with_attribute = suggestion_variable_names_with_attribute,
        suggestion_matching_variable_exists = suggestion_matching_variable_exists,
        suggestion_familiar_attribute_names = suggestion_familiar_attribute_names,
        type_name = type_name,
    )
    
    output = repr(exception_representation)
    vampytest.assert_instance(output, str)
    
    vampytest.assert_in('attribute_name', output)
    vampytest.assert_in(repr(attribute_name), output)
    
    vampytest.assert_in('instance_type_name', output)
    vampytest.assert_in(repr(instance_type_name), output)
    
    vampytest.assert_in('suggestion_attribute_exists_just_was_not_set', output)
    vampytest.assert_in(repr(suggestion_attribute_exists_just_was_not_set), output)
    
    vampytest.assert_in('suggestion_variable_names_with_attribute', output)
    vampytest.assert_in(repr(suggestion_variable_names_with_attribute), output)
    
    vampytest.assert_in('suggestion_matching_variable_exists', output)
    vampytest.assert_in(repr(suggestion_matching_variable_exists), output)
    
    vampytest.assert_in('suggestion_familiar_attribute_names', output)
    vampytest.assert_in(repr(suggestion_familiar_attribute_names), output)
    
    vampytest.assert_in('type_name', output)
    vampytest.assert_in(repr(type_name), output)


def test__ExceptionRepresentationAttributeError__eq():
    """
    Tests whether ``ExceptionRepresentationAttributeError.__eq__`` works as intended.
    """
    attribute_name = 'komeiji'
    instance_type_name = 'object'
    suggestion_attribute_exists_just_was_not_set = True
    suggestion_variable_names_with_attribute = ['hey', 'mister']
    suggestion_matching_variable_exists = False
    suggestion_familiar_attribute_names = ['koishi']
    type_name = AttributeError.__name__
    
    keyword_parameters = {
        'attribute_name': attribute_name,
        'instance_type_name': instance_type_name,
        'suggestion_attribute_exists_just_was_not_set': suggestion_attribute_exists_just_was_not_set,
        'suggestion_variable_names_with_attribute': suggestion_variable_names_with_attribute,
        'suggestion_matching_variable_exists': suggestion_matching_variable_exists,
        'suggestion_familiar_attribute_names': suggestion_familiar_attribute_names,
        'type_name': type_name,
    }
    
    exception_representation = ExceptionRepresentationAttributeError.from_fields(**keyword_parameters)
    vampytest.assert_eq(exception_representation, exception_representation)
    vampytest.assert_ne(exception_representation, object())
    
    for field_name, field_value in (
        ('attribute_name', 'kaenbyou'),
        ('instance_type_name', 'int'),
        ('suggestion_attribute_exists_just_was_not_set', False),
        ('suggestion_variable_names_with_attribute', None),
        ('suggestion_matching_variable_exists', True),
        ('suggestion_familiar_attribute_names', None),
        ('type_name', TabError.__name__),
    ):
        test_exception_representation = ExceptionRepresentationAttributeError.from_fields(
                **{**keyword_parameters, field_name: field_value}
        )
        vampytest.assert_ne(exception_representation, test_exception_representation)
