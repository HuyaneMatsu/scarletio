__all__ = ()

from sys import version_info

HIGHLIGHT_PARSER_FLAG_DO_TRACK_BRACE_NESTING = 1 << 0
HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS = 1 << 1
HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS = 1 << 2
HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_STRING = 1 << 3
HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE = 1 << 4
HIGHLIGHT_PARSER_FLAG_IN_STRING_BINARY = 1 << 5
HIGHLIGHT_PARSER_FLAG_IN_STRING_UNICODE = 1 << 6
HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT = 1 << 7
HIGHLIGHT_PARSER_FLAG_IN_STRING_FORMAT_CODE = 1 << 8
HIGHLIGHT_PARSER_FLAG_HIT_MULTI_LINE_CODE = 1 << 9
HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS = 1 << 10
HIGHLIGHT_PARSER_FLAG_HIT_DISABLED_QUOTE = 1 << 11

HIGHLIGHT_PARSER_MASK_INHERITABLE = (
    HIGHLIGHT_PARSER_FLAG_NO_SINGLE_QUOTE_STRINGS | HIGHLIGHT_PARSER_FLAG_NO_DOUBLE_QUOTE_STRINGS |
    HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS | HIGHLIGHT_PARSER_FLAG_NO_MULTI_LINE_CODE
)


if version_info >= (3, 12):
    HIGHLIGHT_PARSER_MASK_DEFAULT = HIGHLIGHT_PARSER_FLAG_ALLOW_RELAXED_FORMAT_STRINGS
else:
    HIGHLIGHT_PARSER_MASK_DEFAULT = 0
