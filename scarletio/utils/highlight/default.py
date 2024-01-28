__all__ = ('DEFAULT_ANSI_HIGHLIGHTER',)

from .ansi import create_ansi_format_code
from .formatter_context import HighlightFormatterContext
from .token_types import (
    TOKEN_TYPE_COMMENT, TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION, TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE,
    TOKEN_TYPE_CONSOLE_BANNER_LOGO, TOKEN_TYPE_CONSOLE_MARKER, TOKEN_TYPE_IDENTIFIER_ATTRIBUTE,
    TOKEN_TYPE_IDENTIFIER_BUILTIN, TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION, TOKEN_TYPE_IDENTIFIER_KEYWORD,
    TOKEN_TYPE_IDENTIFIER_MAGIC, TOKEN_TYPE_NON_SPACE, TOKEN_TYPE_NUMERIC, TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX,
    TOKEN_TYPE_SPECIAL_OPERATOR, TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, TOKEN_TYPE_SPECIAL_PUNCTUATION,
    TOKEN_TYPE_STRING, TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE, TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK,
    TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX, TOKEN_TYPE_TRACE, TOKEN_TYPE_TRACE_LOCATION_LINE_NUMBER,
    TOKEN_TYPE_TRACE_LOCATION_NAME, TOKEN_TYPE_TRACE_LOCATION_PATH, TOKEN_TYPE_TRACE_TITLE,
    TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE
)


DEFAULT_ANSI_HIGHLIGHTER = HighlightFormatterContext()

# Add code highlights

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_NON_SPACE,
    create_ansi_format_code(foreground_color = (220, 255, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_SPECIAL_OPERATOR,
    create_ansi_format_code(foreground_color = (255, 199, 222)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_IDENTIFIER_MAGIC,
    create_ansi_format_code(foreground_color = (122, 255, 244)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_NUMERIC,
    create_ansi_format_code(foreground_color = (96, 0, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_STRING,
    create_ansi_format_code(foreground_color = (174, 230, 151)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_IDENTIFIER_KEYWORD,
    create_ansi_format_code(foreground_color = (255, 109, 109)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_IDENTIFIER_BUILTIN,
    create_ansi_format_code(foreground_color = (0, 170, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION,
    create_ansi_format_code(foreground_color = (176, 88, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_SPECIAL_PUNCTUATION,
    create_ansi_format_code(foreground_color = (157, 157, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE,
    create_ansi_format_code(foreground_color = (255, 255, 194)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_IDENTIFIER_ATTRIBUTE,
    create_ansi_format_code(foreground_color = (255, 255, 194)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX,
    create_ansi_format_code(foreground_color = (255, 121, 25)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_STRING_UNICODE_FORMAT_MARK,
    create_ansi_format_code(foreground_color = (249, 17, 17)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_COMMENT,
    create_ansi_format_code(foreground_color = (255, 152, 44)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_STRING_UNICODE_FORMAT_CODE,
    create_ansi_format_code(foreground_color = (255, 152, 44)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_STRING_UNICODE_FORMAT_POSTFIX,
    create_ansi_format_code(foreground_color = (155, 185, 243)),
)

# Add trace highlights

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_TRACE,
    create_ansi_format_code(foreground_color = (255, 220, 220)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_TRACE_TITLE,
    create_ansi_format_code(foreground_color = (235, 52, 113)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_TRACE_LOCATION_PATH,
    create_ansi_format_code(foreground_color = (174, 230, 151)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_TRACE_LOCATION_LINE_NUMBER,
    create_ansi_format_code(foreground_color = (151, 174, 230)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_TRACE_LOCATION_NAME,
    create_ansi_format_code(foreground_color = (151, 174, 230)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE,
    create_ansi_format_code(foreground_color = (237, 89, 26)),
)

# Add console highlights

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_CONSOLE_BANNER_LOGO,
    create_ansi_format_code(foreground_color = (137, 17, 217)),
)

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION,
    create_ansi_format_code(foreground_color = (207, 252, 239)),
)

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE,
    create_ansi_format_code(foreground_color = (235, 52, 113)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_ansi_code(
    TOKEN_TYPE_CONSOLE_MARKER,
    create_ansi_format_code(foreground_color = (174, 230, 151)),
)
