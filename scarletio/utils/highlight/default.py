__all__ = ('DEFAULT_ANSI_HIGHLIGHTER',)

from .formatter_context import HighlightFormatterContext
from .formatter_detail import FormatterDetailANSI
from .token_types import (
    TOKEN_TYPE_COMMENT, TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION, TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE,
    TOKEN_TYPE_CONSOLE_BANNER_LOGO, TOKEN_TYPE_CONSOLE_MARKER, TOKEN_TYPE_IDENTIFIER_ATTRIBUTE,
    TOKEN_TYPE_IDENTIFIER_BUILTIN, TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION, TOKEN_TYPE_IDENTIFIER_KEYWORD,
    TOKEN_TYPE_IDENTIFIER_MAGIC, TOKEN_TYPE_NON_SPACE, TOKEN_TYPE_NUMERIC, TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX,
    TOKEN_TYPE_SPECIAL_OPERATOR, TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE, TOKEN_TYPE_SPECIAL_PUNCTUATION,
    TOKEN_TYPE_STRING, TOKEN_TYPE_STRING_FORMAT_CODE, TOKEN_TYPE_STRING_FORMAT_MARK, TOKEN_TYPE_STRING_FORMAT_POSTFIX,
    TOKEN_TYPE_TEXT_NEGATIVE, TOKEN_TYPE_TEXT_NEUTRAL, TOKEN_TYPE_TEXT_POSITIVE, TOKEN_TYPE_TEXT_TITLE,
    TOKEN_TYPE_TEXT_UNKNOWN, TOKEN_TYPE_TRACE, TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE,
    TOKEN_TYPE_TRACE_LOCATION_LINE_NUMBER, TOKEN_TYPE_TRACE_LOCATION_NAME, TOKEN_TYPE_TRACE_LOCATION_PATH,
    TOKEN_TYPE_TRACE_TITLE
)


DEFAULT_ANSI_HIGHLIGHTER = HighlightFormatterContext()

# Add code highlights

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_NON_SPACE,
    FormatterDetailANSI(foreground_color = (220, 255, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_SPECIAL_OPERATOR,
    FormatterDetailANSI(foreground_color = (255, 199, 222)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_IDENTIFIER_MAGIC,
    FormatterDetailANSI(foreground_color = (122, 255, 244)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_NUMERIC,
    FormatterDetailANSI(foreground_color = (96, 0, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_STRING,
    FormatterDetailANSI(foreground_color = (174, 230, 151)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_IDENTIFIER_KEYWORD,
    FormatterDetailANSI(foreground_color = (255, 109, 109)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_IDENTIFIER_BUILTIN,
    FormatterDetailANSI(foreground_color = (0, 170, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_IDENTIFIER_BUILTIN_EXCEPTION,
    FormatterDetailANSI(foreground_color = (176, 88, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_SPECIAL_PUNCTUATION,
    FormatterDetailANSI(foreground_color = (157, 157, 255)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_SPECIAL_OPERATOR_ATTRIBUTE,
    FormatterDetailANSI(foreground_color = (255, 255, 194)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_IDENTIFIER_ATTRIBUTE,
    FormatterDetailANSI(foreground_color = (255, 255, 194)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_SPECIAL_CONSOLE_PREFIX,
    FormatterDetailANSI(foreground_color = (255, 121, 25)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_STRING_FORMAT_MARK,
    FormatterDetailANSI(foreground_color = (249, 17, 17)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_COMMENT,
    FormatterDetailANSI(foreground_color = (255, 152, 44)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_STRING_FORMAT_CODE,
    FormatterDetailANSI(foreground_color = (255, 152, 44)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_STRING_FORMAT_POSTFIX,
    FormatterDetailANSI(foreground_color = (155, 185, 243)),
)

# Add trace highlights

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TRACE,
    FormatterDetailANSI(foreground_color = (255, 220, 220)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TRACE_TITLE,
    FormatterDetailANSI(foreground_color = (235, 52, 113)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TRACE_LOCATION_PATH,
    FormatterDetailANSI(foreground_color = (72, 201, 202)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TRACE_LOCATION_LINE_NUMBER,
    FormatterDetailANSI(foreground_color = (151, 174, 230)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TRACE_LOCATION_NAME,
    FormatterDetailANSI(foreground_color = (151, 174, 230)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TRACE_EXCEPTION_REPR_GRAVE,
    FormatterDetailANSI(foreground_color = (237, 89, 26)),
)

# Add console highlights

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_CONSOLE_BANNER_LOGO,
    FormatterDetailANSI(foreground_color = (137, 17, 217)),
)

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION,
    FormatterDetailANSI(foreground_color = (207, 252, 239)),
)

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_CONSOLE_BANNER_DESCRIPTION_AWAIT_UNAVAILABLE,
    FormatterDetailANSI(foreground_color = (235, 52, 113)),
)
DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_CONSOLE_MARKER,
    FormatterDetailANSI(foreground_color = (78, 154, 6)),
)

# Add text highlights


DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TEXT_NEGATIVE,
    FormatterDetailANSI(foreground_color = (255, 0, 0)),
)

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TEXT_POSITIVE,
    FormatterDetailANSI(foreground_color = (0, 255, 0)),
)

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TEXT_NEUTRAL,
    FormatterDetailANSI(foreground_color = (0, 255, 255)),
)

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TEXT_UNKNOWN,
    FormatterDetailANSI(foreground_color = (255, 0, 255)),
)

DEFAULT_ANSI_HIGHLIGHTER.set_highlight_detail(
    TOKEN_TYPE_TEXT_TITLE,
    FormatterDetailANSI(foreground_color = (255, 251, 222)),
)
