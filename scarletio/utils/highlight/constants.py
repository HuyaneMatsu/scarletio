__all__ = ()

from re import compile as re_compile
from sys import platform, version_info

from .word_pattern import create_word_pattern


COMPLEX_RP = re_compile(
    '((?:\\d(?:_?\\d)*\\.\\d(?:_?\\d)*|\\d(?:_?\\d)*\\.|\\.\\d(?:_?\\d)*)(?:[eE][+-]?\\d(?:_?\\d)*)?[jJ])'
)
FLOAT_RP = re_compile(
    '((?:\\d(?:_?\\d)*\\.\\d(?:_?\\d)*|\\d(?:_?\\d)*\\.|\\.\\d(?:_?\\d)*)(?:[eE][+-]?\\d(?:_?\\d)*)?)'
)
INTEGER_HEXADECIMAL_RP = re_compile('(0[xX](?:_?[0-9a-fA-F])+)')
INTEGER_DECIMAL_RP = re_compile('(\\d(?:_?\\d)*)')
INTEGER_OCTAL_RP = re_compile('(0[oO](?:_?[0-7])+)')
INTEGER_BINARY_RP = re_compile('(0[bB](?:_?[01])+)')
IDENTIFIER_RP = re_compile('([a-zA-Z_][a-zA-Z_0-9]*)')

ATTRIBUTE_ACCESS_OPERATOR = '.'
KEYWORD_ELLIPSIS = '...'
ESCAPE = '\\'

BUILTIN_CONSTANTS = {
    Ellipsis, False, None, NotImplemented, True
}

BUILTIN_CONSTANT_NAMES = {
    KEYWORD_ELLIPSIS,
    *(repr(value) for value in BUILTIN_CONSTANTS),
}

KEYWORDS = {
    'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
    'for', 'from', 'global', 'if', 'import', 'lambda', 'nonlocal', 'pass', 'raise', 'return', 'try', 'while', 'with',
    'yield'
}

BUILTIN_VARIABLES = {
    __import__, abs, all, any, ascii, bin, bool, bytearray, bytes, chr, classmethod, compile, complex, delattr, dict,
    dir, divmod, enumerate, eval, filter, float, format, frozenset, getattr, globals, hasattr, hash, hex, id, input,
    int, isinstance, issubclass, iter, len, list, locals, map, max, memoryview, min, next, object, oct, open, ord, pow,
    print, property, range, repr, reversed, round, set, setattr, slice, sorted, staticmethod, str, sum, super, tuple,
    type, vars, zip,
    *((aiter, anext) if version_info >= (3, 10) else ()),
}


BUILTIN_VARIABLE_NAMES = {
    value.__name__ for value in BUILTIN_VARIABLES
}

BUILTIN_EXCEPTIONS = {
    ArithmeticError, AssertionError, AttributeError, BaseException, BlockingIOError, BrokenPipeError, BufferError,
    BytesWarning, ChildProcessError, ConnectionAbortedError, ConnectionError, ConnectionRefusedError,
    ConnectionResetError, DeprecationWarning, EOFError, EnvironmentError, Exception, FileExistsError,
    FileNotFoundError, FloatingPointError, FutureWarning, GeneratorExit, IOError, ImportError, ImportWarning,
    IndentationError, IndexError, InterruptedError, IsADirectoryError, KeyError, KeyboardInterrupt, LookupError,
    MemoryError, NameError, NotADirectoryError, NotImplementedError, OSError, OverflowError, PendingDeprecationWarning,
    PermissionError, ProcessLookupError, RecursionError, ReferenceError, ResourceWarning, RuntimeError, RuntimeWarning,
    StopAsyncIteration, StopIteration, SyntaxError, SyntaxWarning, SystemError, SystemExit, TabError, TimeoutError,
    TypeError, UnboundLocalError, UnicodeDecodeError, UnicodeEncodeError, UnicodeError, UnicodeTranslateError,
    UnicodeWarning, UserWarning, ValueError, Warning, ZeroDivisionError,
    *((WindowsError,) if platform == 'win32' else ()),
    *((ModuleNotFoundError,) if version_info >= (3, 6) else ()),
    *((EncodingWarning,) if version_info >= (3, 10) else ()),
    *((BaseExceptionGroup, ExceptionGroup,) if version_info >= (3, 11) else ()),
    *((PythonFinalizationError,) if version_info >= (3, 13) else ()),
}

BUILTIN_EXCEPTION_NAMES = {
    value.__name__ for value in BUILTIN_EXCEPTIONS
}

MAGIC_FUNCTION_NAMES = {
    '__abs__', '__add__', '__aenter__', '__aexit__', '__aiter__', '__and__', '__anext__', '__await__', '__bool__',
    '__bytes__', '__call__', '__complex__', '__contains__', '__del__', '__delattr__', '__delete__', '__delitem__',
    '__dir__', '__divmod__', '__enter__', '__eq__', '__exit__', '__float__', '__floordiv__', '__format__', '__ge__',
    '__get__', '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__iadd__', '__iand__',
    '__ifloordiv__', '__ilshift__', '__imatmul__', '__imod__', '__imul__', '__index__', '__init__', '__instancecheck__',
    '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__', '__isub__', '__iter__', '__itruediv__', '__ixor__',
    '__le__', '__len__', '__length_hint__', '__lshift__', '__lt__', '__matmul__', '__missing__', '__mod__', '__mul__',
    '__ne__', '__neg__', '__new__', '__next__', '__or__', '__pos__', '__pow__', '__prepare__', '__radd__', '__rand__',
    '__rdivmod__', '__repr__', '__reversed__', '__rfloordiv__', '__rlshift__', '__rmatmul__', '__rmod__', '__rmul__',
    '__ror__', '__round__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__', '__rtruediv__', '__rxor__', '__set__',
    '__setattr__', '__setitem__', '__str__', '__sub__', '__subclasscheck__', '__truediv__', '__xor__'
}

MAGIC_VARIABLE_NAMES = {
    '__annotations__', '__bases__', '__class__', '__closure__', '__code__', '__defaults__', '__dict__', '__doc__',
    '__file__', '__func__', '__globals__', '__kwdefaults__', '__module__', '__mro__', '__name__', '__objclass__',
    '__qualname__', '__self__', '__slots__', '__weakref__'
}

PUNCTUATIONS = {
    '(', ')', ',', ':', ';', '[', ']', '{', '}'
}

OPERATOR_WORDS = {
    'and', 'in', 'is', 'not', 'or'
}

OPERATORS = {
    '!=', '%', '%=', '&', '&=', '*', '**', '**=', '*=', '+', '+=', '-', '-=', '->', '.', '...', '/', '//', '//=', '/=',
    '<', '<<', '<<=', '<=', '=', '==', '>', '>=', '>>', '>>=', '@', '@=', '\\', '^', '^=', '|', '|='
}

STRING_STARTER_RP = re_compile('(r[fb]?|[fb]r?|b|f)?(\'{3}|\"{3}|\'|\")')

SPACE_MATCH_RP = re_compile('([ \t]+)')

CONSOLE_PREFIX_RP = re_compile('(>>>>?|\\.\\.\\.\\.?| *\\.\\.\\.\\:|In \\[\\d+\\]\\:)( [ \t]*)')

FORMAT_STRING_POSTFIX_RP = re_compile('(![sraSRA])\\}')

PUNCTUATION_WP = create_word_pattern(PUNCTUATIONS)
OPERATOR_WP = create_word_pattern(OPERATORS)
