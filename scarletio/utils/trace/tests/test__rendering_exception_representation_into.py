import vampytest

from ...highlight import DEFAULT_ANSI_HIGHLIGHTER, get_highlight_streamer, iter_split_ansi_format_codes

from ..exception_representation import (
    ExceptionRepresentationAttributeError, ExceptionRepresentationGeneric, ExceptionRepresentationSyntaxError
)
from ..rendering import (
    _render_exception_representation_attribute_error_into, _render_exception_representation_generic_into,
    _render_exception_representation_syntax_error_into, render_exception_representation_into
)


def test__render_exception_representation_generic_into__no_highlight():
    """
    Tests whether ``_render_exception_representation_generic_into`` works as intended.
    
    Case: No highlight.
    """
    representation = 'Exception(\'hey mister\')'
    expected_output = representation + '\n'
    
    exception_representation = ExceptionRepresentationGeneric.from_fields(
        representation = representation
    )
    
    highlight_streamer = get_highlight_streamer(None)
    output = _render_exception_representation_generic_into(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, expected_output)


def test__render_exception_representation_generic_into__with_highlight():
    """
    Tests whether ``_render_exception_representation_generic_into`` works as intended.
    
    Case: With highlight.
    """
    representation = 'Exception(\'hey mister\')'
    expected_output = representation + '\n'
    
    exception_representation = ExceptionRepresentationGeneric.from_fields(
        representation = representation
    )
    
    highlight_streamer = get_highlight_streamer(DEFAULT_ANSI_HIGHLIGHTER)
    output = _render_exception_representation_generic_into(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    split = [*iter_split_ansi_format_codes(output_string)]
    vampytest.assert_true(any(item[0] for item in split))
    
    output_string = ''.join([item[1] for item in split if not item[0]])
    vampytest.assert_eq(output_string, expected_output)


def test__render_exception_representation_attribute_error_into__no_highlight():
    """
    Tests whether ``_render_exception_representation_attribute_error_into`` works as intended.
    
    Case: No highlight.
    """
    type_name = AttributeError.__name__
    instance_type_name = 'Handler'
    attribute_name = 'cuddle'
    suggestion_familiar_attribute_names = ['hug', 'pat']
    
    expected_output = (
        'AttributeError: `Handler` has no attribute `.cuddle`.\n'
        'Did you mean any of: `.hug`, `.pat`?\n'
    )
    
    exception_representation = ExceptionRepresentationAttributeError.from_fields(
        type_name = type_name,
        instance_type_name = instance_type_name,
        attribute_name = attribute_name,
        suggestion_familiar_attribute_names = suggestion_familiar_attribute_names,
    )
    
    highlight_streamer = get_highlight_streamer(None)
    output = _render_exception_representation_attribute_error_into(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, expected_output)


def test__render_exception_representation_attribute_error_into__with_highlight():
    """
    Tests whether ``_render_exception_representation_attribute_error_into`` works as intended.
    
    Case: With highlight.
    """
    type_name = AttributeError.__name__
    instance_type_name = 'Handler'
    attribute_name = 'cuddle'
    suggestion_familiar_attribute_names = ['hug', 'pat']
    
    expected_output = (
        'AttributeError: `Handler` has no attribute `.cuddle`.\n'
        'Did you mean any of: `.hug`, `.pat`?\n'
    )
    
    exception_representation = ExceptionRepresentationAttributeError.from_fields(
        type_name = type_name,
        instance_type_name = instance_type_name,
        attribute_name = attribute_name,
        suggestion_familiar_attribute_names = suggestion_familiar_attribute_names,
    )
    
    highlight_streamer = get_highlight_streamer(DEFAULT_ANSI_HIGHLIGHTER)
    output = _render_exception_representation_attribute_error_into(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    split = [*iter_split_ansi_format_codes(output_string)]
    vampytest.assert_true(any(item[0] for item in split))
    
    output_string = ''.join([item[1] for item in split if not item[0]])
    vampytest.assert_eq(output_string, expected_output)


def test__render_exception_representation_attribute_error_into__frame_with_same_variable():
    """
    Tests whether ``_render_exception_representation_attribute_error_into`` works as intended.
    
    Case: Frame with same variable.
    """
    type_name = AttributeError.__name__
    instance_type_name = 'Handler'
    attribute_name = 'cuddle'
    suggestion_familiar_attribute_names = ['hug', 'pat']
    suggestion_matching_variable_exists = True
    
    expected_output = (
        'AttributeError: `Handler` has no attribute `.cuddle`.\n'
        'Did you mean to use the `cuddle` variable?\n'
        'Or perhaps any of the following attributes: `.hug`, `.pat`?\n'
    )
    
    exception_representation = ExceptionRepresentationAttributeError.from_fields(
        type_name = type_name,
        instance_type_name = instance_type_name,
        attribute_name = attribute_name,
        suggestion_familiar_attribute_names = suggestion_familiar_attribute_names,
        suggestion_matching_variable_exists = suggestion_matching_variable_exists,
    )
    
    highlight_streamer = get_highlight_streamer(None)
    output = _render_exception_representation_attribute_error_into(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, expected_output)


def test__render_exception_representation_attribute_error_into__unset_attribute():
    """
    Tests whether ``_render_exception_representation_attribute_error_into`` works as intended.
    
    Case: Unset variable.
    """
    type_name = AttributeError.__name__
    instance_type_name = 'Handler'
    attribute_name = 'cuddle'
    suggestion_familiar_attribute_names = ['hug', 'pat']
    suggestion_attribute_unset = True
    
    expected_output = (
        'AttributeError: `Handler` does not have its attribute `.cuddle` set.\n'
        'Please review its constructors whether they are omitting setting it.\n'
    )
    
    exception_representation = ExceptionRepresentationAttributeError.from_fields(
        type_name = type_name,
        instance_type_name = instance_type_name,
        attribute_name = attribute_name,
        suggestion_familiar_attribute_names = suggestion_familiar_attribute_names,
        suggestion_attribute_unset = suggestion_attribute_unset,
    )
    
    highlight_streamer = get_highlight_streamer(None)
    output = _render_exception_representation_attribute_error_into(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, expected_output)


def test__render_exception_representation_attribute_error_into__other_variable_with_attribute():
    """
    Tests whether ``_render_exception_representation_attribute_error_into`` works as intended.
    
    Case: Other variable has the same attribute.
    """
    type_name = AttributeError.__name__
    instance_type_name = 'Handler'
    attribute_name = 'cuddle'
    suggestion_familiar_attribute_names = None
    suggestion_variable_names_with_attribute = ['hug', 'kiss']
    
    expected_output = (
        'AttributeError: `Handler` has no attribute `.cuddle`.\n'
        'Did you mean to do any of: `hug.cuddle`, `kiss.cuddle`?\n'
    )
    
    exception_representation = ExceptionRepresentationAttributeError.from_fields(
        type_name = type_name,
        instance_type_name = instance_type_name,
        attribute_name = attribute_name,
        suggestion_familiar_attribute_names = suggestion_familiar_attribute_names,
        suggestion_variable_names_with_attribute = suggestion_variable_names_with_attribute,
    )
    
    highlight_streamer = get_highlight_streamer(None)
    output = _render_exception_representation_attribute_error_into(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, expected_output)


def test__render_exception_representation_syntax_error_into__no_highlight():
    """
    Tests whether ``_render_exception_representation_syntax_error_into`` works as intended.
    
    Case: No highlight.
    """
    file_name = '<string>'
    line = 'from as as'
    line_index = 0
    message = 'invalid syntax'
    pointer_length = 4
    pointer_start_offset = 0
    type_name = SyntaxError.__name__
    
    expected_output = (
        '  File "<string>", line 1\n'
        '    from as as\n'
        '    ^^^^\n'
        'SyntaxError: invalid syntax\n'
    )
    
    exception_representation = ExceptionRepresentationSyntaxError.from_fields(
        file_name = file_name,
        line = line,
        line_index = line_index,
        message = message,
        pointer_length = pointer_length,
        pointer_start_offset = pointer_start_offset,
        type_name = type_name,
    )
    
    highlight_streamer = get_highlight_streamer(None)
    output = _render_exception_representation_syntax_error_into(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    vampytest.assert_eq(output_string, expected_output)



def test__render_exception_representation_syntax_error_into__with_highlight():
    """
    Tests whether ``_render_exception_representation_syntax_error_into`` works as intended.
    
    Case: No highlight.
    """
    file_name = '<string>'
    line = 'from as as'
    line_index = 0
    message = 'invalid syntax'
    pointer_length = 4
    pointer_start_offset = 0
    type_name = SyntaxError.__name__
    
    expected_output = (
        '  File "<string>", line 1\n'
        '    from as as\n'
        '    ^^^^\n'
        'SyntaxError: invalid syntax\n'
    )
    
    exception_representation = ExceptionRepresentationSyntaxError.from_fields(
        file_name = file_name,
        line = line,
        line_index = line_index,
        message = message,
        pointer_length = pointer_length,
        pointer_start_offset = pointer_start_offset,
        type_name = type_name,
    )
    
    highlight_streamer = get_highlight_streamer(DEFAULT_ANSI_HIGHLIGHTER)
    output = _render_exception_representation_syntax_error_into(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    for element in output:
        vampytest.assert_instance(element, str)
    
    output_string = ''.join(output)
    split = [*iter_split_ansi_format_codes(output_string)]
    vampytest.assert_true(any(item[0] for item in split))
    
    output_string = ''.join([item[1] for item in split if not item[0]])
    vampytest.assert_eq(output_string, expected_output)


def test__render_exception_representation_into__hit():
    """
    Tests whether ``render_exception_representation_into`` works as intended.
    
    Case: renderer hit.
    """
    hit = False
    
    def _renderer(exception_representation, highlight_streamer, into):
        nonlocal hit
        hit = True
        return into
    
    
    mock_renderers = {
        ExceptionRepresentationGeneric: _renderer,
    }
    
    mocked = vampytest.mock_globals(
        render_exception_representation_into,
        EXCEPTION_REPRESENTATION_RENDERERS = mock_renderers
    )
    
    exception_representation = ExceptionRepresentationGeneric.from_fields(
        representation = 'hey mister'
    )
    
    highlight_streamer = get_highlight_streamer(None)
    output = mocked(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    vampytest.assert_true(hit)


def test__render_exception_representation_into__miss():
    """
    Tests whether ``render_exception_representation_into`` works as intended.
    
    Case: renderer miss.
    """
    hit = False
    
    def _renderer(exception_representation, highlight_streamer, into):
        nonlocal hit
        hit = True
        return into
    
    
    mock_renderers = {
        ExceptionRepresentationGeneric: _renderer,
    }
    
    mocked = vampytest.mock_globals(
        render_exception_representation_into,
        EXCEPTION_REPRESENTATION_RENDERERS = mock_renderers
    )
    
    exception_representation = None
    
    highlight_streamer = get_highlight_streamer(None)
    output = mocked(exception_representation, highlight_streamer, [])
    output.extend(highlight_streamer.asend(None))
    
    vampytest.assert_instance(output, list)
    vampytest.assert_false(hit)
