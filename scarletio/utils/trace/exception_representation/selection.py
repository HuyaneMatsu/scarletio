__all__ = ('get_exception_representation',)

from .exception_representation_generic import ExceptionRepresentationGeneric
from .exception_representation_syntax_error import ExceptionRepresentationSyntaxError
from .syntax_error_helpers import is_syntax_error


def get_exception_representation(exception):
    """
    Gets the given exception's representation.
    
    Parameters
    ----------
    exception : ``BaseException``
        The exception to get its representation of.
    
    Returns
    -------
    exception_representation : `None | ExceptionRepresentationBase`
    """
    if is_syntax_error(exception):
        return ExceptionRepresentationSyntaxError(exception)
    
    if issubclass(type(exception), BaseException):
        return ExceptionRepresentationGeneric(exception)
    
    return None
