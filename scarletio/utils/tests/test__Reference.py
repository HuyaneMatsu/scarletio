import vampytest

from ..reference import Reference


def test__Reference__new():
    """
    Tests whether ``Reference.__new__`` works as intended.
    """
    value = 6
    
    reference = Reference(value)
    
    vampytest.assert_instance(reference, Reference)
    vampytest.assert_eq(reference.value, value)


def test__Reference__value__read_write():
    """
    Tests whether ``Reference.value`` can be read and written.
    """
    value = 6
    
    reference = Reference(0)
    reference.value = value
    
    vampytest.assert_eq(reference.value, value)


def test__Reference__eq():
    """
    Tests whether ``Reference.__eq__`` works as intended.
    """
    value_0 = 56
    value_1 = 12
    
    reference_0 = Reference(value_0)
    reference_1 = Reference(value_1)
    
    vampytest.assert_eq(reference_0, reference_0)
    vampytest.assert_ne(reference_0, reference_1)


def test__Reference__repr():
    """
    Tests whether ``Reference.__repr__`` works as intended.
    """
    value = 62
    
    reference = Reference(value)
    
    output = repr(reference)
    vampytest.assert_instance(output, str)
    vampytest.assert_in(repr(value), output)
