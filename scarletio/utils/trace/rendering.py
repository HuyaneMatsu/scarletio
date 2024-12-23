__all__ = ()

from ..highlight import (
    HIGHLIGHT_TOKEN_TYPES, add_highlighted_part_into, add_highlighted_parts_into, iter_highlight_code_lines
)
from ..highlight.constants import (
    BUILTIN_EXCEPTION_NAMES, BUILTIN_VARIABLE_NAMES, MAGIC_FUNCTION_NAMES, MAGIC_VARIABLE_NAMES
)

from .exception_representation import (
    ExceptionRepresentationAttributeError, ExceptionRepresentationGeneric, ExceptionRepresentationSyntaxError
)


def render_exception_proxy_into(exception, highlighter, into):
    """
    Renders the given frame groups.
    
    Parameters
    ----------
    exception : ``ExceptionProxyBase``
        The frame groups to render.
    
    highlighter : `None`, ``HighlightFormatterContext``
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to render the representation into.
    
    Returns
    -------
    into : `list<str>`
    """
    into = render_frame_groups_into(exception.frame_groups, highlighter, into)
    into = render_exception_representation_into(exception.exception_representation, highlighter, into)
    return into


def render_frame_groups_into(frame_groups, highlighter, into):
    """
    Renders the given frame groups.
    
    Parameters
    ----------
    frame_groups : `None | list<FrameGroup>`
        The frame groups to render.
    
    highlighter : `None`, ``HighlightFormatterContext``
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to render the representation into.
    
    Returns
    -------
    into : `list<str>`
    """
    if (frame_groups is not None):
        for frame_group in frame_groups:
            into = render_frame_group_into(frame_group, highlighter, into)
    
    return into


def _build_frames_repeated_line(frame_count, repeat_count):
    """
    Builds the `frames repeated` line.
    
    Parameters
    ----------
    frame_count : `lint`
        The amount of repeated frames.
    repeat_count : `int`
        How much times the frames were repeated.
    
    Returns
    -------
    line : `str`
    """
    parts = []
    parts.append('[Following ')
    parts.append(str(frame_count))
    parts.append(' frame')
    parts.append('s were' if frame_count > 1 else ' was')
    parts.append(' repeated ')
    parts.append(str(repeat_count))
    parts.append(' times]')
    
    return ''.join(parts)


def render_frame_group_into(frame_group, highlighter, into):
    """
    Renders the frame group.
    
    Parameters
    ----------
    frame_group : ``FrameGroup``
        The frame group to render.
    
    highlighter : `None`, ``HighlightFormatterContext``
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to render the representation into.
    
    Returns
    -------
    into : `list<str>`
    """
    frames = frame_group.frames
    if frames is None:
        # Empty frame group, should not happen.
        return into
    
    repeat_count = frame_group.repeat_count
    if (repeat_count > 1):
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_FRAME_REPEAT,
            _build_frames_repeated_line(len(frames), repeat_count),
            highlighter,
            into,
        )
        into.append('\n')
    
    for frame in frames:
        into = render_frame_proxy_into(frame, highlighter, into)
    
    if (repeat_count > 1):
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_FRAME_REPEAT,
            '[End of repeated frames]',
            highlighter,
            into,
        )
        into.append('\n')
    
    return into


def render_frame_proxy_into(frame, highlighter, into):
    """
    Produces each part of the frame to render.
    
    This method is an iterable generator.
    
    Parameters
    ----------
    frame : ``FrameProxyBase``
        The frame to render.
    
    highlighter : `None | HighlightFormatterContext`
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to extend.
    
    Yields
    ------
    into : `list<str>`
    """
    lines = frame.lines
    
    add_highlighted_parts_into(
        _produce_file_location(frame.file_name, frame.line_index, frame.name, len(lines)),
        highlighter,
        into,
    )
    
    if lines:
        if (highlighter is None):
            for line in lines:
                into.append('    ')
                into.append(line)
                into.append('\n')
        
        else:
            into.extend(iter_highlight_code_lines([f'    {line}\n' for line in lines], highlighter))
    
    return into


def _produce_file_location(file_name, line_index, name, line_count):
    """
    Produces file location part and their tokens.
    
    Parameters
    ----------
    file_name : `str`
        Path of the respective file.
    line_index : int`
        The respective line's index.
    name : `str`
        The respective functions name.
    line_count : `int`
        How much lines is the expression at the location.
    
    Yields
    ------
    token_type : `int`
        The part's type.
    part : `str`
        Part to render
    """
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION, '  File '
    
    if file_name:
        file_name = file_name.replace('"', '\\"') # Add escapes into the file name
        yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION_PATH, f'"{file_name!s}"'
    else:
        yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION, 'unknown location'
    
    # if its multiple lines add `around` word
    if line_count > 1:
        yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION, ', around line '
    else:
        yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION, ', line '
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION_LINE_NUMBER, str(line_index + 1)
    
    if name:
        yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION, ', in '
        yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_LOCATION_NAME, name
    
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_LINEBREAK, '\n'


def add_trace_title_into(title, highlighter, into):
    """
    Adds trace title into the given list of strings.
    
    Parameters
    ----------
    title : `str`
        The title to add.
    
    highlighter : `None | HighlightFormatterContext`
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to extend.
    
    Returns
    -------
    into : `list<str>`
    """
    return add_highlighted_part_into(HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE, title, highlighter, into)


def _render_exception_representation_generic_into(exception_representation, highlighter, into):
    """
    Renders a generic exception's representation.
    
    Parameters
    ----------
    exception_representation : ``ExceptionRepresentationGeneric``
        The exception representation to render.
    
    highlighter : `None | HighlightFormatterContext`
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to extend.
    
    Returns
    -------
    into : `list<str>`
    """
    into = add_highlighted_part_into(
        HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
        exception_representation.representation,
        highlighter,
        into,
    )
    into.append('\n')
    return into


def _render_exception_representation_syntax_error_into(exception_representation, highlighter, into):
    """
    Renders a syntax error exception's representation.
    
    Parameters
    ----------
    exception_representation : ``ExceptionRepresentationSyntaxError``
        The exception representation to render.
    
    highlighter : `None | HighlightFormatterContext`
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to extend.
    
    Returns
    -------
    into : `list<str>`
    """
    # location
    into = add_highlighted_parts_into(
        _produce_file_location(exception_representation.file_name, exception_representation.line_index, '', 1),
        highlighter,
        into,
    )
    
    line = exception_representation.line
    if line:
        # Add line
        into.append('    ')
        if highlighter is None:
            into.append(line)
        else:
            into.extend(iter_highlight_code_lines([line], highlighter))
        into.append('\n')
        
        # Add pointer
        pointer_length = exception_representation.pointer_length
        if pointer_length:
            into.append(' ' * (4 + exception_representation.pointer_start_offset))
            into = add_highlighted_part_into(
                HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR, '^' * pointer_length, highlighter, into
            )
            into.append('\n')
    
    # type & message
    representation = exception_representation.type_name
    message = exception_representation.message
    if message:
        representation = f'{representation!s}: {message!s}'
    
    into = add_highlighted_part_into(
        HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR, representation, highlighter, into
    )
    into.append('\n')
    return into


def _produce_variable_name_only(variable_name):
    """
    Produces a variable name such as: `variable_name`.
    Also it them withing grace characters.
    
    Parameters
    ----------
    variable_name : `str`
        Variable name to produce.
    
    Yields
    ------
    token_type : `int`
        The part's type.
    part : `str`
        Part to render
    """
    if variable_name in BUILTIN_VARIABLE_NAMES:
        token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE
    elif variable_name in BUILTIN_EXCEPTION_NAMES:
        token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION
    else:
        token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_IDENTIFIER_VARIABLE
    
    yield token_type, variable_name


def _produce_attribute_name_only(attribute_name):
    """
    Produces a variable name such as: `.attribute_name`.
    
    Parameters
    ----------
    attribute_name : `str`
        The attribute name to produce.
    
    Yields
    ------
    token_type : `int`
        The part's type.
    part : `str`
        Part to render
    """
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, '.'
    
    if attribute_name in MAGIC_FUNCTION_NAMES:
        token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION
    elif attribute_name in MAGIC_VARIABLE_NAMES:
        token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE
    else:
        token_type = HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_IDENTIFIER_ATTRIBUTE
    
    yield token_type, attribute_name


def _produce_variable_attribute_access_only(variable_name, attribute_name):
    """
    Produces a variable attribute access such as: `variable_name.attribute_name`.
    
    Parameters
    ----------
    variable_name : `str`
        Variable name to produce.
    attribute_name : `str`
        The attribute name to produce.
    
    Yields
    ------
    token_type : `int`
        The part's type.
    part : `str`
        Part to render
    """
    yield from _produce_variable_name_only(variable_name)
    yield from _produce_attribute_name_only(attribute_name)


def _produce_grave_wrapped(producer):
    """
    Wraps the given `iterable` within grave characters.
    
    Parameters
    ----------
    producer : `iterable<(int, str)>`
        The producer to wrap between grave characters.
    
    Yields
    ------
    token_type : `int`
        The part's type.
    part : `str`
        Part to render
    """
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE_AFFIX, '`'
    yield from producer
    yield HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE_AFFIX, '`'


def _produce_variable_name(variable_name):
    """
    Produces a variable name such as: `variable_name`.
    Also it them withing grace characters.
    
    Parameters
    ----------
    variable_name : `str`
        Variable name to produce.
    
    Yields
    ------
    token_type : `int`
        The part's type.
    part : `str`
        Part to render
    """
    yield from _produce_grave_wrapped(_produce_variable_name_only(variable_name))


def _produce_attribute_name(attribute_name):
    """
    Produces a variable name such as: `.attribute_name`.
    Also wraps it withing grace characters.
    
    Parameters
    ----------
    attribute_name : `str`
        The attribute name to produce.
    
    Yields
    ------
    token_type : `int`
        The part's type.
    part : `str`
        Part to render
    """
    yield from _produce_grave_wrapped(_produce_attribute_name_only(attribute_name))


def _produce_variable_attribute_access(variable_name, attribute_name):
    """
    Produces a variable attribute access such as: `variable_name.attribute_name`.
    Also wraps them withing grace characters.
    
    Parameters
    ----------
    variable_name : `str`
        Variable name to produce.
    attribute_name : `str`
        The attribute name to produce.
    
    Yields
    ------
    token_type : `int`
        The part's type.
    part : `str`
        Part to render
    """
    yield from _produce_grave_wrapped(_produce_variable_attribute_access_only(variable_name, attribute_name))


def _render_exception_representation_attribute_error_into(exception_representation, highlighter, into):
    """
    Renders a syntax error exception's representation.
    
    Parameters
    ----------
    exception_representation : ``ExceptionRepresentationAttributeError``
        The exception representation to render.
    
    highlighter : `None | HighlightFormatterContext`
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to extend.
    
    Returns
    -------
    into : `list<str>`
    """
    attribute_name = exception_representation.attribute_name
    attribute_unset = exception_representation.suggestion_attribute_unset
    familiar_attribute_names = exception_representation.suggestion_familiar_attribute_names
    matching_variable_exists = exception_representation.suggestion_matching_variable_exists
    variable_names_with_attribute = exception_representation.suggestion_variable_names_with_attribute
    lines_rendered = 0
    
    into = add_highlighted_part_into(
        HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
        exception_representation.type_name,
        highlighter,
        into,
    )
    into = add_highlighted_part_into(
        HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
        ': ',
        highlighter,
        into,
    )
    
    into = add_highlighted_parts_into(
        _produce_grave_wrapped([
            (
                HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE_FILLING,
                exception_representation.instance_type_name,
            ),
        ]),
        highlighter,
        into,
    )
    
    into = add_highlighted_part_into(
        HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
        (' does not have its attribute ' if attribute_unset else ' has no attribute '),
        highlighter,
        into,
    )
    into = add_highlighted_parts_into(
        _produce_attribute_name(attribute_name),
        highlighter,
        into,
    )
    into = add_highlighted_part_into(
        HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
        ' set.' if attribute_unset else '.',
        highlighter,
        into,
    )
    
    into.append('\n')
    lines_rendered += 1
    
    if attribute_unset and matching_variable_exists:
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
            'Perhaps you meant to use the ',
            highlighter,
            into,
        )
        
        into = add_highlighted_parts_into(
            _produce_variable_name(attribute_name),
            highlighter,
            into,
        )
    
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
            ' variable instead?',
            highlighter,
            into,
        )
    
        into.append('\n')
        lines_rendered += 1
    
    if attribute_unset and (not matching_variable_exists):
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
            'Please review its constructors whether they are omitting setting it.',
            highlighter,
            into,
        )
        
        into.append('\n')
        lines_rendered += 1
    
    if (not attribute_unset) and matching_variable_exists:
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
            'Did you mean to use the ',
            highlighter,
            into,
        )
        
        into = add_highlighted_parts_into(
            _produce_variable_name(exception_representation.attribute_name),
            highlighter,
            into,
        )
    
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
            ' variable?',
            highlighter,
            into,
        )
        
        into.append('\n')
        lines_rendered += 1
    
    if (not attribute_unset) and (familiar_attribute_names is not None):
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
            ('Or perhaps any of the following attributes: ' if lines_rendered >= 2 else 'Did you mean any of: '),
            highlighter,
            into,
        )
        
        index = 0
        length = len(familiar_attribute_names)
        while True:
            name = familiar_attribute_names[index]
            into = add_highlighted_parts_into(_produce_attribute_name(name), highlighter, into)
            
            index += 1
            if index == length:
                break
            
            into = add_highlighted_part_into(
                HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
                ', ',
                highlighter,
                into,
            )
            continue
        
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
            '?',
            highlighter,
            into,
        )
        
        into.append('\n')
        lines_rendered += 1

    if (familiar_attribute_names is None) and  (variable_names_with_attribute is not None):
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
            ('Or perhaps you meant to do any of: ' if lines_rendered >= 2 else 'Did you mean to do any of: '),
            highlighter,
            into,
        )
        
        index = 0
        length = len(variable_names_with_attribute)
        while True:
            name = variable_names_with_attribute[index]
            into = add_highlighted_parts_into(
                _produce_variable_attribute_access(name, attribute_name), highlighter, into
            )
            
            index += 1
            if index == length:
                break
            
            into = add_highlighted_part_into(
                HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
                ', ',
                highlighter,
                into,
            )
            continue
        
        into = add_highlighted_part_into(
            HIGHLIGHT_TOKEN_TYPES.TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR,
            '?',
            highlighter,
            into,
        )
        
        into.append('\n')
        lines_rendered += 1
    
    return into


EXCEPTION_REPRESENTATION_RENDERERS = {
    ExceptionRepresentationAttributeError: _render_exception_representation_attribute_error_into,
    ExceptionRepresentationGeneric: _render_exception_representation_generic_into,
    ExceptionRepresentationSyntaxError: _render_exception_representation_syntax_error_into,
}


def render_exception_representation_into(exception_representation, highlighter, into):
    """
    Renders an exception's representation.
    
    Parameters
    ----------
    exception_representation : `None | ExceptionRepresentationBase`
        The exception representation to render.
    
    highlighter : `None | HighlightFormatterContext`
        Stores how the output should be highlighted.
    
    into : `list<str>`
        The list of strings to extend.
    
    Returns
    -------
    into : `list<str>`
    """
    renderer = EXCEPTION_REPRESENTATION_RENDERERS.get(type(exception_representation), None)
    if (renderer is not None):
        into = renderer(exception_representation, highlighter, into)
    
    return into
