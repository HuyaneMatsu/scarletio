import vampytest

from ..flags import (
    HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS, HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE,
    HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE, HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
    HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE, HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS,
    HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE, HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS
)
from ..location import Location
from ..matching import (
    _try_match_anything, _try_match_comment, _try_match_complex, _try_match_console_prefix, _try_match_float,
    _try_match_format_string_code, _try_match_format_string_end, _try_match_format_string_postfix,
    _try_match_identifier, _try_match_integer_binary, _try_match_integer_decimal, _try_match_integer_hexadecimal,
    _try_match_integer_octal, _try_match_line_break, _try_match_operator, _try_match_punctuation, _try_match_space,
    _try_match_string
)
from ..parser_context import HighlightParserContext
from ..token import Token
from ..token_types import (
    TOKEN_TYPE_COMMENT, TOKEN_TYPE_IDENTIFIER_ATTRIBUTE, TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT,
    TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION, TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, TOKEN_TYPE_IDENTIFIER_KEYWORD,
    TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION, TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE, TOKEN_TYPE_IDENTIFIER_VARIABLE,
    TOKEN_TYPE_LINE_BREAK, TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, TOKEN_TYPE_NUMERIC_FLOAT,
    TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX, TOKEN_TYPE_NUMERIC_INTEGER_BINARY, TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL,
    TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL, TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, TOKEN_TYPE_SPACE,
    TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX, TOKEN_TYPE_SPECIAL_OPERATOR, TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE,
    TOKEN_TYPE_SPECIAL_OPERATOR_WORD, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE,
    TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN,
    TOKEN_TYPE_SPECIAL_PUNCTUATION_SEMI_COLON, TOKEN_TYPE_STRING_BINARY, TOKEN_TYPE_STRING_BINARY_SPECIAL_PREFIX,
    TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_CLOSE, TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN,
    TOKEN_TYPE_STRING_FORMAT_CODE, TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
    TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, TOKEN_TYPE_STRING_FORMAT_POSTFIX, TOKEN_TYPE_STRING_UNICODE,
    TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE,
    TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN
)


def _iter_options():
    # ---- complex ----
    
    yield (
        'complex -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_complex,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'complex -> actual',
        (
            '2.3j '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_complex,
        (
            4,
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX, Location(0, 0, 0, 4)),
            ],
            True,
        ),
    )
    
    yield (
        'complex -> start in middle',
        (
            '\n'
            '    2.3j '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_complex,
        (
            9,
            1,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX, Location(5, 1, 4, 4)),
            ],
            True,
        ),
    )
    
    # ---- float ----
    
    yield (
        'float -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_float,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'float -> actual',
        (
            '2.3 '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_float,
        (
            3,
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_FLOAT, Location(0, 0, 0, 3)),
            ],
            True,
        ),
    )
    
    yield (
        'float -> start in middle',
        (
            '\n'
            '    2.3 '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_float,
        (
            8,
            1,
            7,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_FLOAT, Location(5, 1, 4, 3)),
            ],
            True,
        ),
    )
    
    # ---- integer ~ hexadecimal ----
    
    yield (
        'integer ~ hexadecimal -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_hexadecimal,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'integer ~ hexadecimal -> actual',
        (
            '0xa2 '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_hexadecimal,
        (
            4,
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL, Location(0, 0, 0, 4)),
            ],
            True,
        ),
    )
    
    yield (
        'integer ~ hexadecimal -> start in middle',
        (
            '\n'
            '    0xa2 '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_integer_hexadecimal,
        (
            9,
            1,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL, Location(5, 1, 4, 4)),
            ],
            True,
        ),
    )
    
    # ---- integer ~ decimal ----
    
    yield (
        'integer ~ decimal -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_decimal,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'integer ~ decimal -> actual',
        (
            '2_345 '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_decimal,
        (
            5,
            0,
            5,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL, Location(0, 0, 0, 5)),
            ],
            True,
        ),
    )
    
    yield (
        'integer ~ decimal -> start in middle',
        (
            '\n'
            '    2_345 '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_integer_decimal,
        (
            10,
            1,
            9,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL, Location(5, 1, 4, 5)),
            ],
            True,
        ),
    )
    
    # ---- integer ~ octal ----
    
    yield (
        'integer ~ octal -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_octal,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'integer ~ octal -> actual',
        (
            '0o17 '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_octal,
        (
            4,
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, Location(0, 0, 0, 4)),
            ],
            True,
        ),
    )
    
    yield (
        'integer ~ octal -> start in middle',
        (
            '\n'
            '    0o17 '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_integer_octal,
        (
            9,
            1,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, Location(5, 1, 4, 4)),
            ],
            True,
        ),
    )
    
    # ---- integer ~ binary ----
    
    yield (
        'integer ~ binary -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_binary,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'integer ~ binary -> actual',
        (
            '0b01 '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_binary,
        (
            4,
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_BINARY, Location(0, 0, 0, 4)),
            ],
            True,
        ),
    )
    
    yield (
        'integer ~ binary -> start in middle',
        (
            '\n'
            '    0b01 '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_integer_binary,
        (
            9,
            1,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_BINARY, Location(5, 1, 4, 4)),
            ],
            True,
        ),
    )
    
    # ---- identifier ----
    
    yield (
        'identifier -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'identifier ~ constant -> actual',
        (
            'None '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            4,
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT, Location(0, 0, 0, 4)),
            ],
            True,
        ),
    )
    
    yield (
        'identifier ~ keyword -> actual',
        (
            'import '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            6,
            0,
            6,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_KEYWORD, Location(0, 0, 0, 6)),
            ],
            True,
        ),
    )
    
    yield (
        'identifier ~ operator word -> actual',
        (
            'and '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            3,
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_OPERATOR_WORD, Location(0, 0, 0, 3)),
            ],
            True,
        ),
    )
    
    yield (
        'identifier ~ magic function -> actual',
        (
            'pudding.__add__ '
        ),
        8,
        0,
        8,
        0,
        None,
        [
            Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(0, 0, 0, 7)),
            Token(TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, Location(7, 0, 7, 1)),
        ],
        _try_match_identifier,
        (
            15,
            0,
            15,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION, Location(8, 0, 8, 7)),
            ],
            True,
        ),
    )
    
    yield (
        'identifier ~ magic attribute -> actual',
        (
            'pudding.__mro__ '
        ),
        8,
        0,
        8,
        0,
        None,
        [
            Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(0, 0, 0, 7)),
            Token(TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, Location(7, 0, 7, 1)),
            
        ],
        _try_match_identifier,
        (
            15,
            0,
            15,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE, Location(8, 0, 8, 7)),
            ],
            True,
        ),
    )
    
    yield (
        'identifier ~ attribute -> actual',
        (
            'pudding.flandre '
        ),
        8,
        0,
        8,
        0,
        None,
        [
            Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(0, 0, 0, 7)),
            Token(TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, Location(7, 0, 7, 1)),
        ],
        _try_match_identifier,
        (
            15,
            0,
            15,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_ATTRIBUTE, Location(8, 0, 8, 7)),
            ],
            True,
        ),
    )
    
    yield (
        'identifier ~ builtin variable -> actual',
        (
            'max '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            3,
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, Location(0, 0, 0, 3)),
            ],
            True,
        ),
    )
    
    yield (
        'identifier ~ builtin exception -> actual',
        (
            'ImportError '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            11,
            0,
            11,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION, Location(0, 0, 0, 11)),
            ],
            True,
        ),
    )
    
    yield (
        'identifier ~ variable -> actual',
        (
            'pudding '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            7,
            0,
            7,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(0, 0, 0, 7)),
            ],
            True,
        ),
    )
    
    yield (
        'identifier -> start in middle',
        (
            '\n'
            '    pudding '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_identifier,
        (
            12,
            1,
            11,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(5, 1, 4, 7)),
            ],
            True,
        ),
    )
    
    # ---- punctuation  ----
    
    yield (
        'punctuation -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_punctuation,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'punctuation -> actual (semi colon)',
        (
            '; '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_punctuation,
        (
            1,
            0,
            1,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_SEMI_COLON, Location(0, 0, 0, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'punctuation -> brace (curly open), tracking',
        (
            '{ '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_punctuation,
        (
            1,
            0,
            1,
            0,
            [
                TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN,
            ],
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, Location(0, 0, 0, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'punctuation -> brace (curly close), tracking',
        (
            '({} '
        ),
        2,
        0,
        2,
        0,
        [
            TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN,
            TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN,
        ],
        [
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN, Location(0, 0, 0, 1)),
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN, Location(1, 0, 1, 1)),
        ],
        _try_match_punctuation,
        (
            3,
            0,
            3,
            0,
            [
                TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_ROUND_OPEN,
            ],
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_CLOSE, Location(2, 0, 2, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'punctuation -> start in middle',
        (
            '\n'
            '    ; '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_punctuation,
        (
            6,
            1,
            5,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION_SEMI_COLON, Location(5, 1, 4, 1)),
            ],
            True,
        ),
    )
    
    # ---- operator  ----
    
    yield (
        'operator -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_operator,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'operator ~ regular -> actual',
        (
            '<<= '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_operator,
        (
            3,
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_OPERATOR, Location(0, 0, 0, 3)),
            ],
            True,
        ),
    )
    
    yield (
        'operator ~ attribute -> actual',
        (
            '. '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_operator,
        (
            1,
            0,
            1,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, Location(0, 0, 0, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'operator ~ ellipsis -> actual',
        (
            '... '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_operator,
        (
            3,
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT, Location(0, 0, 0, 3)),
            ],
            True,
        ),
    )
    
    yield (
        'operator -> start in middle',
        (
            '\n'
            '    <<= '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_operator,
        (
            8,
            1,
            7,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_OPERATOR, Location(5, 1, 4, 3)),
            ],
            True,
        ),
    )
    
    # ---- space  ----
    
    yield (
        'space -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_space,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'space -> actual',
        (
            '  = '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_space,
        (
            2,
            0,
            2,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPACE, Location(0, 0, 0, 2)),
            ],
            True,
        ),
    )
    
    yield (
        'space -> start in middle',
        (
            '\n'
            '    pudding  ='
        ),
        12,
        1,
        11,
        0,
        None,
        None,
        _try_match_space,
        (
            14,
            1,
            13,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPACE, Location(12, 1, 11, 2)),
            ],
            True,
        ),
    )
    
    # ---- comment  ----
    
    yield (
        'comment -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_comment,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'comment -> actual',
        (
            '# pudding '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_comment,
        (
            10,
            0,
            10,
            0,
            None,
            True,
            [
                Token(TOKEN_TYPE_COMMENT, Location(0, 0, 0, 10)),
            ],
            True,
        ),
    )
    
    yield (
        'comment -> actual (has next line)',
        (
            '# pudding \n'
            '12.6'
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_comment,
        (
            10,
            0,
            10,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_COMMENT, Location(0, 0, 0, 10)),
            ],
            True,
        ),
    )
    
    yield (
        'comment -> start in middle',
        (
            '\n'
            '    # pudding'
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_comment,
        (
            14,
            1,
            13,
            0,
            None,
            True,
            [
                Token(TOKEN_TYPE_COMMENT, Location(5, 1, 4, 9)),
            ],
            True,
        ),
    )
    
    # ---- anything  ----
    
    yield (
        'anything -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_anything,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'anything -> actual',
        (
            '¤ '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_anything,
        (
            1,
            0,
            1,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, Location(0, 0, 0, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'anything -> start in middle',
        (
            '\n'
            '    ¤ '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_anything,
        (
            6,
            1,
            5,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, Location(5, 1, 4, 1)),
            ],
            True,
        ),
    )
    
    # ---- console prefix  ----
    
    yield (
        'console prefix -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_console_prefix,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'console prefix -> actual',
        (
            'In [1]: miau'
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_console_prefix,
        (
            8,
            0,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX, Location(0, 0, 0, 7)),
                Token(TOKEN_TYPE_SPACE, Location(7, 0, 7, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'console prefix -> start in middle',
        (
            '\n'
            '    In [1]: miau '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_console_prefix,
        (
            5,
            1,
            4,
            0,
            None,
            False,
            [],
            False,
        ),
    )
    
    # ---- line break  ----
    
    yield (
        'line break -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_line_break,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'line break -> actual',
        (
            '\n'
            ' '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_line_break,
        (
            1,
            1,
            0,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_LINE_BREAK, Location(0, 0, 0, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'line break -> line breaks disabled',
        (
            '\n'
            ''
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE,
        None,
        None,
        _try_match_line_break,
        (
            0,
            0,
            0,
            HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE | HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE,
            None,
            True,
            [],
            True,
        ),
    )
    
    yield (
        'line break -> start in middle',
        (
            '\n'
            'miau\n'
            ' '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_line_break,
        (
            6,
            2,
            0,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_LINE_BREAK, Location(5, 1, 4, 1)),
            ],
            True,
        ),
    )
    
    # ---- format string end  ----
    
    yield (
        'format string end -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        None,
        None,
        _try_match_format_string_end,
        (
            0,
            0,
            0,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'format string end -> actual',
        (
            '} '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_end,
        (
            1,
            0,
            1,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(0, 0, 0, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'format string end -> not in format string',
        (
            '} '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_format_string_end,
        (
            0,
            0,
            0,
            0,
            None,
            False,
            [],
            False,
        ),
    )
    
    yield (
        'format string end -> open braces',
        (
            '{} '
        ),
        1,
        0,
        1,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN,
        ],
        [
            Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(0, 0, 0, 1)),
        ],
        _try_match_format_string_end,
        (
            1,
            0,
            1,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            [
                TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN,
            ],
            False,
            [],
            False,
        ),
    )
    
    yield (
        'format string end -> start in middle',
        (
            '\n'
            '    } '
        ),
        5,
        1,
        4,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_end,
        (
            6,
            1,
            5,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(5, 1, 4, 1)),
            ],
            True,
        ),
    )
    
    # ---- format string postfix  ----
    
    yield (
        'format string postfix -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        None,
        None,
        _try_match_format_string_postfix,
        (
            0,
            0,
            0,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'format string postfix -> actual',
        (
            '!r} '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_postfix,
        (
            3,
            0,
            3,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_POSTFIX, Location(0, 0, 0, 2)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(2, 0, 2, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'format string postfix -> not in format string',
        (
            '!r} '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_format_string_postfix,
        (
            0,
            0,
            0,
            0,
            None,
            False,
            [],
            False,
        ),
    )
    
    yield (
        'format string postfix -> open braces',
        (
            '{!r} ',
        ),
        1,
        0,
        1,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN,
        ],
        [
            Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(0, 0, 0, 1)),
        ],
        _try_match_format_string_postfix,
        (
            1,
            0,
            1,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            [
                TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN,
            ],
            False,
            [],
            False,
        ),
    )
    
    yield (
        'format string postfix -> start in middle',
        (
            '\n'
            '    !r} '
        ),
        5,
        1,
        4,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_postfix,
        (
            
            8,
            1,
            7,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_POSTFIX, Location(5, 1, 4, 2)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(7, 1, 6, 1)),
            ],
            True,
        ),
    )
    
    # ---- format string code  ----
    
    yield (
        'format string code -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        None,
        None,
        _try_match_format_string_code,
        (
            0,
            0,
            0,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'format string code -> actual',
        (
            ':} '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_code,
        (
            2,
            0,
            2,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(1, 0, 1, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'format string code -> string in it',
        (
            ':pudding} '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_code,
        (
            9,
            0,
            9,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_CODE, Location(1, 0, 1, 7)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(8, 0, 8, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'format string code -> double brace in it',
        (
            ':}}{{} '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_code,
        (
            6,
            0,
            6,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_CODE, Location(1, 0, 1, 4)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(5, 0, 5, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'format string code -> escaped',
        (
            ':\\n\\n} '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_code,
        (
            6,
            0,
            6,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_CODE, Location(1, 0, 1, 4)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(5, 0, 5, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'format string code -> escaping',
        (
            ':\n'
            '} '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN,
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_code,
        (
            1,
            0,
            1,
            (
                HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT |
                HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(1, 0, 1, 0)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(1, 0, 1, 0)),
            ],
            True,
        ),
    )
    
    yield (
        'format string code -> nested braces',
        (
            ':{pudding}a} '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_code,
        (
            12,
            0,
            12,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(2, 0, 2, 7)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(9, 0, 9, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_CODE, Location(10, 0, 10, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(11, 0, 11, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'format string code -> multi-line',
        (
            ':{\n'
            '    pudding\n'
            '}} '
        ),
        0,
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT |
            HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS
        ),
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_code,
        (
            17,
            2,
            2,
            (
                HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT |
                HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_LINE_BREAK, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_SPACE, Location(3, 1, 0, 4)),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(7, 1, 4, 7)),
                Token(TOKEN_TYPE_LINE_BREAK, Location(14, 1, 11, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(15, 2, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(16, 2, 1, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'format string code -> multi-line (string code)',
        (
            ':a\n'
            'a} '
        ),
        0,
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT |
            HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS
        ),
        [
            TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN,
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_code,
        (
            5,
            1,
            2,
            (
                HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT |
                HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS
            ),
            [
                TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN,
            ],
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_CODE, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_LINE_BREAK, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_CODE, Location(3, 1, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(4, 1, 1, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'format string code -> multi-line & multi-line disabled',
        (
            ':{\n'
            '    pudding\n'
            '}} '
        ),
        0,
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT |
            HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE
        ),
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN
        ],
        None,
        _try_match_format_string_code,
        (
            2,
            0,
            2,
            (
                HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT |
                HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE | HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(2, 0, 2, 0)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(2, 0, 2, 0)),
            ],
            True,
        ),
    )
    
    yield (
        'format string code -> not in format string',
        (
            ':} '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_format_string_code,
        (
            0,
            0,
            0,
            0,
            None,
            False,
            [],
            False,
        ),
    )
    
    yield (
        'format string format code -> open braces',
        (
            '{:} '
        ),
        1,
        0,
        1,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN,
        ],
        [
            Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(0, 0, 0, 1)),
        ],
        _try_match_format_string_code,
        (
            1,
            0,
            1,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            [
                TOKEN_TYPE_SPECIAL_PUNCTUATION_BRACE_CURLY_OPEN,
            ],
            False,
            [],
            False,
        ),
    )
    
    yield (
        'format string code -> start in middle',
        (
            '\n'
            '    :} '
        ),
        5,
        1,
        4,
        HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
        [
            TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN,
        ],
        None,
        _try_match_format_string_code,
        (
            7,
            1,
            6,
            HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE | HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_CODE_BEGIN, Location(5, 1, 4, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(6, 1, 5, 1)),
            ],
            True,
        ),
    )
    
    # ---- string ----
    
    yield (
        'string -> empty',
        (
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            0,
            0,
            0,
            None,
            True,
            [],
            False,
        ),
    )
    
    yield (
        'string ~ unicode -> actual',
        (
            '"pudding" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            9,
            0,
            9,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(1, 0, 1, 7)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(8, 0, 8, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ unicode ~ single quote -> actual',
        (
            '\'pudding\' '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            9,
            0,
            9,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(1, 0, 1, 7)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(8, 0, 8, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ raw unicode -> actual',
        (
            'r"pudding" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            10,
            0,
            10,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(2, 0, 2, 7)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(9, 0, 9, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ binary -> actual',
        (
            'b"pudding" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            10,
            0,
            10,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_BINARY_SPECIAL_PREFIX, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_BINARY, Location(2, 0, 2, 7)),
                Token(TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_CLOSE, Location(9, 0, 9, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ raw binary -> actual',
        (
            'rb"pudding" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            11,
            0,
            11,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_BINARY_SPECIAL_PREFIX, Location(0, 0, 0, 2)),
                Token(TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_OPEN, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_STRING_BINARY, Location(3, 0, 3, 7)),
                Token(TOKEN_TYPE_STRING_BINARY_SPECIAL_QUOTE_CLOSE, Location(10, 0, 10, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ format unicode -> actual',
        (
            'f"pudding" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            10,
            0,
            10,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(2, 0, 2, 7)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(9, 0, 9, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ raw format unicode -> actual',
        (
            'rf"pudding" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            11,
            0,
            11,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, Location(0, 0, 0, 2)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(3, 0, 3, 7)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(10, 0, 10, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ unicode -> other encapsulator in middle',
        (
            '"\'\'" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            4,
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(1, 0, 1, 2)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(3, 0, 3, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ unicode -> single line',
        (
            '""\n'
            '""\n'
        
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            2,
            0,
            2,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(1, 0, 1, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ unicode -> multi line',
        (
            '"""\n'
            '    pudding"""\n'
            ''
        
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            18,
            1,
            14,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(0, 0, 0, 3)),
                Token(TOKEN_TYPE_LINE_BREAK, Location(3, 0, 3, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(4, 1, 0, 11)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(15, 1, 11, 3)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ unicode -> unclosed',
        (
            '"""\n'
            '    pudding\n'
            ''
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            16,
            2,
            0,
            0,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(0, 0, 0, 3)),
                Token(TOKEN_TYPE_LINE_BREAK, Location(3, 0, 3, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(4, 1, 0, 11)),
                Token(TOKEN_TYPE_LINE_BREAK, Location(15, 1, 11, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(16, 2, 0, 0)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ unicode -> multi line, multi line code disabled',
        (
            '"""pudding\n'
            '"""\n'
            ''
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE,
        None,
        None,
        _try_match_string,
        (
            10,
            0,
            10,
            HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(0, 0, 0, 3)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(3, 0, 3, 7)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(10, 0, 10, 0)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ unicode -> ignore escaped encapsulator',
        (
            '"\\"" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            4,
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(1, 0, 1, 2)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(3, 0, 3, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ unicode -> double quote, but disabled',
        (
            '"" '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS,
        None,
        None,
        _try_match_string,
        (
            0,
            0,
            0,
            HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS | HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE,
            None,
            True,
            [],
            True,
        ),
    )
    
    yield (
        'string ~ unicode -> single quote, but disabled',
        (
            '\'\' '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS,
        None,
        None,
        _try_match_string,
        (
            0,
            0,
            0,
            HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS | HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE,
            None,
            True,
            [],
            True,
        ),
    )
    
    yield (
        'string ~ format unicode -> with code in it',
        (
            'f"{pudding + mister}" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            21,
            0,
            21,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(3, 0, 3, 7)),
                Token(TOKEN_TYPE_SPACE, Location(10, 0, 10, 1)),
                Token(TOKEN_TYPE_SPECIAL_OPERATOR, Location(11, 0, 11, 1)),
                Token(TOKEN_TYPE_SPACE, Location(12, 0, 12, 1)),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(13, 0, 13, 6)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(19, 0, 19, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(20, 0, 20, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ format unicode -> multi-line code, but not allowed',
        (
            'f"{\n'
            'pudding\n'
            '}" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            3,
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(3, 0, 3, 0)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(3, 0, 3, 0)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ format unicode -> multi-line code, allowed',
        (
            'f"{\n'
            'pudding\n'
            '}" '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS,
        None,
        None,
        _try_match_string,
        (
            14,
            2,
            2,
            HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_LINE_BREAK, Location(3, 0, 3, 1)),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, Location(4, 1, 0, 7)),
                Token(TOKEN_TYPE_LINE_BREAK, Location(11, 1, 7, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(12, 2, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(13, 2, 1, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ format unicode -> string inside, allow different',
        (
            'f"{\'\'}" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            7,
            0,
            7,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(3, 0, 3, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(4, 0, 4, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(5, 0, 5, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(6, 0, 6, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ format unicode -> string inside, allow same (relaxed)',
        (
            'f"{""}" '
        ),
        0,
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS,
        None,
        None,
        _try_match_string,
        (
            7,
            0,
            7,
            HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(3, 0, 3, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(4, 0, 4, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(5, 0, 5, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(6, 0, 6, 1)),
            ],
            True,
        ),
    )
    
    yield (
        'string ~ format unicode -> string inside, disallow same (strict)',
        (
            'f"{""}" '
        ),
        0,
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            3,
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_PREFIX, Location(0, 0, 0, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(1, 0, 1, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_OPEN, Location(2, 0, 2, 1)),
                Token(TOKEN_TYPE_STRING_FORMAT_MARK_BRACE_CLOSE, Location(3, 0, 3, 0)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(3, 0, 3, 0)),
            ],
            True,
        ),
    )
    
    yield (
        'string -> start in middle',
        (
            '\n'
            '    "pudding" '
        ),
        5,
        1,
        4,
        0,
        None,
        None,
        _try_match_string,
        (
            14,
            1,
            13,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_OPEN, Location(5, 1, 4, 1)),
                Token(TOKEN_TYPE_STRING_UNICODE, Location(6, 1, 5, 7)),
                Token(TOKEN_TYPE_STRING_UNICODE_SPECIAL_QUOTE_CLOSE, Location(13, 1, 12, 1)),
            ],
            True,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).named_first().returning_last())
def test__try_matchers(
    content, content_character_index, line_index, line_character_index, flags, brace_nesting, tokens, matcher
):
    """
    Tests whether try matchers work as intended.
    
    Parameters
    ----------
    content : `str`
        Content to match form.
    
    content_character_index : `int`
        Content character index to start matching at.
    
    line_index : `int`
        Line index to start matching at.
    
    line_character_index : `int`
        Character index to start matching at.
    
    flags : `int`
        Flags to match with.
    
    brace_nesting : `None | list<int>`
        How the braces are nested.
    
    tokens : `None | list<Token>`
        Tokens to start initially with.
    
    matcher : `FunctionType`
        Matcher to use.
    
    Returns
    -------
    line_index : `int`
        Line index to start matching at.
    
    line_character_index : `int`
        Character index to start matching at.
    
    flags : `int`
        Flags to match with.
    
    brace_nesting : `None | list<int>`
        How the braces are nested.
    
    done : `bool`
        Whether matching is done.
    
    tokens : `list<Token>`
        Matched tokens.
    
    output : `bool`
        Whether matching was successful.
    """
    parser_context = HighlightParserContext(content, flags)
    parser_context.content_character_index = content_character_index
    parser_context.line_index = line_index
    parser_context.line_character_index = line_character_index
    
    if (tokens is not None):
        parser_context.tokens.extend(tokens)
    
    if (brace_nesting is not None):
        parser_context.brace_nesting = brace_nesting.copy()
    
    output = matcher(parser_context)
    vampytest.assert_instance(output, bool)
    
    return (
        parser_context.content_character_index,
        parser_context.line_index,
        parser_context.line_character_index,
        parser_context.flags,
        parser_context.brace_nesting,
        parser_context.done,
        parser_context.tokens[(0 if tokens is None else len(tokens)):],
        output,
    )
