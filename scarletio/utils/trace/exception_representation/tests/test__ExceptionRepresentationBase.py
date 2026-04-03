import vampytest

from ..exception_representation_base import ExceptionRepresentationBase


def _assert_fields_set(exception_representation):
    """
    Asserts whether every fields are set of the exception representation.
    
    Parameters
    ----------
    exception_representation : ``ExceptionRepresentationBase``
        The exception representation to test.
    """
    vampytest.assert_instance(exception_representation, ExceptionRepresentationBase)
    

def test__ExceptionRepresentationBase__new():
    """
    Tests whether ``ExceptionRepresentationBase.__new__`` works as intended.
    """
    exception = Exception()
    
    exception_representation = ExceptionRepresentationBase(exception, None)
    _assert_fields_set(exception_representation)


def test__ExceptionRepresentationBase__from_fields():
    """
    Tests whether ``ExceptionRepresentationBase.from_fields`` works as intended.
    """
    exception_representation = ExceptionRepresentationBase.from_fields()
    _assert_fields_set(exception_representation)


def test__ExceptionRepresentationBase__repr():
    """
    Tests whether ``ExceptionRepresentationBase.__repr__`` works as intended.
    """
    exception_representation = ExceptionRepresentationBase.from_fields()
    
    output = repr(exception_representation)
    vampytest.assert_instance(output, str)


def test__ExceptionRepresentationBase__eq():
    """
    Tests whether ``ExceptionRepresentationBase.__eq__`` works as intended.
    """
    exception_representation = ExceptionRepresentationBase.from_fields()
    vampytest.assert_eq(exception_representation, exception_representation)
    vampytest.assert_ne(exception_representation, object())
