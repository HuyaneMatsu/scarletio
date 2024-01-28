__all__ = ('get_exception_representation',)

from .attribute_error_helpers import is_attribute_error
from .exception_helpers import is_exception
from .exception_representation_attribute_error import ExceptionRepresentationAttributeError
from .exception_representation_generic import ExceptionRepresentationGeneric
from .exception_representation_syntax_error import ExceptionRepresentationSyntaxError
from .syntax_error_helpers import is_syntax_error



SELECTORS = [
    (is_attribute_error, ExceptionRepresentationAttributeError),
    (is_syntax_error, ExceptionRepresentationSyntaxError),
    (is_exception, ExceptionRepresentationGeneric),
]


def get_exception_representation(exception, frame):
    """
    Gets the given exception's representation.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to get its representation of.
    frame : `None | FrameProxyBase`
        The frame the exception is raised from.
    
    Returns
    -------
    exception_representation : `None | ExceptionRepresentationBase`
    """
    for checker, representation_type in SELECTORS:
        if checker(exception):
            return representation_type(exception, frame)
    
    return None
