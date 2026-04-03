import vampytest

from ..exception_representation_syntax_error import ExceptionRepresentationSyntaxError


def _assert_fields_set(exception_representation):
    """
    Asserts whether every fields are set of the exception representation.
    
    Parameters
    ----------
    exception_representation : ``ExceptionRepresentationSyntaxError``
        The exception representation to test.
    """
    vampytest.assert_instance(exception_representation, ExceptionRepresentationSyntaxError)
    vampytest.assert_instance(exception_representation.file_name, str)
    vampytest.assert_instance(exception_representation.line, str)
    vampytest.assert_instance(exception_representation.line_index, int)
    vampytest.assert_instance(exception_representation.message, str)
    vampytest.assert_instance(exception_representation.pointer_start_offset, int)
    vampytest.assert_instance(exception_representation.pointer_length, int)
    vampytest.assert_instance(exception_representation.type_name, str)


def test__ExceptionRepresentationSyntaxError__new():
    """
    Tests whether ``ExceptionRepresentationSyntaxError.__new__`` works as intended.
    """
    file_name = '<string>'
    line = 'from as as'
    line_index = 0
    message = 'invalid syntax'
    pointer_length = 4
    pointer_start_offset = 0
    type_name = SyntaxError.__name__
    spaces_before = 2
    
    exception = SyntaxError()
    exception.args = (
        'invalid syntax',
        (
            file_name,
            line_index + 1,
            pointer_start_offset + 1 + spaces_before,
            ' ' * spaces_before + line,
            line_index + 1,
            pointer_start_offset + 1 + pointer_length + spaces_before,
        ),
    )
    
    exception_representation = ExceptionRepresentationSyntaxError(exception, None)
    _assert_fields_set(exception_representation)
    
    vampytest.assert_eq(exception_representation.file_name, file_name)
    vampytest.assert_eq(exception_representation.line, line)
    vampytest.assert_eq(exception_representation.line_index, line_index)
    vampytest.assert_eq(exception_representation.message, message)
    vampytest.assert_eq(exception_representation.pointer_start_offset, pointer_start_offset)
    vampytest.assert_eq(exception_representation.pointer_length, pointer_length)
    vampytest.assert_eq(exception_representation.type_name, type_name)


def test__ExceptionRepresentationSyntaxError__from_fields__no_fields():
    """
    Tests whether ``ExceptionRepresentationSyntaxError.from_fields`` works as intended.
    
    Case: no fields given.
    """
    exception_representation = ExceptionRepresentationSyntaxError.from_fields()
    _assert_fields_set(exception_representation)


def test__ExceptionRepresentationSyntaxError__from_fields__all_fields():
    """
    Tests whether ``ExceptionRepresentationSyntaxError.from_fields`` works as intended.
    
    Case: all fields given.
    """
    file_name = '<string>'
    line = 'from as as'
    line_index = 0
    message = 'invalid syntax'
    pointer_length = 4
    pointer_start_offset = 0
    type_name = SyntaxError.__name__
    
    exception_representation = ExceptionRepresentationSyntaxError.from_fields(
        file_name = file_name,
        line = line,
        line_index = line_index,
        message = message,
        pointer_length = pointer_length,
        pointer_start_offset = pointer_start_offset,
        type_name = type_name,
    )
    _assert_fields_set(exception_representation)
    
    vampytest.assert_eq(exception_representation.file_name, file_name)
    vampytest.assert_eq(exception_representation.line, line)
    vampytest.assert_eq(exception_representation.line_index, line_index)
    vampytest.assert_eq(exception_representation.message, message)
    vampytest.assert_eq(exception_representation.pointer_start_offset, pointer_start_offset)
    vampytest.assert_eq(exception_representation.pointer_length, pointer_length)
    vampytest.assert_eq(exception_representation.type_name, type_name)


def test__ExceptionRepresentationSyntaxError__repr():
    """
    Tests whether ``ExceptionRepresentationSyntaxError.__repr__`` works as intended.
    """
    file_name = '<string>'
    line = 'from as as'
    line_index = 0
    message = 'invalid syntax'
    pointer_length = 4
    pointer_start_offset = 0
    type_name = SyntaxError.__name__
    
    exception_representation = ExceptionRepresentationSyntaxError.from_fields(
        file_name = file_name,
        line = line,
        line_index = line_index,
        message = message,
        pointer_length = pointer_length,
        pointer_start_offset = pointer_start_offset,
        type_name = type_name,
    )
    
    output = repr(exception_representation)
    vampytest.assert_instance(output, str)
    
    vampytest.assert_in('file_name', output)
    vampytest.assert_in(repr(file_name), output)
    
    vampytest.assert_in('line', output)
    vampytest.assert_in(repr(line), output)
    
    vampytest.assert_in('line_index', output)
    vampytest.assert_in(repr(line_index), output)
    
    vampytest.assert_in('message', output)
    vampytest.assert_in(repr(message), output)
    
    vampytest.assert_in('pointer_length', output)
    vampytest.assert_in(repr(pointer_length), output)
    
    vampytest.assert_in('pointer_start_offset', output)
    vampytest.assert_in(repr(pointer_start_offset), output)
    
    vampytest.assert_in('type_name', output)
    vampytest.assert_in(repr(type_name), output)


def test__ExceptionRepresentationSyntaxError__eq():
    """
    Tests whether ``ExceptionRepresentationSyntaxError.__eq__`` works as intended.
    """
    file_name = '<string>'
    line = 'from as as'
    line_index = 0
    message = 'invalid syntax'
    pointer_length = 4
    pointer_start_offset = 0
    type_name = SyntaxError.__name__
    
    keyword_parameters = {
        'file_name': file_name,
        'line': line,
        'line_index': line_index,
        'message': message,
        'pointer_length': pointer_length,
        'pointer_start_offset': pointer_start_offset,
        'type_name': type_name,
    }
    
    exception_representation = ExceptionRepresentationSyntaxError.from_fields(**keyword_parameters)
    vampytest.assert_eq(exception_representation, exception_representation)
    vampytest.assert_ne(exception_representation, object())
    
    for field_name, field_value in (
        ('file_name', '<module>'),
        ('line', 'ass ass in'),
        ('line_index', 10),
        ('message', 'valid syntax'),
        ('pointer_length', 1),
        ('pointer_start_offset', 4),
        ('type_name', TabError.__name__),
    ):
        test_exception_representation = ExceptionRepresentationSyntaxError.from_fields(
                **{**keyword_parameters, field_name: field_value}
        )
        vampytest.assert_ne(exception_representation, test_exception_representation)
