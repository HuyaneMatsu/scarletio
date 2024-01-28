__all__ = ()

from builtins import AttributeError as PlainAttributeError

from ...rich_attribute_error import ATTRIBUTE_ERROR_HAS_RICH_SLOTS, AttributeError as RichAttributeError


INSTANCE_SLOT = RichAttributeError.instance
ATTRIBUTE_NAME_SLOT = RichAttributeError.attribute_name


def is_attribute_error(exception):
    """
    Returns whether the given exception is an attribute error.
    
    Parameters
    ----------
    exception : `BaseException`
        The exception to check.
    
    Returns
    -------
    is_attribute_error : `bool`
    """
    # Case 0: are we rich?
    if issubclass(type(exception), RichAttributeError):
        attribute_name = exception.attribute_name
    
    # Case 1: are we plain?
    elif ATTRIBUTE_ERROR_HAS_RICH_SLOTS and issubclass(type(exception), PlainAttributeError):
        # Since it is set in C it should be always set.
        attribute_name = ATTRIBUTE_NAME_SLOT.__get__(exception, type(exception))
    
    # Case 2: we cant be good
    else:
        return False
    
    if (attribute_name is None) or not isinstance(attribute_name, str):
        return False
    
    return True


def extract_attribute_error_fields(exception):
    """
    Extracts the attribute error's context fields.
    
    Parameters
    ----------
    exception : `AttributeError`
        The exception to get its fields of.
    
    Returns
    -------
    instance : `object`
    attribute_name : `str`
    """
    instance = INSTANCE_SLOT.__get__(exception, type(exception))
    
    attribute_name = ATTRIBUTE_NAME_SLOT.__get__(exception, type(exception))
    if type(attribute_name) is not str:
        attribute_name = str(attribute_name)
    
    return instance, attribute_name
