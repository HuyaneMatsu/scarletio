import vampytest

from ..exception_representation_generic import ExceptionRepresentationGeneric
from ..exception_representation_syntax_error import ExceptionRepresentationSyntaxError
from ..selection import get_exception_representation


def test__get_exception_representation__syntax_error():
    """
    Tests whether ``get_exception_representation`` works as intended.
    
    Case: syntax error.
    """
    exception = SyntaxError()
    exception.args = ('invalid syntax', ('<string>', 1, 1, 'for n in range(10):\n', 1, 4))
    
    output = get_exception_representation(exception, None)
    
    vampytest.assert_instance(output, ExceptionRepresentationSyntaxError)


def test__get_exception_representation__generic():
    """
    Tests whether ``get_exception_representation`` works as intended.
    
    Case: generic.
    """
    exception = ValueError()
    
    output = get_exception_representation(exception, None)
    
    vampytest.assert_instance(output, ExceptionRepresentationGeneric)


def test__get_exception_representation__invalid():
    """
    Tests whether ``get_exception_representation`` works as intended.
    
    Case: invalid input.
    """
    exception = object()
    
    output = get_exception_representation(exception, None)
    
    vampytest.assert_instance(output, type(None))
