__all__ = ()

from .constants import (
    ATTRIBUTE_ACCESS_OPERATOR, BUILTIN_CONSTANT_NAMES, BUILTIN_EXCEPTION_NAMES, BUILTIN_VARIABLE_NAMES, COMPLEX_RP,
    CONSOLE_PREFIX_RP, FLOAT_RP, FORMAT_STRING_POSTFIX_RP, IDENTIFIER_RP, INTEGER_BINARY_RP, INTEGER_DECIMAL_RP,
    INTEGER_HEXADECIMAL_RP, INTEGER_OCTAL_RP, KEYWORDS, KEYWORD_ELLIPSIS, MAGIC_FUNCTION_NAMES, MAGIC_VARIABLE_NAMES,
    OPERATOR_WORDS, OPERATOR_WP, PUNCTUATION_WP, SPACE_MATCH_RP, STRING_STARTER_RP
)
from .flags import (
    HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS, HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE,
    HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE, HIGHLIGHT_PARSER_FLAG_IN_STRING_BINARY,
    HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT, HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT_CODE,
    HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE, HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS,
    HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE, HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_STRING,
    HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS, HIGHLIGHT_PARSER_MASK_INHERITABLE
)
from .token_types import (
    TOKEN_TYPE_COMMENT, TOKEN_TYPE_IDENTIFIER_ATTRIBUTE, TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT,
    TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION, TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, TOKEN_TYPE_IDENTIFIER_KEYWORD,
    TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION, TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE, TOKEN_TYPE_IDENTIFIER_VARIABLE,
    TOKEN_TYPE_LINE_BREAK, TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, TOKEN_TYPE_NUMERIC_FLOAT,
    TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX, TOKEN_TYPE_NUMERIC_INTEGER_BINARY, TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL,
    TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL, TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, TOKEN_TYPE_SPACE,
    TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX, TOKEN_TYPE_SPECIAL_OPERATOR, TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE,
    TOKEN_TYPE_SPECIAL_OPERATOR_WORD, TOKEN_TYPE_SPECIAL_PUNCTUATION, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE,
    TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE,
    TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_CLOSE,
    TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_OPEN, TOKEN_TYPE_SPECIAL_PUNCTUATION_COLON,
    TOKEN_TYPE_SPECIAL_PUNCTUATION_COMMA, TOKEN_TYPE_SPECIAL_PUNCTUATION_SEMI_COLON, TOKEN_TYPE_STRING,
    TOKEN_TYPE_STRING_BINARY, TOKEN_TYPE_STRING_BINARY_SPECIAL_PREFIX, TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_CLOSE,
    TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN, TOKEN_TYPE_STRING_FORMAT_CODE,
    TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
    TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, TOKEN_TYPE_STRING_FORMAT_POSTFIX, TOKEN_TYPE_STRING_UNICODE,
    TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE,
    TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN
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
    matched = COMPLEX_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    context.add_token(TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX, matched.end() - matched.start())
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
    matched = FLOAT_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    context.add_token(TOKEN_TYPE_NUMERIC_FLOAT, matched.end() - matched.start())
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
    matched = INTEGER_HEXADECIMAL_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    context.add_token(TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL, matched.end() - matched.start())
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
    matched = INTEGER_DECIMAL_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    context.add_token(TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL, matched.end() - matched.start())
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
    matched = INTEGER_OCTAL_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    context.add_token(TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, matched.end() - matched.start())
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
    matched = INTEGER_BINARY_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    context.add_token(TOKEN_TYPE_NUMERIC_INTEGER_BINARY, matched.end() - matched.start())
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
    matched = IDENTIFIER_RP.match(context.content, context.content_character_index)
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
    
    context.add_token(token_type, len(content))
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
    punctuation = PUNCTUATION_WP.match(context.content, context.content_character_index)
    if punctuation is None:
        return False
    
    if punctuation == '(':
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN
    elif punctuation == '{':
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN
    elif punctuation == '[':
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_OPEN
    elif punctuation == ')':
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_CLOSE
    elif punctuation == '}':
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE
    elif punctuation == ']':
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_SQUARE_CLOSE
    elif punctuation == ':':
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_COLON
    elif punctuation == ',':
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_COMMA
    elif punctuation == ';':
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION_SEMI_COLON
    else:
        # should not happen
        token_type = TOKEN_TYPE_SPECIAL_PUNCTUATION
    
    context.add_token(token_type, len(punctuation))
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
    matched = OPERATOR_WP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    if matched == ATTRIBUTE_ACCESS_OPERATOR:
        token_type = TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE
    elif matched == KEYWORD_ELLIPSIS:
        token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT
    else:
        token_type = TOKEN_TYPE_SPECIAL_OPERATOR
    
    context.add_token(token_type, len(matched))
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
    matched = SPACE_MATCH_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    context.add_token(TOKEN_TYPE_SPACE, matched.end() - matched.start())
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
    content = context.content
    content_character_index = context.content_character_index
    content_length = context.content_length
    
    if content_character_index >= content_length or content[content_character_index] != '#':
        return False
    
    # In later joined contents we might meet line break, so check that as well!
    line_break_index = content.find('\n', content_character_index)
    if line_break_index == -1:
        context.add_token(TOKEN_TYPE_COMMENT, content_length - content_character_index)
    
    else:
        context.add_token(TOKEN_TYPE_COMMENT, line_break_index - content_character_index)
    
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
    if context.content_character_index >= context.content_length:
        return False
    
    context.add_token(TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, 1)
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
    if context.line_character_index != 0:
        return False
    
    matched = CONSOLE_PREFIX_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    prefix, space = matched.groups()
    context.add_token(TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX, len(prefix))
    context.add_token(TOKEN_TYPE_SPACE, len(space))
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
    content = context.content
    content_character_index = context.content_character_index
    content_length = context.content_length
    
    if content_character_index >= content_length or content[content_character_index] != '\n':
        return False
    
    if not context.flags & HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE:
        context.add_token(TOKEN_TYPE_LINE_BREAK, 1)
    
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
    
    brace_nesting = context.brace_nesting
    if (brace_nesting is not None) and (brace_nesting[-1] != TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN):
        return False
    
    content = context.content
    content_character_index = context.content_character_index
    content_length = context.content_length
    
    if content_character_index >= content_length or content[content_character_index] != '}':
        return False
    
    context.add_token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, 1)
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
    
    brace_nesting = context.brace_nesting
    if (brace_nesting is not None) and (brace_nesting[-1] != TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN):
        return False
    
    matched = FORMAT_STRING_POSTFIX_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
    context.add_token(TOKEN_TYPE_STRING_FORMAT_POSTFIX, matched.end(1) - matched.start(1))
    context.add_token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, 1)
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
    
    brace_nesting = context.brace_nesting
    if (brace_nesting is not None) and (brace_nesting[-1] != TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN):
        return False
    
    content = context.content
    content_character_index = context.content_character_index
    content_length = context.content_length
    
    if content_character_index >= content_length or content[content_character_index] != ':':
        return False
    
    context.add_token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, 1)
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
    matched = STRING_STARTER_RP.match(context.content, context.content_character_index)
    if matched is None:
        return False
    
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
        prefix_token_type = TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX
        encapsulator_token_type = TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN
        string_parsing_flags = HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE
    elif 'b' in prefix:
        prefix_token_type = TOKEN_TYPE_STRING_BINARY_SPECIAL_PREFIX
        encapsulator_token_type = TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN
        string_parsing_flags = HIGHLIGHT_PARSER_FLAG_IN_STRING_BINARY
    elif 'f' in prefix:
        prefix_token_type = TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX
        encapsulator_token_type = TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN
        string_parsing_flags = HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
    else:
        prefix_token_type = TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX
        encapsulator_token_type = TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN
        string_parsing_flags = HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE
    
    string_parsing_flags |= disable_flag
    
    if len(encapsulator) == 1:
        string_parsing_flags |= HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_STRING
    
    if (prefix is not None):
        context.add_token(prefix_token_type, len(prefix))
    context.add_token(encapsulator_token_type, len(encapsulator))
    
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


def _get_string_token_type(context, end_string):
    """
    Gets the current string token type from the given context.
    
    Parameter
    ---------
    context : ``HighlightParserContext``
        The context to use.
    
    end_string : `None | str`
        Whether the string is ending and with what.
    
    Returns
    -------
    token_type : `int`
    """
    if (end_string is not None) and (end_string == '}'):
        return TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE
    
    flags = context.flags
    if flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_BINARY:
        if (end_string is not None):
            token_type = TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_CLOSE
        else:
            token_type = TOKEN_TYPE_STRING_BINARY
    
    elif flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE:
        if (end_string is not None):
            token_type = TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE
        
        else:
            # Unicode can be a format string.
            if flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT_CODE:
                token_type = TOKEN_TYPE_STRING_FORMAT_CODE
            
            elif flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT:
                token_type = TOKEN_TYPE_STRING_UNICODE
            
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
    if not (
        (flags & HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_STRING) or
        (
            (not flags & HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS) and
            (flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT_CODE)
        )
    ):
        return False
    
    context.flags = flags | HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE
    context.done = True
    return True


def _try_consume_string_till_end_of_line(context, unconsumed_since, index, end_string):
    """
    Tries to consume till the end of the line.
    
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
    
    end_string : `None | str`
        Whether the string is ending and with what.
    
    Returns
    -------
    action : `0`
    """
    while True:
        if index >= context.content_length:
            add_line_break = False
            break
        
        character = context.content[index]
        if character == '\n':
            add_line_break = True
            break
        
        return 0
    
    
    if index > unconsumed_since:
        context.add_token(_get_string_token_type(context, None), index - unconsumed_since)
    
    end_parsing = _end_parsing_if_no_multi_line_code(context) or _end_parsing_if_no_multi_line_string(context)
    if end_parsing:
        context.add_token(_get_string_token_type(context, end_string), 0)
        
        if (end_string is not None) and end_string == '}' and (context.flags & HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT):
            context.add_token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, 0)
    
    else:
        if add_line_break:
            context.add_token(TOKEN_TYPE_LINE_BREAK, 1)
    
    return 1 + end_parsing


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
    
    content = context.content
    content_length = context.content_length
    
    while True:
        content_character_index = context.content_character_index
        
        if content_character_index >= content_length:
            context.add_token(_get_string_token_type(context, end_string), 0)
            return
        
        unconsumed_since = content_character_index
        
        while True:
            action = _try_consume_string_till_end_of_line(
                context, unconsumed_since, content_character_index, end_string
            )
            if action != 0:
                if action == 1:
                    break
                return
            
            character = content[content_character_index]
            
            # ignore escaped
            if (
                (character == '\\') and
                (
                    
                    (content_character_index + 1 < content_length) and
                    (content[content_character_index + 1] in ('\\', '\'', '"', 'a', 'b', 'f', 'n', 'r', 't', 'v'))
                )
            ):
                content_character_index += 2
                continue
            
            # match end
            if (
                (character == end_character) and
                (
                    (end_string_length == 1) or
                    (
                        (content_character_index + end_string_length <= content_length) and
                        (content[content_character_index : content_character_index + end_string_length] == end_string)
                    )
                )
            ):
                if content_character_index > unconsumed_since:
                    context.add_token(_get_string_token_type(context, None), content_character_index - unconsumed_since)
                
                context.add_token(_get_string_token_type(context, end_string), end_string_length)
                return
            
            # Noting mentionable
            content_character_index += 1
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
    
    content = context.content
    content_length = context.content_length
    
    while True:
        content_character_index = context.content_character_index
        
        if content_character_index >= content_length:
            context.add_token(_get_string_token_type(context, end_string), 0)
            return
        
        unconsumed_since = content_character_index
        
        while True:
            action = _try_consume_string_till_end_of_line(
                context, unconsumed_since, content_character_index, end_string
            )
            if action != 0:
                if action == 1:
                    break
                return
            
            character = content[content_character_index]
            
            # ignore double `{` and `}`
            if (
                (character in ('{', '}')) and
                (
                    (content_character_index + 1 < content_length) and
                    (content[content_character_index + 1] == character)
                )
            ):
                content_character_index += 2
                continue
            
            # ignore escaped
            if (
                (character == '\\') and
                (
                    
                    (content_character_index + 1 < content_length) and
                    (content[content_character_index + 1] in ('\\', '\'', '"', 'a', 'b', 'f', 'n', 'r', 't', 'v'))
                )
            ):
                content_character_index += 2
                continue
            
            # match end
            if (
                (character == end_character) and
                (
                    (end_string_length == 1) or
                    (
                        (content_character_index + end_string_length <= content_length) and
                        (content[content_character_index : content_character_index + end_string_length] == end_string)
                    )
                )
            ):
                if content_character_index > unconsumed_since:
                    context.add_token(_get_string_token_type(context, None), content_character_index - unconsumed_since)
                
                context.add_token(_get_string_token_type(context, end_string), end_string_length)
                return
            
            # are we entering a format string?
            if character == '{':
                if content_character_index > unconsumed_since:
                    context.add_token(_get_string_token_type(context, None), content_character_index - unconsumed_since,
                    )
                
                context.add_token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, 1)
                
                # are we entering a format string?
                with context.enter(
                    (context.flags & HIGHLIGHT_PARSER_MASK_INHERITABLE) |
                    (
                        0
                        if context.flags & HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS
                        else HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE
                    ) |
                    HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                    HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
                ):
                    _keep_python_parsing(context)
                    nested_flags = context.flags
                
                if nested_flags & HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE:
                    _end_parsing_if_no_multi_line_code(context)
                    context.add_token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, 0)
                    context.add_token(_get_string_token_type(context, end_string), 0)
                    return
                
                # end parsing if disabled flag is hit
                if nested_flags & HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE:
                    context.flags |= HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE
                    context.add_token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, 0)
                    context.add_token(_get_string_token_type(context, end_string), 0)
                    return
                
                break
            
            # Noting mentionable
            content_character_index += 1
            continue


PYTHON_PARSERS = (
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
