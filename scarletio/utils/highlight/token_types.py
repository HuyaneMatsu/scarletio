"""
The token types for coloring are the following:

+-----------------------------------------------------------+-------+-----------------------------------------------+
| Respective name                                           | Value | Parent's respective name                      |
+===========================================================+=======+===============================================+
| TOKEN_TYPE_ALL                                            |   0   | N/A                                           |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_SPACE                                          |   1   | TOKEN_TYPE_ALL                                |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_LINEBREAK                                      |   2   | TOKEN_TYPE_ALL                                |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NON_SPACE                                      |   3   | TOKEN_TYPE_ALL                                |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NON_SPACE_UNIDENTIFIED                         |   4   | TOKEN_TYPE_NON_SPACE                          |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_COMMENT                                        |   5   | TOKEN_TYPE_ALL                                |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_LINEBREAK_ESCAPED                              |   6   | TOKEN_TYPE_LINEBREAK                          |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSTANT                                       | 100   | TOKEN_TYPE_NON_SPACE                          |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NUMERIC                                        | 110   | TOKEN_TYPE_CONSTANT                           |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NUMERIC_FLOAT                                  | 111   | TOKEN_TYPE_NUMERIC                            |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX                          | 112   | TOKEN_TYPE_NUMERIC_FLOAT                      |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NUMERIC_INTEGER                                | 113   | TOKEN_TYPE_NUMERIC                            |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL                    | 114   | TOKEN_TYPE_NUMERIC_INTEGER                    |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL                        | 115   | TOKEN_TYPE_NUMERIC_INTEGER                    |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NUMERIC_INTEGER_OCTAL                          | 116   | TOKEN_TYPE_NUMERIC_INTEGER                    |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_NUMERIC_INTEGER_BINARY                         | 117   | TOKEN_TYPE_NUMERIC_INTEGER                    |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_STRING                                         | 120   | TOKEN_TYPE_CONSTANT                           |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_STRING_BINARY                                  | 121   | TOKEN_TYPE_STRING                             |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_STRING_UNICODE                                 | 122   | TOKEN_TYPE_STRING                             |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_STRING_UNICODE_FORMAT                          | 123   | TOKEN_TYPE_STRING_UNICODE                     |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK                     | 124   | TOKEN_TYPE_STRING_UNICODE_FORMAT              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE                     | 125   | TOKEN_TYPE_STRING_UNICODE_FORMAT              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX                  | 126   | TOKEN_TYPE_STRING_UNICODE_FORMAT              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER                                     | 200   | TOKEN_TYPE_NON_SPACE                          |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_VARIABLE                            | 201   | TOKEN_TYPE_IDENTIFIER                         |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_ATTRIBUTE                           | 202   | TOKEN_TYPE_IDENTIFIER                         |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_KEYWORD                             | 210   | TOKEN_TYPE_IDENTIFIER                         |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_BUILTIN                             | 220   | TOKEN_TYPE_IDENTIFIER                         |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE                    | 221   | TOKEN_TYPE_IDENTIFIER_BUILTIN                 |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT                    | 222   | TOKEN_TYPE_IDENTIFIER_BUILTIN                 |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION                   | 223   | TOKEN_TYPE_IDENTIFIER_BUILTIN                 |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_MAGIC                               | 230   | TOKEN_TYPE_IDENTIFIER                         |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION                      | 231   | TOKEN_TYPE_IDENTIFIER_MAGIC                   |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE                      | 232   | TOKEN_TYPE_IDENTIFIER_MAGIC                   |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_SPECIAL                                        | 300   | TOKEN_TYPE_NON_SPACE                          |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_SPECIAL_OPERATOR                               | 301   | TOKEN_TYPE_SPECIAL                            |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE                     | 302   | TOKEN_TYPE_SPECIAL_OPERATOR                   |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_SPECIAL_PUNCTUATION                            | 303   | TOKEN_TYPE_SPECIAL                            |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_SPECIAL_OPERATOR_WORD                          | 304   | TOKEN_TYPE_SPECIAL_OPERATOR                   |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX                         | 305   | TOKEN_TYPE_SPECIAL                            |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE                                          | 1000  | TOKEN_TYPE_ALL                                |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_TITLE                                    | 1100  | TOKEN_TYPE_TRACE                              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_TITLE_ADDITIONAL                         | 1110  | TOKEN_TYPE_TRACE_TITLE                        |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_TITLE_ADDITIONAL_BEFORE                  | 1111  | TOKEN_TYPE_TRACE_TITLE_ADDITIONAL             |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_TITLE_ADDITIONAL_AFTER                   | 1112  | TOKEN_TYPE_TRACE_TITLE_ADDITIONAL             |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_TITLE_EXCEPTION                          | 1120  | TOKEN_TYPE_TRACE_TITLE                        |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_TITLE_EXCEPTION_START                    | 1121  | TOKEN_TYPE_TRACE_TITLE_EXCEPTION              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR                     | 1122  | TOKEN_TYPE_TRACE_TITLE_EXCEPTION              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE                     | 1123  | TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR         |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE_AFFIX               | 1124  | TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE         |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE_FILLING             | 1124  | TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE         |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_LOCATION                                 | 1200  | TOKEN_TYPE_TRACE                              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_LOCATION_PATH                            | 1201  | TOKEN_TYPE_TRACE_LOCATION                     |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_LOCATION_LINE_NUMBER                     | 1202  | TOKEN_TYPE_TRACE_LOCATION                     |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_LOCATION_NAME                            | 1203  | TOKEN_TYPE_TRACE_LOCATION                     |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_FRAME                                    | 1300  | TOKEN_TYPE_TRACE                              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_TRACE_FRAME_REPEAT                             | 1301  | TOKEN_TYPE_TRACE_FRAME                        |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE                                        | 2000  | TOKEN_TYPE_ALL                                |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_BANNER                                 | 2100  | TOKEN_TYPE_CONSOLE                            |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_BANNER_LOGO                            | 2110  | TOKEN_TYPE_CONSOLE_BANNER                     |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_BANNER_LOGO_VERSION                    | 2111  | TOKEN_TYPE_CONSOLE_BANNER_LOGO                |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION                     | 2120  | TOKEN_TYPE_CONSOLE_BANNER                     |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT               | 2121  | TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION         |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE   | 2122  | TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT   |
+-----------------------------------------------------------+-------+-----------------------------------------------+     
| TOKEN_TYPE_CONSOLE_MARKER                                 | 2200  | TOKEN_TYPE_CONSOLE                            |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_MARKER_IN                              | 2210  | TOKEN_TYPE_CONSOLE_MARKER                     |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_MARKER_IN_INITIAL                      | 2211  | TOKEN_TYPE_CONSOLE_MARKER_IN                  |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_MARKER_IN_CONTINUOUS                   | 2212  | TOKEN_TYPE_CONSOLE_MARKER_IN                  |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_MARKER_PREFIX                          | 2220  | TOKEN_TYPE_CONSOLE_MARKER                     |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_MARKER_PREFIX_INITIAL                  | 2221  | TOKEN_TYPE_CONSOLE_MARKER_PREFIX              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
| TOKEN_TYPE_CONSOLE_MARKER_PREFIX_CONTINUOUS               | 2222  | TOKEN_TYPE_CONSOLE_MARKER_PREFIX              |
+-----------------------------------------------------------+-------+-----------------------------------------------+
"""
__all__ = ()


TOKEN_TYPE_ALL = 0
TOKEN_TYPE_SPACE = 1
TOKEN_TYPE_LINEBREAK = 2
TOKEN_TYPE_NON_SPACE = 3
TOKEN_TYPE_NON_SPACE_UNIDENTIFIED = 4
TOKEN_TYPE_COMMENT = 5
TOKEN_TYPE_LINEBREAK_ESCAPED = 6

TOKEN_TYPE_CONSTANT = 100
TOKEN_TYPE_NUMERIC = 110
TOKEN_TYPE_NUMERIC_FLOAT = 111
TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX = 112
TOKEN_TYPE_NUMERIC_INTEGER = 113
TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL = 114
TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL = 115
TOKEN_TYPE_NUMERIC_INTEGER_OCTAL = 116
TOKEN_TYPE_NUMERIC_INTEGER_BINARY = 117
TOKEN_TYPE_STRING = 120
TOKEN_TYPE_STRING_BINARY = 121
TOKEN_TYPE_STRING_UNICODE = 122
TOKEN_TYPE_STRING_UNICODE_FORMAT = 123
TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK = 124
TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE = 125
TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX = 126

TOKEN_TYPE_IDENTIFIER = 200
TOKEN_TYPE_IDENTIFIER_VARIABLE = 201
TOKEN_TYPE_IDENTIFIER_ATTRIBUTE = 202
TOKEN_TYPE_IDENTIFIER_KEYWORD = 210
TOKEN_TYPE_IDENTIFIER_BUILTIN = 220
TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE = 221
TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT = 222
TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION = 223
TOKEN_TYPE_IDENTIFIER_MAGIC = 230
TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION = 231
TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE = 232

TOKEN_TYPE_SPECIAL = 300
TOKEN_TYPE_SPECIAL_OPERATOR = 301
TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE = 302
TOKEN_TYPE_SPECIAL_PUNCTUATION = 303
TOKEN_TYPE_SPECIAL_OPERATOR_WORD = 304
TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX = 305

# TRACE TYPES

TOKEN_TYPE_TRACE = 1000

TOKEN_TYPE_TRACE_TITLE = 1100
TOKEN_TYPE_TRACE_TITLE_ADDITIONAL = 1110
TOKEN_TYPE_TRACE_TITLE_ADDITIONAL_BEFORE = 1111
TOKEN_TYPE_TRACE_TITLE_ADDITIONAL_AFTER = 1112
TOKEN_TYPE_TRACE_TITLE_EXCEPTION = 1120
TOKEN_TYPE_TRACE_TITLE_EXCEPTION_START = 1121
TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR = 1122

TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE = 1123
TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE_AFFIX = 1124
TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE_FILLING = 1125

TOKEN_TYPE_TRACE_LOCATION = 1200
TOKEN_TYPE_TRACE_LOCATION_PATH = 1201
TOKEN_TYPE_TRACE_LOCATION_LINE_NUMBER = 1202
TOKEN_TYPE_TRACE_LOCATION_NAME = 1203

TOKEN_TYPE_TRACE_FRAME = 1300
TOKEN_TYPE_TRACE_FRAME_REPEAT = 1301

# CONSOLE

TOKEN_TYPE_CONSOLE = 2000

TOKEN_TYPE_CONSOLE_BANNER = 2100
TOKEN_TYPE_CONSOLE_BANNER_LOGO = 2110
TOKEN_TYPE_CONSOLE_BANNER_LOGO_VERSION = 2111
TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION = 2120
TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT = 2121
TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE = 2122

TOKEN_TYPE_CONSOLE_MARKER = 2200
TOKEN_TYPE_CONSOLE_MARKER_IN = 2210
TOKEN_TYPE_CONSOLE_MARKER_IN_INITIAL = 2211
TOKEN_TYPE_CONSOLE_MARKER_IN_CONTINUOUS = 2212
TOKEN_TYPE_CONSOLE_MARKER_PREFIX = 2220
TOKEN_TYPE_CONSOLE_MARKER_PREFIX_INITIAL = 2221
TOKEN_TYPE_CONSOLE_MARKER_PREFIX_CONTINUOUS = 2222


TOKEN_STRUCTURE = {
    TOKEN_TYPE_ALL: {
        TOKEN_TYPE_SPACE : None,
        TOKEN_TYPE_LINEBREAK : {
            TOKEN_TYPE_LINEBREAK_ESCAPED : None,
        },
        TOKEN_TYPE_NON_SPACE : {
            TOKEN_TYPE_NON_SPACE_UNIDENTIFIED : None,
            TOKEN_TYPE_CONSTANT : {
                TOKEN_TYPE_NUMERIC : {
                    TOKEN_TYPE_NUMERIC_FLOAT : {
                        TOKEN_TYPE_NUMERIC_FLOAT_COMPLEX : None,
                    },
                    TOKEN_TYPE_NUMERIC_INTEGER : {
                        TOKEN_TYPE_NUMERIC_INTEGER_HEXADECIMAL : None,
                        TOKEN_TYPE_NUMERIC_INTEGER_DECIMAL : None,
                        TOKEN_TYPE_NUMERIC_INTEGER_OCTAL : None,
                        TOKEN_TYPE_NUMERIC_INTEGER_BINARY : None,
                    },
                    TOKEN_TYPE_STRING : {
                        TOKEN_TYPE_STRING_BINARY : None,
                        TOKEN_TYPE_STRING_UNICODE : {
                            TOKEN_TYPE_STRING_UNICODE_FORMAT : {
                                TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK : None,
                                TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE : None,
                                TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX : None,
                            },
                        },
                    },
                },
            },
            TOKEN_TYPE_IDENTIFIER : {
                TOKEN_TYPE_IDENTIFIER_VARIABLE : None,
                TOKEN_TYPE_IDENTIFIER_ATTRIBUTE : None,
                TOKEN_TYPE_IDENTIFIER_KEYWORD : None,
                TOKEN_TYPE_IDENTIFIER_BUILTIN : {
                    TOKEN_TYPE_IDENTIFIER_BUILTIN_VARIABLE : None,
                    TOKEN_TYPE_IDENTIFIER_BUILTIN_CONSTANT : None,
                    TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION : None,
                },
                TOKEN_TYPE_IDENTIFIER_MAGIC : {
                    TOKEN_TYPE_IDENTIFIER_MAGIC_FUNCTION : None,
                    TOKEN_TYPE_IDENTIFIER_MAGIC_VARIABLE : None,
                },
            },
            TOKEN_TYPE_SPECIAL : {
                TOKEN_TYPE_SPECIAL_OPERATOR : {
                    TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE : None,
                    TOKEN_TYPE_SPECIAL_OPERATOR_WORD : None,
                },
                TOKEN_TYPE_SPECIAL_PUNCTUATION : None,
                TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX : None,
            },
        },
        TOKEN_TYPE_COMMENT : None,
    },
    TOKEN_TYPE_TRACE : {
        TOKEN_TYPE_TRACE_TITLE : {
            TOKEN_TYPE_TRACE_TITLE_ADDITIONAL: {
                TOKEN_TYPE_TRACE_TITLE_ADDITIONAL_BEFORE : None,
                TOKEN_TYPE_TRACE_TITLE_ADDITIONAL_AFTER : None,
            },
            TOKEN_TYPE_TRACE_TITLE_EXCEPTION : {
                TOKEN_TYPE_TRACE_TITLE_EXCEPTION_START : None,
                TOKEN_TYPE_TRACE_TITLE_EXCEPTION_REPR : {            
                    TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE : {
                        TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE_AFFIX : None,
                        TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE_FILLING : None,
                    },
                }
            },
        },
        TOKEN_TYPE_TRACE_LOCATION : {
            TOKEN_TYPE_TRACE_LOCATION_PATH : None,
            TOKEN_TYPE_TRACE_LOCATION_LINE_NUMBER : None,
            TOKEN_TYPE_TRACE_LOCATION_NAME : None,
        },
        TOKEN_TYPE_TRACE_FRAME : {
            TOKEN_TYPE_TRACE_FRAME_REPEAT : None,
        },
    },
    TOKEN_TYPE_CONSOLE : {
        TOKEN_TYPE_CONSOLE_BANNER : {
            TOKEN_TYPE_CONSOLE_BANNER_LOGO : {
                TOKEN_TYPE_CONSOLE_BANNER_LOGO_VERSION : None
            },
            TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION : {
                TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT : {
                    TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE : None
                },
            },
        },
        TOKEN_TYPE_CONSOLE_MARKER : {
            TOKEN_TYPE_CONSOLE_MARKER_IN : {
                TOKEN_TYPE_CONSOLE_MARKER_IN_INITIAL : None,
                TOKEN_TYPE_CONSOLE_MARKER_IN_CONTINUOUS : None,
            },
            TOKEN_TYPE_CONSOLE_MARKER_PREFIX : {
                TOKEN_TYPE_CONSOLE_MARKER_PREFIX_INITIAL : None,
                TOKEN_TYPE_CONSOLE_MARKER_PREFIX_CONTINUOUS : None,
            }
        },
    },
}


MERGE_TOKEN_TYPES = {
    # Strings are usually added as 3 parts, prefix + encapsulator | content | prefix + encapsulator
    TOKEN_TYPE_STRING,
    TOKEN_TYPE_STRING_BINARY,
    TOKEN_TYPE_STRING_UNICODE,
    TOKEN_TYPE_STRING_UNICODE_FORMAT,
    TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK,
    TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE,
    # At the case of special characters it not really matters
    TOKEN_TYPE_SPECIAL,
    TOKEN_TYPE_SPECIAL_OPERATOR,
    TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE,
    TOKEN_TYPE_SPECIAL_PUNCTUATION,
    TOKEN_TYPE_SPECIAL_OPERATOR_WORD,
    # Yes, space may be duped as well.
    TOKEN_TYPE_SPACE,
}
