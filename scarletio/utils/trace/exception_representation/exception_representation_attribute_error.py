__all__ = ('ExceptionRepresentationAttributeError',)

from ...docs import copy_docs

from .attribute_error_helpers import extract_attribute_error_fields
from .exception_representation_base import ExceptionRepresentationBase
from .representation_helpers import _get_type_name
from .suggestion import (
    exists_matching_variable_name, get_familiar_instance_attribute_names, get_matching_variable_names_with_attribute
)


class ExceptionRepresentationAttributeError(ExceptionRepresentationBase):
    """
    Holds a valid syntax error's representation.
    
    Attributes
    ----------
    attribute_name : `str`
        The attribute's name that was not present.
    instance_type_name : `str`
        The representation of the instance's type's name.
    suggestion_attribute_exists_just_was_not_set : `bool`
        Whether the instance should have an attribute with the given name.
    suggestion_familiar_attribute_names : `None | list<str>`
        Attributes of the same instance with familiar names.
    suggestion_matching_variable_exists : `bool`
        Variables of the same scope with the same name.
    suggestion_variable_names_with_attribute : `None | list<str>`
        Variables with an attribute with the same name.
    type_name : `str`
        The represented exception's type's name.
    """
    __slots__ = (
        'attribute_name', 'instance_type_name', 'suggestion_attribute_exists_just_was_not_set',
        'suggestion_familiar_attribute_names', 'suggestion_matching_variable_exists', 'suggestion_matching_variables',
        'suggestion_variable_names_with_attribute', 'type_name',
    )
    
    def __new__(cls, exception, frame):
        """
        Creates a new exception representation.
        
        Parameters
        ----------
        exception : `AttributeError`
            Exception to represent.
        frame : `None | FrameProxyBase`
            The frame the exception is raised from.
        """
        instance, attribute_name = extract_attribute_error_fields(exception)
        
        suggestion_attribute_exists_just_was_not_set, suggestion_familiar_attribute_names = (
            get_familiar_instance_attribute_names(instance, attribute_name)
        )
        suggestion_matching_variable_exists = exists_matching_variable_name(frame, attribute_name)
        suggestion_variable_names_with_attribute = get_matching_variable_names_with_attribute(frame, attribute_name)
        
        instance_type_name = _get_type_name(type(instance))
        type_name = _get_type_name(type(exception))
        
        self = object.__new__(cls)
        self.attribute_name = attribute_name
        self.instance_type_name = instance_type_name
        self.suggestion_attribute_exists_just_was_not_set = suggestion_attribute_exists_just_was_not_set
        self.suggestion_familiar_attribute_names = suggestion_familiar_attribute_names
        self.suggestion_matching_variable_exists = suggestion_matching_variable_exists
        self.suggestion_variable_names_with_attribute = suggestion_variable_names_with_attribute
        self.type_name = type_name
        return self
    
    
    @classmethod
    def from_fields(
        cls,
        *,
        attribute_name = ...,
        instance_type_name = ...,
        suggestion_attribute_exists_just_was_not_set = ...,
        suggestion_familiar_attribute_names = ...,
        suggestion_matching_variable_exists = ...,
        suggestion_variable_names_with_attribute = ...,
        type_name = ...,
    ):
        """
        Creates a new syntax error representation from the given fields.
        
        Attributes
        ----------
        attribute_name : `str`, Optional (Keyword only)
            The attribute's name that was not present.
        instance_type_name : `str`, Optional (Keyword only)
            The representation of the instance's type's name.
        suggestion_attribute_exists_just_was_not_set : `bool`, Optional (Keyword only)
            Whether the instance should have an attribute with the given name.
        suggestion_familiar_attribute_names : `None | list<str>`, Optional (Keyword only)
            Attributes of the same instance with familiar names.
        suggestion_matching_variable_exists : `bool`, Optional (Keyword only)
            Variables of the same scope with the same name.
        suggestion_variable_names_with_attribute : `None | list<str>`, Optional (Keyword only)
            Variables with an attribute with the same name.
        type_name : `str`, Optional (Keyword only)
            The represented exception's type's name.
        
        Returns
        -------
        self : `instance<cls>`
        """
        self = object.__new__(cls)
        self.attribute_name = '' if attribute_name is ... else attribute_name
        self.instance_type_name = '' if instance_type_name is ... else instance_type_name
        self.suggestion_attribute_exists_just_was_not_set = (
            False if suggestion_attribute_exists_just_was_not_set is ... else suggestion_attribute_exists_just_was_not_set
        )
        self.suggestion_familiar_attribute_names = (
            None if suggestion_familiar_attribute_names is ... else suggestion_familiar_attribute_names
        )
        self.suggestion_matching_variable_exists = (
            False if suggestion_matching_variable_exists is ... else suggestion_matching_variable_exists
        )
        self.suggestion_variable_names_with_attribute = (
            None if suggestion_variable_names_with_attribute is ... else suggestion_variable_names_with_attribute
        )
        self.type_name = AttributeError.__name__ if type_name is ... else type_name
        return self
    
    
    @copy_docs(ExceptionRepresentationBase._populate_repr_parts)
    def _populate_repr_parts(self, repr_parts):
        # type_name
        repr_parts.append(' type_name = ')
        repr_parts.append(repr(self.type_name))
        
        # instance_type_name
        repr_parts.append(', instance_type_name = ')
        repr_parts.append(repr(self.instance_type_name))
        
        # attribute_name
        repr_parts.append(', attribute_name = ')
        repr_parts.append(repr(self.attribute_name))
        
        # suggestion_attribute_exists_just_was_not_set
        suggestion_attribute_exists_just_was_not_set = self.suggestion_attribute_exists_just_was_not_set
        if suggestion_attribute_exists_just_was_not_set:
            repr_parts.append(', suggestion_attribute_exists_just_was_not_set = ')
            repr_parts.append(repr(suggestion_attribute_exists_just_was_not_set))
        
        # suggestion_familiar_attribute_names
        suggestion_familiar_attribute_names = self.suggestion_familiar_attribute_names
        if (suggestion_familiar_attribute_names is not None):
            repr_parts.append(', suggestion_familiar_attribute_names = ')
            repr_parts.append(repr(suggestion_familiar_attribute_names))
        
        # suggestion_matching_variable_exists
        suggestion_matching_variable_exists = self.suggestion_matching_variable_exists
        if suggestion_matching_variable_exists:
            repr_parts.append(', suggestion_matching_variable_exists = ')
            repr_parts.append(repr(suggestion_matching_variable_exists))
        
        # suggestion_variable_names_with_attribute
        suggestion_variable_names_with_attribute = self.suggestion_variable_names_with_attribute
        if (suggestion_variable_names_with_attribute is not None):
            repr_parts.append(', suggestion_variable_names_with_attribute = ')
            repr_parts.append(repr(suggestion_variable_names_with_attribute))
    
    
    @copy_docs(ExceptionRepresentationBase._is_equal)
    def _is_equal(self, other):
        if self.type_name != other.type_name:
            return False
        
        if self.attribute_name != other.attribute_name:
            return False
        
        if self.instance_type_name != other.instance_type_name:
            return False
        
        if self.suggestion_attribute_exists_just_was_not_set != other.suggestion_attribute_exists_just_was_not_set:
            return False
        
        if self.suggestion_familiar_attribute_names != other.suggestion_familiar_attribute_names:
            return False
        
        if self.suggestion_matching_variable_exists != other.suggestion_matching_variable_exists:
            return False
        
        if self.suggestion_variable_names_with_attribute != other.suggestion_variable_names_with_attribute:
            return False
        
        return True
