__all__ = ('IgnoreCaseString', )

import sys

from .docs import has_docs


@has_docs
class IgnoreCaseString(str):
    """
    Strings, which have their casing ignored.
    
    Attributes
    ----------
    _case_fold : `str`
        Case folded version of the string.
    """
    __slots__ = ('_case_fold', )
    
    @has_docs
    def __new__(cls, value = '', encoding = sys.getdefaultencoding(), errors = 'strict'):
        """
        Return an string which ignores casing. If object is not provided, returns the empty string. Otherwise, the
        behavior of ``IgnoreCaseString`` depends on whether encoding or errors is given, as follows.
        
        If neither encoding nor errors is given, `IgnoreCaseString(object)` returns `object.__str__()`, which is the
        "informal" or nicely printable string representation of object. For string objects, this is `string`. If
        object does not have a `__str__()` method, then `IgnoreCaseString()` falls back to returning `repr(object)`.
        
        If at least one of encoding or errors is given, object should be a `bytes-like` object. In this case, if object
        is a `byte-like` object, then `IgnoreCaseString(bytes, encoding, errors)` is equivalent to
        `bytes.decode(encoding, errors)`. Otherwise, the bytes object underlying the buffer object is obtained before
        calling `bytes.decode()`.
        
        Passing a `bytes-like` object to ``IgnoreCaseString`` without the encoding or errors parameters falls under the
        first case of returning the informal string representation.
        
        Parameters
        ----------
        value : `object` = `''`, Optional
            The value, what is representation or encoded version is returned.
        encoding : `str` = `sys.getdefaultencoding()`, Optional
            Encoding to use when decoding a `bytes-like`.
        errors : `str` = `'strict'`, Optional
            May be given to set a different error handling scheme when decoding from `bytes-like`. The default `errors`
            value is `'strict'`, meaning that encoding errors raise a `UnicodeError`. Other possible values are
            `'ignore'`, `'replace'`, `'xmlcharrefreplace'`, `'backslashreplace'` and any other name registered via
            `codecs.register_error()`.
        
        Returns
        -------
        self : ``IgnoreCaseString``
        """
        if type(value) is cls:
            return value
        
        if isinstance(value,(bytes, bytearray, memoryview)):
            value = str(value, encoding, errors)
        elif isinstance(value, str):
            pass
        else:
            value = str(value)
        
        self = str.__new__(cls, value)
        self._case_fold = str.casefold(value)
        return self
    
    @has_docs
    def __hash__(self):
        """Returns the string's hash value."""
        return hash(self._case_fold)
    
    @has_docs
    def __eq__(self, other):
        """Returns whether the two strings are equal."""
        other_type = other.__class__
        if other_type is type(self):
            other_value = other._case_fold
        elif other_type is str:
            other_value = other.casefold()
        elif issubclass(other, str):
            other_value = str.casefold(other)
        else:
            return NotImplemented
        
        return (self._case_fold == other_value)
