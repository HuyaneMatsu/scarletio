import vampytest

from ..flags import (
    HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS, HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING,
    HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE, HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE,
    HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT, HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE,
    HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS, HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE,
    HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS
)
from ..matching import (
    _try_match_anything, _try_match_comment, _try_match_complex, _try_match_console_prefix, _try_match_empty_line,
    _try_match_float, _try_match_format_string_code, _try_match_format_string_end, _try_match_format_string_postfix,
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
    TOKEN_TYPE_SPECIAL_OPERATOR_WORD, TOKEN_TYPE_SPECIAL_PUNCTUATION, TOKEN_TYPE_STRING_BINARY,
    TOKEN_TYPE_STRING_UNICODE, TOKEN_TYPE_STRING_UNICODE_FORMAT, TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE,
    TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX
)


def _iter_options():
    # ---- complex ----
    
    # complex -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # complex -> actual
    yield (
        [
            '2.3j ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_complex,
        (
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX, '2.3j'),
            ],
            True,
        ),
    )
    
    # complex -> start in middle
    yield (
        [
            '\n',
            '    2.3j ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_complex,
        (
            1,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX, '2.3j'),
            ],
            True,
        ),
    )
    
    # ---- float ----
    
    # float -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # float -> actual
    yield (
        [
            '2.3 ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_float,
        (
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_FLOAT, '2.3'),
            ],
            True,
        ),
    )
    
    # float -> start in middle
    yield (
        [
            '\n',
            '    2.3 ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_float,
        (
            1,
            7,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_FLOAT, '2.3'),
            ],
            True,
        ),
    )
    
    # ---- integer ~ hexadecimal ----
    
    # integer ~ hexadecimal -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # integer ~ hexadecimal -> actual
    yield (
        [
            '0xa2 ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_hexadecimal,
        (
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL, '0xa2'),
            ],
            True,
        ),
    )
    
    # integer ~ hexadecimal -> start in middle
    yield (
        [
            '\n',
            '    0xa2 ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_integer_hexadecimal,
        (
            1,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL, '0xa2'),
            ],
            True,
        ),
    )
    
    # ---- integer ~ decimal ----
    
    # integer ~ decimal -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # integer ~ decimal -> actual
    yield (
        [
            '2_345 ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_decimal,
        (
            0,
            5,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL, '2_345'),
            ],
            True,
        ),
    )
    
    # integer ~ decimal -> start in middle
    yield (
        [
            '\n',
            '    2_345 ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_integer_decimal,
        (
            1,
            9,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL, '2_345'),
            ],
            True,
        ),
    )
    
    # ---- integer ~ octal ----
    
    # integer ~ octal -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # integer ~ octal -> actual
    yield (
        [
            '0o17 ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_octal,
        (
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, '0o17'),
            ],
            True,
        ),
    )
    
    # integer ~ octal -> start in middle
    yield (
        [
            '\n',
            '    0o17 ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_integer_octal,
        (
            1,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_OCTAL, '0o17'),
            ],
            True,
        ),
    )
    
    # ---- integer ~ binary ----
    
    # integer ~ binary -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # integer ~ binary -> actual
    yield (
        [
            '0b01 ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_integer_binary,
        (
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_BINARY, '0b01'),
            ],
            True,
        ),
    )
    
    # integer ~ binary -> start in middle
    yield (
        [
            '\n',
            '    0b01 ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_integer_binary,
        (
            1,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NUMERIC_INTEGER_BINARY, '0b01'),
            ],
            True,
        ),
    )
    
    # ---- identifier ----
    
    # identifier -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # identifier ~ constant -> actual
    yield (
        [
            'None ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT, 'None'),
            ],
            True,
        ),
    )
    
    # identifier ~ keyword -> actual
    yield (
        [
            'import ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            0,
            6,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_KEYWORD, 'import'),
            ],
            True,
        ),
    )
    
    # identifier ~ operator word -> actual
    yield (
        [
            'and ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_OPERATOR_WORD, 'and'),
            ],
            True,
        ),
    )
    
    # identifier ~ magic function -> actual
    yield (
        [
            'pudding.__add__ ',
        ],
        0,
        8,
        0,
        None,
        [
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
                Token(TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, '.'),
            
        ],
        _try_match_identifier,
        (
            0,
            15,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION, '__add__'),
            ],
            True,
        ),
    )
    
    # identifier ~ magic attribute -> actual
    yield (
        [
            'pudding.__mro__ ',
        ],
        0,
        8,
        0,
        None,
        [
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
                Token(TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, '.'),
            
        ],
        _try_match_identifier,
        (
            0,
            15,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE, '__mro__'),
            ],
            True,
        ),
    )
    
    # identifier ~ attribute -> actual
    yield (
        [
            'pudding.flandre ',
        ],
        0,
        8,
        0,
        None,
        [
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
                Token(TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, '.'),
            
        ],
        _try_match_identifier,
        (
            0,
            15,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_ATTRIBUTE, 'flandre'),
            ],
            True,
        ),
    )
    
    # identifier ~ builtin variable -> actual
    yield (
        [
            'max ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE, 'max'),
            ],
            True,
        ),
    )
    
    # identifier ~ builtin exception -> actual
    yield (
        [
            'ImportError ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            0,
            11,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION, 'ImportError'),
            ],
            True,
        ),
    )
    
    # identifier ~ variable -> actual
    yield (
        [
            'pudding ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_identifier,
        (
            0,
            7,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
            ],
            True,
        ),
    )
    
    # identifier -> start in middle
    yield (
        [
            '\n',
            '    pudding ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_identifier,
        (
            1,
            11,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
            ],
            True,
        ),
    )
    
    # ---- punctuation  ----
    
    # punctuation -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # punctuation -> actual
    yield (
        [
            '; ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_punctuation,
        (
            0,
            1,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, ';'),
            ],
            True,
        ),
    )
    
    # punctuation -> brace, no tracking
    yield (
        [
            '{ ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_punctuation,
        (
            0,
            1,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, '{'),
            ],
            True,
        ),
    )
    
    # punctuation -> brace, tracking
    yield (
        [
            '{ ',
        ],
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING,
        None,
        None,
        _try_match_punctuation,
        (
            0,
            1,
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING,
            [
                '{',
            ],
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, '{'),
            ],
            True,
        ),
    )
    
    # punctuation -> brace, tracking (close)
    yield (
        [
            '({} ',
        ],
        0,
        2,
        HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING,
        [
            '(', '{',
        ],
        [
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, '('),
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, '{'),
        ],
        _try_match_punctuation,
        (
            0,
            3,
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING,
            [
                '(',
            ],
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, '}'),
            ],
            True,
        ),
    )
    
    # punctuation -> start in middle
    yield (
        [
            '\n',
            '    ; ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_punctuation,
        (
            1,
            5,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, ';'),
            ],
            True,
        ),
    )
    
    # ---- operator  ----
    
    # operator -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # operator ~ regular -> actual
    yield (
        [
            '<<= ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_operator,
        (
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_OPERATOR, '<<='),
            ],
            True,
        ),
    )
    
    # operator ~ attribute -> actual
    yield (
        [
            '. ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_operator,
        (
            0,
            1,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, '.'),
            ],
            True,
        ),
    )
    
    # operator ~ ellipsis -> actual
    yield (
        [
            '... ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_operator,
        (
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT, '...'),
            ],
            True,
        ),
    )
    
    # operator -> start in middle
    yield (
        [
            '\n',
            '    <<= ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_operator,
        (
            1,
            7,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_OPERATOR, '<<='),
            ],
            True,
        ),
    )
    
    # ---- space  ----
    
    # space -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # space -> actual
    yield (
        [
            '  = ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_space,
        (
            0,
            2,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPACE, '  '),
            ],
            True,
        ),
    )
    
    # space -> start in middle
    yield (
        [
            '\n',
            '    pudding  =',
        ],
        1,
        11,
        0,
        None,
        None,
        _try_match_space,
        (
            1,
            13,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPACE, '  '),
            ],
            True,
        ),
    )
    
    # ---- comment  ----
    
    # comment -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # comment -> actual
    yield (
        [
            '# pudding ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_comment,
        (
            1,
            0,
            0,
            None,
            True,
            [
                Token(TOKEN_TYPE_COMMENT, '# pudding '),
            ],
            True,
        ),
    )
    
    # comment -> actual
    yield (
        [
            '# pudding \n',
            '12.6',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_comment,
        (
            1,
            0,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_COMMENT, '# pudding '),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # comment -> multi line when disabled
    yield (
        [
            '# pudding \n',
            '',
        ],
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE,
        None,
        None,
        _try_match_comment,
        (
            1,
            0,
            HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE | HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE,
            None,
            True,
            [
                Token(TOKEN_TYPE_COMMENT, '# pudding '),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # comment -> start in middle
    yield (
        [
            '\n',
            '    # pudding',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_comment,
        (
            2,
            0,
            0,
            None,
            True,
            [
                Token(TOKEN_TYPE_COMMENT, '# pudding'),
            ],
            True,
        ),
    )
    
    # ---- anything  ----
    
    # anything -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # anything -> actual
    yield (
        [
            '¤ ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_anything,
        (
            0,
            1,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, '¤'),
            ],
            True,
        ),
    )
    
    # anything -> start in middle
    yield (
        [
            '\n',
            '    ¤ ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_anything,
        (
            1,
            5,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_NON_SPACE_UNIDENTIFIED, '¤'),
            ],
            True,
        ),
    )
    
    # ---- empty line  ----
    
    # empty line -> empty
    yield (
        [],
        0,
        0,
        0,
        None,
        None,
        _try_match_empty_line,
        (
            1,
            0,
            0,
            None,
            True,
            [],
            True,
        ),
    )
    
    # empty line -> actual
    yield (
        [
            '',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_empty_line,
        (
            1,
            0,
            0,
            None,
            True,
            [],
            True,
        ),
    )
    
    # empty line -> start in middle
    yield (
        [
            '\n',
            ' \n',
            '',
        ],
        1,
        1,
        0,
        None,
        None,
        _try_match_empty_line,
        (
            1,
            1,
            0,
            None,
            False,
            [],
            False,
        ),
    )
    
    # ---- console prefix  ----
    
    # console prefix -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # console prefix -> actual
    yield (
        [
            'In [1]: miau',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_console_prefix,
        (
            0,
            8,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX, 'In [1]:'),
                Token(TOKEN_TYPE_SPACE, ' '),
            ],
            True,
        ),
    )
    
    # console prefix -> start in middle
    yield (
        [
            '\n',
            '    In [1]: miau ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_console_prefix,
        (
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
    
    # line break -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # line break -> actual
    yield (
        [
            '\n',
            '',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_line_break,
        (
            1,
            0,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # line break -> line breaks disabled
    yield (
        [
            '\n',
            '',
        ],
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE,
        None,
        None,
        _try_match_line_break,
        (
            1,
            0,
            HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE | HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE,
            None,
            True,
            [
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # line break -> start in middle
    yield (
        [
            '\n',
            'miau\n',
            '',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_line_break,
        (
            2,
            0,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # ---- format string end  ----
    
    # format string end -> empty
    yield (
        [],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_end,
        (
            0,
            0,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [],
            False,
        ),
    )
    
    # format string end -> actual
    yield (
        [
            '} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_end,
        (
            0,
            1,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # format string end -> not in format string
    yield (
        [
            '} ',
        ],
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
            None,
            False,
            [],
            False,
        ),
    )
    
    # format string end -> open braces
    yield (
        [
            '{} ',
        ],
        0,
        1,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        [
            '{',
        ],
        [
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, '{'),
        ],
        _try_match_format_string_end,
        (
            0,
            1,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            [
                '{',
            ],
            False,
            [],
            False,
        ),
    )
    
    # format string end -> start in middle
    yield (
        [
            '\n',
            '    } ',
        ],
        1,
        4,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_end,
        (
            1,
            5,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # ---- format string postfix  ----
    
    # format string postfix -> empty
    yield (
        [],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_postfix,
        (
            0,
            0,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [],
            False,
        ),
    )
    
    # format string postfix -> actual
    yield (
        [
            '!r} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_postfix,
        (
            0,
            3,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX, '!r'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # format string postfix -> not in format string
    yield (
        [
            '!r} ',
        ],
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
            None,
            False,
            [],
            False,
        ),
    )
    
    # format string postfix -> open braces
    yield (
        [
            '{!r} ',
        ],
        0,
        1,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        [
            '{',
        ],
        [
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, '{'),
        ],
        _try_match_format_string_postfix,
        (
            0,
            1,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            [
                '{',
            ],
            False,
            [],
            False,
        ),
    )
    
    # format string postfix -> start in middle
    yield (
        [
            '\n',
            '    !r} ',
        ],
        1,
        4,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_postfix,
        (
            1,
            7,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX, '!r'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # ---- format string code  ----
    
    # format string code -> empty
    yield (
        [],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            0,
            0,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [],
            False,
        ),
    )
    
    # format string code -> actual
    yield (
        [
            ':} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            0,
            2,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # format string code -> string in it
    yield (
        [
            ':pudding} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            0,
            9,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE, 'pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # format string code -> double brace in it
    yield (
        [
            ':}}{{} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            0,
            6,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE, '}}{{'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # format string code -> escaped
    yield (
        [
            ':\\n\\n} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            0,
            6,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE, '\\n\\n'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # format string code -> escaped
    yield (
        [
            ':\n',
            '} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            1,
            0,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT | HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # format string code -> escaped
    yield (
        [
            ':{pudding}a} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            0,
            12,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE, 'a'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # format string code -> nested braces
    yield (
        [
            ':{pudding}a} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            0,
            12,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE, 'a'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # format string code -> multi-line
    yield (
        [
            ':{\n',
            '    pudding\n',
            '}} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT | HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            2,
            2,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT | HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
                Token(TOKEN_TYPE_SPACE, '    '),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # format string code -> multi-line & multi-line disabled
    yield (
        [
            ':{\n',
            '    pudding\n',
            '}} ',
        ],
        0,
        0,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT | HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            1,
            0,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT | HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE |
                HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # format string code -> not in format string
    yield (
        [
            ':} ',
        ],
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
            None,
            False,
            [],
            False,
        ),
    )
    
    # format string postfix -> open braces
    yield (
        [
            '{:} ',
        ],
        0,
        1,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        [
            '{',
        ],
        [
            Token(TOKEN_TYPE_SPECIAL_PUNCTUATION, '{'),
        ],
        _try_match_format_string_code,
        (
            0,
            1,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            [
                '{',
            ],
            False,
            [],
            False,
        ),
    )
    
    # format string code -> start in middle
    yield (
        [
            '\n',
            '    :} ',
        ],
        1,
        4,
        (
            HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
            HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
        ),
        None,
        None,
        _try_match_format_string_code,
        (
            1,
            6,
            (
                HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING | HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE |
                HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT
            ),
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, ':'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
            ],
            True,
        ),
    )
    
    # ---- string ----
    
    # string -> empty
    yield (
        [],
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
            None,
            True,
            [],
            False,
        ),
    )
    
    # string ~ unicode -> actual
    yield (
        [
            '"pudding" ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            9,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
                Token(TOKEN_TYPE_STRING_UNICODE, 'pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
            ],
            True,
        ),
    )
    
    # string ~ unicode ~ single quote -> actual
    yield (
        [
            '\'pudding\' ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            9,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, '\''),
                Token(TOKEN_TYPE_STRING_UNICODE, 'pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE, '\''),
            ],
            True,
        ),
    )
    
    # string ~ raw unicode -> actual
    yield (
        [
            'r"pudding" ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            10,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, 'r"'),
                Token(TOKEN_TYPE_STRING_UNICODE, 'pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
            ],
            True,
        ),
    )
    
    # string ~ binary -> actual
    yield (
        [
            'b"pudding" ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            10,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_BINARY, 'b"'),
                Token(TOKEN_TYPE_STRING_BINARY, 'pudding'),
                Token(TOKEN_TYPE_STRING_BINARY, '"'),
            ],
            True,
        ),
    )
    
    # string ~ raw binary -> actual
    yield (
        [
            'rb"pudding" ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            11,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_BINARY, 'rb"'),
                Token(TOKEN_TYPE_STRING_BINARY, 'pudding'),
                Token(TOKEN_TYPE_STRING_BINARY, '"'),
            ],
            True,
        ),
    )
    
    # string ~ format unicode -> actual
    yield (
        [
            'f"pudding" ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            10,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'f"'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, '"'),
            ],
            True,
        ),
    )
    
    # string ~ raw format unicode -> actual
    yield (
        [
            'rf"pudding" ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            11,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'rf"'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, '"'),
            ],
            True,
        ),
    )
    
    # string ~ unicode -> other encapsulator in middle
    yield (
        [
            '"\'\'" ',
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
                Token(TOKEN_TYPE_STRING_UNICODE, '\'\''),
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
            ],
            True,
        ),
    )
    
    # string ~ unicode -> single line
    yield (
        [
            '""\n',
            '""\n',
            
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            2,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
            ],
            True,
        ),
    )
    
    # string ~ unicode -> multi line
    yield (
        [
            '"""\n',
            '    pudding"""\n',
            '',
            
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            1,
            14,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, '"""'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
                Token(TOKEN_TYPE_STRING_UNICODE, '    pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE, '"""'),
            ],
            True,
        ),
    )
    
    # string ~ unicode -> unclosed
    yield (
        [
            '"""\n',
            '    pudding\n',
            '',
            
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            3,
            0,
            0,
            None,
            True,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, '"""'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
                Token(TOKEN_TYPE_STRING_UNICODE, '    pudding'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # string ~ unicode -> multi line, multi line code disabled
    yield (
        [
            '"""pudding\n',
            '"""\n',
            '',
            
        ],
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE,
        None,
        None,
        _try_match_string,
        (
            1,
            0,
            HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, '"""'),
                Token(TOKEN_TYPE_STRING_UNICODE, 'pudding'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # string ~ unicode -> ignore escaped encapsulator
    yield (
        [
            '"\\"" ',
            
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            4,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
                Token(TOKEN_TYPE_STRING_UNICODE, '\\"'),
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
            ],
            True,
        ),
    )
    
    # string ~ unicode -> double quote, but disabled
    yield (
        [
            '"" ',
            
        ],
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS,
        None,
        None,
        _try_match_string,
        (
            0,
            0,
            HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS | HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE,
            None,
            True,
            [],
            True,
        ),
    )
    
    # string ~ unicode -> single quote, but disabled
    yield (
        [
            '\'\' ',
            
        ],
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS,
        None,
        None,
        _try_match_string,
        (
            0,
            0,
            HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS | HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE,
            None,
            True,
            [],
            True,
        ),
    )
    
    # string ~ format unicode -> with code in it
    yield (
        [
            'f"{pudding + mister}" ',
            
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            21,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'f"'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
                Token(TOKEN_TYPE_SPACE, ' '),
                Token(TOKEN_TYPE_SPECIAL_OPERATOR, '+'),
                Token(TOKEN_TYPE_SPACE, ' '),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'mister'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, '"'),
            ],
            True,
        ),
    )
    
    # string ~ format unicode -> multi-line code, but not allowed
    yield (
        [
            'f"{\n',
            'pudding\n',
            '}" ',
            
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            1,
            0,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'f"'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
            ],
            True,
        ),
    )
    
    # string ~ format unicode -> multi-line code, allowed
    yield (
        [
            'f"{\n',
            'pudding\n',
            '}" ',
            
        ],
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS,
        None,
        None,
        _try_match_string,
        (
            2,
            2,
            HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'f"'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
                Token(TOKEN_TYPE_IDENTIFIER_VARIABLE, 'pudding'),
                Token(TOKEN_TYPE_LINE_BREAK, '\n'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, '"'),
            ],
            True,
        ),
    )
    
    # string ~ format unicode -> string inside, allow different
    yield (
        [
            'f"{\'\'}" ',
            
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            7,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'f"'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
                Token(TOKEN_TYPE_STRING_UNICODE, '\''),
                Token(TOKEN_TYPE_STRING_UNICODE, '\''),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, '"'),
            ],
            True,
        ),
    )
    
    # string ~ format unicode -> string inside, allow same (relaxed)
    yield (
        [
            'f"{""}" ',
            
        ],
        0,
        0,
        HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS,
        None,
        None,
        _try_match_string,
        (
            0,
            7,
            HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'f"'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '}'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, '"'),
            ],
            True,
        ),
    )
    
    # string ~ format unicode -> string inside, disallow same (strict)
    yield (
        [
            'f"{""}" ',
            
        ],
        0,
        0,
        0,
        None,
        None,
        _try_match_string,
        (
            0,
            3,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT, 'f"'),
                Token(TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK, '{'),
            ],
            True,
        ),
    )
    
    # string -> start in middle
    yield (
        [
            '\n',
            '    "pudding" ',
        ],
        1,
        4,
        0,
        None,
        None,
        _try_match_string,
        (
            1,
            13,
            0,
            None,
            False,
            [
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
                Token(TOKEN_TYPE_STRING_UNICODE, 'pudding'),
                Token(TOKEN_TYPE_STRING_UNICODE, '"'),
            ],
            True,
        ),
    )
    


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__try_matchers(lines, line_index, line_character_index, flags, brace_nesting, tokens, matcher):
    """
    Tests whether try matchers work as intended.
    
    Parameters
    ----------
    lines : `list<str>`
        Lines to match from.
    
    line_index : `int`
        Line index to start matching at.
    
    line_character_index : `int`
        Character index to start matching at.
    
    flags : `int`
        Flags to match with.
    
    brace_nesting : `None | list<str>`
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
    
    brace_nesting : `None | list<str>`
        How the braces are nested.
    
    done : `bool`
        Whether matching is done.
    
    tokens : `list<Token>`
        Matched tokens.
    
    output : `bool`
        Whether matching was successful.
    """
    parser_context = HighlightParserContext(lines, flags)
    parser_context.line_index = line_index
    parser_context.line_character_index = line_character_index
    
    if (tokens is not None):
        parser_context.tokens.extend(tokens)
    
    if (brace_nesting is not None):
        parser_context.brace_nesting = brace_nesting.copy()
    
    output = matcher(parser_context)
    vampytest.assert_instance(output, bool)
    
    return (
        parser_context.line_index,
        parser_context.line_character_index,
        parser_context.flags,
        parser_context.brace_nesting,
        parser_context.done,
        parser_context.tokens[(0 if tokens is None else len(tokens)):],
        output,
    )
