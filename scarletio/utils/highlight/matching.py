__all__ = ()

from .constants import (
    ATTRIBUTE_ACCESS_OPERATOR, BUILTIN_CONSTANT_NAMES, BUILTIN_EXCEPTION_NAMES, BUILTIN_VARIABLE_NAMES, COMPLEX_RP,
    CONSOLE_PREFIX_RP, FLOAT_RP, FORMAT_STRING_POSTFIX_RP, IDENTIFIER_RP, INTEGER_BINARY_RP, INTEGER_DECIMAL_RP,
    INTEGER_HEXADECIMAL_RP, INTEGER_OCTAL_RP, KEYWORDS, KEYWORD_ELLIPSIS, MAGIC_FUNCTION_NAMES, MAGIC_VARIABLE_NAMES,
    OPERATOR_WORDS, OPERATOR_WP, PUNCTUATION_WP, SPACE_MATCH_RP, STRING_STARTER_RP
)
from .flags import (
    HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS, HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING,
    HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE, HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE,
    HIGHLIGHT_PARSER_FLAG_IN_STRING_BINARY, HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
    HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT_CODE, HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE,
    HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS, HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE,
    HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_STRING, HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS,
    HIGHLIGHT_PARSER_MASK_INHERITABLE
)
from .token_types import (
    TOKEN_TYPE_COMMENT, TOKEN_TYPE_IDENTIFIER_ATTRIBUTE, TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT,
    TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION, TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, TOKEN_TYPE_IDENTIFIER_KEYWORD,
    TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION, TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE, TOKEN_TYPE_IDENTIFIER_VARIABLE,
    TOKEN_TYPE_LINE_BREAK, TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, TOKEN_TYPE_NUMERIC_FLOAT,
    TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX, TOKEN_TYPE_NUMERIC_INTEGER_BINARY, TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL,
    TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL, TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, TOKEN_TYPE_SPACE,
    TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX, TOKEN_TYPE_SPECIAL_OPERATOR, TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE,
    TOKEN_TYPE_SPECIAL_OPERATOR_WORD, TOKEN_TYPE_SPECIAL_PUNCTUATION, TOKEN_TYPE_STRING, TOKEN_TYPE_STRING_BINARY,
    TOKEN_TYPE_STRING_UNICODE, TOKEN_TYPE_STRING_UNICODE_FORMAT, TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE,
    TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX
)


def _try_match_complex(context):
    """
    Tries to match a complex as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether a complex could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = COMPLEX_RP.match(line, index)
    if matched is None:
        return False
    
    content = matched.group(0)
    
    context.add_token(TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX, content)
    
    end = matched.end()
    context.set_line_character_index(end)
    return True


def _try_match_float(context):
    """
    Tries to match a float as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether a float could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = FLOAT_RP.match(line, index)
    if matched is None:
        return False
    
    content = matched.group(0)
    
    context.add_token(TOKEN_TYPE_NUMERIC_FLOAT, content)
    
    end = matched.end()
    context.set_line_character_index(end)
    return True


def _try_match_integer_hexadecimal(context):
    """
    Tries to match an hexadecimal integer as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether a hexadecimal integer could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = INTEGER_HEXADECIMAL_RP.match(line, index)
    if matched is None:
        return False
    
    content = matched.group(0)
    
    context.add_token(TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL, content)
    
    end = matched.end()
    context.set_line_character_index(end)
    return True


def _try_match_integer_decimal(context):
    """
    Tries to match an decimal integer as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether a decimal integer could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = INTEGER_DECIMAL_RP.match(line, index)
    if matched is None:
        return False
    
    content = matched.group(0)
    
    context.add_token(TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL, content)
    
    end = matched.end()
    context.set_line_character_index(end)
    return True


def _try_match_integer_octal(context):
    """
    Tries to match an octal integer as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether an octal integer could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = INTEGER_OCTAL_RP.match(line, index)
    if matched is None:
        return False
    
    content = matched.group(0)
    
    context.add_token(TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, content)
    
    end = matched.end()
    context.set_line_character_index(end)
    return True


def _try_match_integer_binary(context):
    """
    Tries to match a binary integer as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether an octal integer could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = INTEGER_BINARY_RP.match(line, index)
    if matched is None:
        return False
    
    content = matched.group(0)
    
    context.add_token(TOKEN_TYPE_NUMERIC_INTEGER_BINARY, content)
    
    end = matched.end()
    context.set_line_character_index(end)
    return True


def _try_match_identifier(context):
    """
    Tries to match an identifier as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether an identifier could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = IDENTIFIER_RP.match(line, index)
    if matched is None:
        return False
    
    content = matched.group(0)
    
    if content in BUILTIN_CONSTANT_NAMES:
        token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT
    elif content in KEYWORDS:
        token_type = TOKEN_TYPE_IDENTIFIER_KEYWORD
    elif content in OPERATOR_WORDS:
        token_type = TOKEN_TYPE_SPECIAL_OPERATOR_WORD
    else:
        last_token = context.get_last_related_token()
        if (last_token is not None) and (last_token.type == TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE):
            if content in MAGIC_FUNCTION_NAMES:
                token_type = TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION
            elif content in MAGIC_VARIABLE_NAMES:
                token_type = TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE
            else:
                token_type = TOKEN_TYPE_IDENTIFIER_ATTRIBUTE
        else:
            if content in BUILTIN_VARIABLE_NAMES:
                token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE
            elif content in BUILTIN_EXCEPTION_NAMES:
                token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION
            else:
                token_type = TOKEN_TYPE_IDENTIFIER_VARIABLE
    
    context.add_token(token_type, content)
    
    end = matched.end()
    context.set_line_character_index(end)
    return True


def _try_match_punctuation(context):
    """
    Tries to match a punctuation as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether a punctuation could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = PUNCTUATION_WP.match(line, index)
    if matched is None:
        return False
    
    context.add_token(TOKEN_TYPE_SPECIAL_PUNCTUATION, matched)
    
    end = index + len(matched)
    context.set_line_character_index(end)
    return True


def _try_match_operator(context):
    """
    Tries to match an operator as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether a operator could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = OPERATOR_WP.match(line, index)
    if matched is None:
        return False
    
    if matched == ATTRIBUTE_ACCESS_OPERATOR:
        token_type = TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE
    elif matched == KEYWORD_ELLIPSIS:
        token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT
    else:
        token_type = TOKEN_TYPE_SPECIAL_OPERATOR
    
    context.add_token(token_type, matched)
    
    end = index + len(matched)
    context.set_line_character_index(end)
    return True


def _try_match_space(context):
    """
    Tries to match some space as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether any space could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = SPACE_MATCH_RP.match(line, index)
    if matched is None:
        return False
    
    content = matched.group(0)
    
    context.add_token(TOKEN_TYPE_SPACE, content)
    
    end = matched.end()
    context.set_line_character_index(end)
    return True


def _try_match_comment(context):
    """
    Tries to match a comment as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether any comment could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    if (index >= len(line)) or (line[index] != '#'):
        return False
    
    # In later joined contents we might meet line break, so check that as well!
    line_break_index = line.find('\n')
    if line_break_index == -1:
        content = line[index:]
        context.add_token(TOKEN_TYPE_COMMENT, content)
        context.set_line_character_index(-1)
    else:
        content = line[index : line_break_index]
        context.add_token(TOKEN_TYPE_COMMENT, content)
        context.add_token(TOKEN_TYPE_LINE_BREAK, '\n')
        context.set_line_character_index(-1)
    
    # Mark the context as done if comments are not enabled
    _end_parsing_if_no_multi_line_code(context)
    return True


def _try_match_anything(context):
    """
    Matches anything as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether anything could be matched, so of course true.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    if (index >= len(line)):
        return False
    
    content = line[index]
    
    context.add_token(TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, content)
    context.set_line_character_index(index + 1)
    return True


def _try_match_empty_line(context):
    """
    Tries to match an empty line.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether an empty line could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    if index or line:
        return False
    
    context.set_line_character_index(-1)
    return True


def _try_match_console_prefix(context):
    """
    Tries to match a console prefix
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether console prefix could be matched.
    """
    index = context.get_line_character_index()
    if index != 0:
        return False
    
    line = context.get_line()
    
    matched = CONSOLE_PREFIX_RP.match(line)
    if matched is None:
        return False
    
    prefix, space = matched.groups()
    context.add_token(TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX, prefix)
    context.add_token(TOKEN_TYPE_SPACE, space)
    
    end = matched.end()
    context.set_line_character_index(end)
    return True


def _try_match_line_break(context):
    """
    Tries to match a line break.
    
    Parameters
    ----------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether a line break was matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    if (index >= len(line)) or (line[index] != '\n'):
        return False
    
    context.add_token(TOKEN_TYPE_LINE_BREAK, '\n')
    context.set_line_character_index(-1)
    
    # Mark the context as done if multi-line code is not enabled.
    _end_parsing_if_no_multi_line_code(context)
    return True


def _try_match_format_string_end(context):
    """
    Tries to match format string's end.
    
    Parameters
    ----------
    context : ``FormatStringParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether end was matched.
    """
    if not context.flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT:
        return False
    
    if (context.brace_nesting is not None):
        return False
    
    line = context.get_line()
    index = context.get_line_character_index()
    
    if (index >= len(line)) or (line[index] != '}'):
        return False
    
    context.add_token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}')
    context.set_line_character_index(index + 1)
    context.done = True
    return True


def _try_match_format_string_postfix(context):
    """
    Tries to match format string postfix.
    
    Parameters
    ----------
    context : ``FormatStringParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether postfix was matched.
    """
    if not context.flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT:
        return False
    
    if (context.brace_nesting is not None):
        return False
    
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = FORMAT_STRING_POSTFIX_RP.match(line, index)
    if matched is None:
        return False
    
    postfix = matched.group(1)
    end = matched.end()
    
    context.add_token(TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX, postfix)
    context.add_token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}')
    context.set_line_character_index(end)
    context.done = True
    return True


def _try_match_format_string_code(context):
    """
    tries to match format string code.
    
    Parameters
    ----------
    context : ``FormatStringParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether the format code was matched.
    """
    if not context.flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT:
        return False
    
    if (context.brace_nesting is not None):
        return False
    
    line = context.get_line()
    index = context.get_line_character_index()
    
    if (index >= len(line)) or (line[index] != ':'):
        return False
    
    context.add_token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':')
    context.set_line_character_index(index + 1)
    with context.enter(
        context.flags & HIGHLIGHT_PARSER_MASK_INHERITABLE |
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
        HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT |
        HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT_CODE
    ):
        _consume_format_string_until(context, '}')
        nested_flags = context.flags
    
    if (nested_flags & HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE):
        context.flags |= HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE
    
    context.done = True
    return True


def _try_match_string(context):
    """
    Tries to match a string as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether a string could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = STRING_STARTER_RP.match(line, index)
    if matched is None:
        return False
    
    content = matched.group(0)
    prefix, encapsulator = matched.groups()
    
    if context.flags & HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS:
        disable_flag = 0
    else:
        # Check whether the current encapsulator is allowed, leave if no.
        if encapsulator[0] == '\'':
            disable_flag = HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS
        else:
            disable_flag = HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS
        
        if context.flags & disable_flag:
            # We are in a nested string block, we end parsing right here.
            context.flags |= HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE
            context.done = True
            return True
    
    if prefix is None:
        token_type = TOKEN_TYPE_STRING_UNICODE
        string_parsing_flags = HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE
    elif 'b' in prefix:
        token_type = TOKEN_TYPE_STRING_BINARY
        string_parsing_flags = HIGHLIGHT_PARSER_FLAG_IN_STRING_BINARY
    elif 'f' in prefix:
        token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT
        string_parsing_flags = HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
    else:
        token_type = TOKEN_TYPE_STRING_UNICODE
        string_parsing_flags = HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE
    
    string_parsing_flags |= disable_flag
    
    if len(encapsulator) == 1:
        string_parsing_flags |= HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_STRING
    
    context.add_token(token_type, content)
    end = matched.end()
    context.set_line_character_index(end)
    
    with context.enter(
        (context.flags & HIGHLIGHT_PARSER_MASK_INHERITABLE) |
        string_parsing_flags
    ):
        if string_parsing_flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT:
            consumer = _consume_format_string_until
        else:
            consumer = _consume_string_until
        
        consumer(context, encapsulator)
    
    return True


def _get_string_token_type(context):
    """
    Gets the current string token type from the given context.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    token_type : `int`
    """
    flags = context.flags
    if flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_BINARY:
        token_type = TOKEN_TYPE_STRING_BINARY
    
    elif flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE:
        # Unicode can be a format string.
        if flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT_CODE:
            token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE
        
        elif flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT:
            token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT
        
        else:
            token_type = TOKEN_TYPE_STRING_UNICODE
    
    else:
        token_type = TOKEN_TYPE_STRING
    
    return token_type


def _end_parsing_if_no_multi_line_code(context):
    """
    Ends the current parsing if multi-line code is not allowed.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    end_parsing : `bool`
    """
    flags = context.flags
    if not flags & HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE:
        return False
    
    context.flags = flags | HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE
    context.done = True
    return True


def _end_parsing_if_no_multi_line_string(context):
    """
    Ends the current parsing if multi-line strings are not allowed
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    Returns
    -------
    end_parsing : `bool`
    """
    flags = context.flags
    if not flags & (HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_STRING | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT_CODE):
        return False
    
    context.flags = flags | HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE
    context.done = True
    return True


def _try_consume_string_end_of_line(context, line, unconsumed_since, index, line_length):
    """
    Tries to consume end of line while in a string.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    line : `str`
        Current line.
    
    unconsumed_since : `int`
        Index where consuming the line started.
    
    index : `int`
        The current index.
    
    line_length : `int`
        The line's total length.
    
    Returns
    -------
    end_parsing : `bool`
    """
    if index < line_length:
        return False
    
    if index > unconsumed_since:
        context.add_token(_get_string_token_type(context), line[unconsumed_since : index])
    
    context.set_line_character_index(-1)
    return True


def _try_consume_string_line_break(context, line, unconsumed_since, index, character):
    """
    Tries to consume line break while in a string.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    line : `str`
        Current line.
    
    unconsumed_since : `int`
        Index where consuming the line started.
    
    index : `int`
        The current index.
    
    character : `int`
        The line's current character.
    
    Returns
    -------
    end_parsing : `bool`
    """
    # end of line (with line break)
    if character != '\n':
        return False
    
    if index > unconsumed_since:
        context.add_token(_get_string_token_type(context), line[unconsumed_since : index])
    
    context.add_token(TOKEN_TYPE_LINE_BREAK, '\n')
    context.set_line_character_index(-1)
    return True


def _consume_string_until(context, end_string):
    """
    Consumes the string until the end string is met.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    end_string : `str`
        End string to match.
    """
    end_character = end_string[0]
    end_string_length = len(end_string)

    while True:
        if context.line_index >= len(context.lines):
            return
        
        line = context.get_line()
        line_length = len(line)
        index = context.get_line_character_index()
        unconsumed_since = index
        
        while True:
            # end of line (without line break)
            if _try_consume_string_end_of_line(context, line, unconsumed_since, index, line_length):
                if _end_parsing_if_no_multi_line_code(context) or _end_parsing_if_no_multi_line_string(context):
                    return
                
                break
            
            character = line[index]
            
            # end of line (with line break)
            if _try_consume_string_line_break(context, line, unconsumed_since, index, character):
                if _end_parsing_if_no_multi_line_code(context) or _end_parsing_if_no_multi_line_string(context):
                    return
                
                break
            
            # ignore escaped
            if (
                (character == '\\') and
                (
                    
                    (index + 1 < line_length) and
                    (line[index + 1] in ('\\', '\'', '"', 'a', 'b', 'f', 'n', 'r', 't', 'v'))
                )
            ):
                index += 2
                continue
            
            # match end
            if (
                (character == end_character) and
                (
                    (end_string_length == 1) or
                    (
                        (index + end_string_length <= line_length) and
                        (line[index : index + end_string_length] == end_string)
                    )
                )
            ):
                if index > unconsumed_since:
                    context.add_token(_get_string_token_type(context), line[unconsumed_since : index])
                
                if end_string == '}':
                    token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION
                else:
                    token_type = _get_string_token_type(context)
                
                context.add_token(token_type, end_string)
                context.set_line_character_index(index + end_string_length)
                return
            
            # Noting mentionable
            index += 1
            continue


def _consume_format_string_until(context, end_string):
    """
    Consumes format string until the end string is met.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    end_string : `str`
        End string to match.
    """
    end_character = end_string[0]
    end_string_length = len(end_string)
    
    while True:
        if context.line_index >= len(context.lines):
            return
        
        line = context.get_line()
        line_length = len(line)
        index = context.get_line_character_index()
        unconsumed_since = index
        
        while True:
            # end of line (without line break)
            if _try_consume_string_end_of_line(context, line, unconsumed_since, index, line_length):
                if _end_parsing_if_no_multi_line_code(context) or _end_parsing_if_no_multi_line_string(context):
                    return
                
                break
            
            character = line[index]
            
            # end of line (with line break)
            if _try_consume_string_line_break(context, line, unconsumed_since, index, character):
                if _end_parsing_if_no_multi_line_code(context) or _end_parsing_if_no_multi_line_string(context):
                    return
                
                break
            
            # ignore double `{` and `}`
            if (
                (character in ('{', '}')) and
                (
                    (index + 1 < line_length) and
                    (line[index + 1] == character)
                )
            ):
                index += 2
                continue
            
            # ignore escaped
            if (
                (character == '\\') and
                (
                    
                    (index + 1 < line_length) and
                    (line[index + 1] in ('\\', '\'', '"', 'a', 'b', 'f', 'n', 'r', 't', 'v'))
                )
            ):
                index += 2
                continue
            
            # match end
            if (
                (character == end_character) and
                (
                    (end_string_length == 1) or
                    (
                        (index + end_string_length <= line_length) and
                        (line[index : index + end_string_length] == end_string)
                    )
                )
            ):
                if index > unconsumed_since:
                    context.add_token(_get_string_token_type(context), line[unconsumed_since : index])
                
                if end_string == '}':
                    token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK
                else:
                    token_type = _get_string_token_type(context)
                
                context.add_token(token_type, end_string)
                context.set_line_character_index(index + end_string_length)
                return
            
            # are we entering a format string?
            if character == '{':
                if index > unconsumed_since:
                    context.add_token(_get_string_token_type(context), line[unconsumed_since : index])
                
                context.add_token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, character)
                context.set_line_character_index(index + 1)
                
                # are we entering a format string?
                with context.enter(
                    (context.flags & HIGHLIGHT_PARSER_MASK_INHERITABLE) |
                    (
                        0
                        if context.flags & HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS
                        else HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE
                    ) |
                    HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                    HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT |
                    HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING
                ):
                    _keep_python_parsing(context)
                    nested_flags = context.flags
                
                if nested_flags & HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE:
                    _end_parsing_if_no_multi_line_code(context)
                    return
                
                # end parsing if disabled flag is hit
                if nested_flags & HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE:
                    context.flags |= HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE
                    return
                
                break
            
            # Noting mentionable
            index += 1
            continue


PYTHON_PARSERS = (
    _try_match_empty_line,
    _try_match_console_prefix,
    _try_match_space,
    _try_match_format_string_end,
    _try_match_format_string_code,
    _try_match_format_string_postfix,
    _try_match_comment,
    _try_match_string,
    _try_match_complex,
    _try_match_float,
    _try_match_integer_hexadecimal,
    _try_match_integer_decimal,
    _try_match_integer_octal,
    _try_match_integer_binary,
    _try_match_identifier,
    _try_match_punctuation,
    _try_match_operator,
    _try_match_line_break,
    _try_match_anything,
)



def _keep_python_parsing(context):
    """
    Parses python code on the given context until its marked as done.
    
    Parameters
    ----------
    context : ``FormatStringParserContext``
        The context to use.
    """
    while not context.done:
        for parser in PYTHON_PARSERS:
            if parser(context):
                break
