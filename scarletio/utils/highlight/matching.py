__all__ = ()

from ..export_include import include

from .constants import (
    ATTRIBUTE_ACCESS_OPERATOR, BUILTIN_CONSTANTS, BUILTIN_EXCEPTIONS, BUILTIN_VARIABLES, COMPLEX_RP, CONSOLE_PREFIX_RP,
    FLOAT_RP, FORMAT_STRING_MATCH_STRING, FORMAT_STRING_POSTFIX_RP, IDENTIFIER_RP, INTEGER_BINARY_RP,
    INTEGER_DECIMAL_RP, INTEGER_HEXADECIMAL_RP, INTEGER_OCTAL_RP, KEYWORDS, KEYWORD_ELLIPSIS, MAGIC_FUNCTIONS,
    MAGIC_VARIABLES, OPERATOR_WORDS, OPERATOR_WP, PUNCTUATION_WP, SPACE_MATCH_RP, STRING_END_DOUBLE_RP,
    STRING_END_SINGLE_RP, STRING_MULTI_LINE_END_DOUBLE_RP, STRING_MULTI_LINE_END_SINGLE_RP, STRING_STARTER_RP
)
from .token_types import (
    TOKEN_TYPE_COMMENT, TOKEN_TYPE_IDENTIFIER_ATTRIBUTE, TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT,
    TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION, TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, TOKEN_TYPE_IDENTIFIER_KEYWORD,
    TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION, TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE, TOKEN_TYPE_IDENTIFIER_VARIABLE,
    TOKEN_TYPE_LINEBREAK, TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, TOKEN_TYPE_NUMERIC_FLOAT, TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX,
    TOKEN_TYPE_NUMERIC_INTEGER_BINARY, TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL, TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL,
    TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, TOKEN_TYPE_SPACE, TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX, TOKEN_TYPE_SPECIAL_OPERATOR,
    TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, TOKEN_TYPE_SPECIAL_OPERATOR_WORD, TOKEN_TYPE_SPECIAL_PUNCTUATION,
    TOKEN_TYPE_STRING_BINARY, TOKEN_TYPE_STRING_UNICODE, TOKEN_TYPE_STRING_UNICODE_FORMAT,
    TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX
)


FormatStringParserContext = include('FormatStringParserContext')


def _try_match_complex(context):
    """
    Tries to match a complex as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightContextBase``
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
    context : ``HighlightContextBase``
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
    context : ``HighlightContextBase``
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
    context : ``HighlightContextBase``
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
    context : ``HighlightContextBase``
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
    context : ``HighlightContextBase``
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
    context : ``HighlightContextBase``
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
    
    if content in BUILTIN_CONSTANTS:
        token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT
    elif content in KEYWORDS:
        token_type = TOKEN_TYPE_IDENTIFIER_KEYWORD
    elif content in OPERATOR_WORDS:
        token_type = TOKEN_TYPE_SPECIAL_OPERATOR_WORD
    else:
        last_token = context.get_last_related_token()
        if (last_token is not None) and (last_token.type == TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE):
            if content in MAGIC_FUNCTIONS:
                token_type = TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION
            elif content in MAGIC_VARIABLES:
                token_type = TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE
            else:
                token_type = TOKEN_TYPE_IDENTIFIER_ATTRIBUTE
        else:
            if content in BUILTIN_VARIABLES:
                token_type = TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE
            elif content in BUILTIN_EXCEPTIONS:
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
    context : ``HighlightContextBase``
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
    context : ``HighlightContextBase``
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


def _try_match_string(context):
    """
    Tries to match a string as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightContextBase``
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
    
    if prefix is None:
        token_type = TOKEN_TYPE_STRING_UNICODE
    elif 'b' in prefix:
        token_type = TOKEN_TYPE_STRING_BINARY
    elif 'f' in prefix:
        token_type = TOKEN_TYPE_STRING_UNICODE_FORMAT
    else:
        token_type = TOKEN_TYPE_STRING_UNICODE
    
    context.add_token(token_type, content)
    
    end = matched.end()
    context.set_line_character_index(end)
    set_end_later = -100
    
    if len(encapsulator) == 3:
        if encapsulator == '\'\'\'':
            end_finder = STRING_MULTI_LINE_END_SINGLE_RP
        else:
            end_finder = STRING_MULTI_LINE_END_DOUBLE_RP
        
        content_parts = []
        while True:
            if context.done:
                break
            
            line = context.get_line()
            index = context.get_line_character_index()
            
            matched = end_finder.match(line, index)
            if matched is None:
                end = len(line)
                if (end > index) and (line[end -1] == '\n'):
                    end -= 1
                    add_line_break = True
                else:
                    add_line_break = False
                
                if index != end:
                    content_parts.append(line[index : end])
                if add_line_break:
                    content_parts.append('\n')
                
                context.set_line_character_index(-2)
                continue
            
            content = matched.group(1)
            if content:
                content_parts.append(content)
            
            set_end_later = matched.end()
            break
        
        # Add content
        if token_type == TOKEN_TYPE_STRING_UNICODE_FORMAT:
            content = ''.join(content_parts)
            format_string_context = FormatStringParserContext(content)
            format_string_context.match()
            context.add_tokens(format_string_context.tokens)
        
        else:
            for content in content_parts:
                if content == '\n':
                    context.add_token(TOKEN_TYPE_LINEBREAK, '\n')
                else:
                    context.add_token(token_type, content)
    
    else:
        if len(line) != end:
            if encapsulator == '\'':
                end_finder = STRING_END_SINGLE_RP
            else:
                end_finder = STRING_END_DOUBLE_RP
            
            matched = end_finder.match(line, end)
            if matched is None:
                content = line[end:]
                set_end_later = -1
            else:
                content = matched.group(1)
                set_end_later = matched.end()
            
            if token_type == TOKEN_TYPE_STRING_UNICODE_FORMAT:
                format_string_context = FormatStringParserContext(content)
                format_string_context.match()
                context.add_tokens(format_string_context.tokens)
            
            else:
                context.add_token(token_type, content)
    
    if set_end_later >= 0:
        context.add_token(token_type, encapsulator)
    
    if set_end_later != -100:
        context.set_line_character_index(set_end_later)
    
    return True


def _try_match_space(context):
    """
    Tries to match some space as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightContextBase``
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
    context : ``HighlightContextBase``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether any comment could be matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    if line[index] != '#':
        return False
    
    # In later joined contents we might meet line break, so check that as well!
    line_break_index = line.find('\n')
    if line_break_index == -1:
        content = line[index:]
        context.add_token(TOKEN_TYPE_COMMENT, content)
        context.set_line_character_index(-1)
    else:
        content = line[index:line_break_index]
        context.add_token(TOKEN_TYPE_COMMENT, content)
        context.add_token(TOKEN_TYPE_LINEBREAK, '\n')
        context.set_line_character_index(line_break_index + 1)
    
    return True


def _try_match_anything(context):
    """
    Matches anything as the context's next token.
    
    Parameter
    ---------
    context : ``HighlightContextBase``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether anything could be matched, so of course true.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    content = line[index]
    context.add_token(TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, content)
    context.set_line_character_index(index + 1)
    return True


def _try_match_empty_line(context):
    """
    Tries to match an empty line.
    
    Parameter
    ---------
    context : ``HighlightContextBase``
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
    
    context.add_token(TOKEN_TYPE_LINEBREAK, '\n')
    context.set_line_character_index(-1)
    return True


def _try_match_console_prefix(context):
    """
    Tries to match a console prefix
    
    Parameter
    ---------
    context : ``HighlightContextBase``
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


def _try_match_linebreak(context):
    """
    Tries to match a linebreak.
    
    Parameters
    ----------
    context : ``HighlightContextBase``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether a linebreak was matched.
    """
    line = context.get_line()
    index = context.get_line_character_index()
    
    if line[index] != '\n':
        return False
    
    context.add_token(TOKEN_TYPE_LINEBREAK, '\n')
    context.set_line_character_index(index + 1)
    
    return True


PYTHON_PARSERS = (
    _try_match_empty_line,
    _try_match_console_prefix,
    _try_match_space,
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
    _try_match_linebreak,
    _try_match_anything,
)


def _try_match_till_format_string_expression(context):
    """
    Tries to match a format string's internal content, till reaches the first code part.
    
    Parameters
    ----------
    context : ``FormatStringParserContext``
        The context to use.
    
    Returns
    -------
    success : `bool`
        Whether anything was matched.
        
        Always returns `True`.
    """
    line = context.get_line()
    line_length = len(line)
    index = context.get_line_character_index()
    
    while True:
        if index >= line_length:
            break
        
        matched = FORMAT_STRING_MATCH_STRING.match(line, index)
        if matched is None:
            # We are at the end, we done, yay.
            content = line[index:]
            context.add_token(TOKEN_TYPE_STRING_UNICODE_FORMAT, content)
            index = -1
            break
        
        content, ender = matched.groups()
        index += len(content) + len(ender)
        context.add_token(TOKEN_TYPE_STRING_UNICODE_FORMAT, content)
        
        if (ender == '{{') or (ender == '}}'):
            # Escaped `{` or '}'
            context.add_token(TOKEN_TYPE_STRING_UNICODE_FORMAT, ender)
            continue
        
        if ender == '\n':
            # Multi-line string line break, need to add a linebreak.
            context.add_token(TOKEN_TYPE_LINEBREAK, '\n')
            continue
        
        if (ender == '{') or (ender == '}'):
            context.add_token(TOKEN_TYPE_SPECIAL_PUNCTUATION, ender)
            break
    
    context.set_line_character_index(index)
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
    if context.in_code:
        return False
    
    if context.brace_level != 1:
        return False
    
    line = context.get_line()
    index = context.get_line_character_index()
    
    matched = FORMAT_STRING_POSTFIX_RP.match(line, index)
    if matched is None:
        return False
    
    postfix = matched.group(1)
    end = matched.end()
    
    context.add_token(TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX, postfix)
    context.add_token(TOKEN_TYPE_SPECIAL_PUNCTUATION, '}')
    context.set_line_character_index(end)
    return True


PYTHON_PARSERS_FORMAT_STRING = (
    _try_match_empty_line,
    _try_match_linebreak,
    _try_match_space,
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
    _try_match_format_string_postfix,
    _try_match_anything,
)
