__all__ = (
    'AttributeError', 'AttributeErrorBase', 'RICH_TYPE_FEATURE_FLAG_ATTRIBUTE_ERROR', 'RICH_TYPE_FEATURE_FLAG_EQUAL',
    'RICH_TYPE_FEATURE_FLAG_REPRESENTATION', 'RichAttributeErrorBaseType', 'RichType'
)


ATTRIBUTE_ERROR_HAS_RICH_SLOTS = hasattr(AttributeError, 'obj') and hasattr(AttributeError, 'name')
AttributeErrorBase = AttributeError


class AttributeError(AttributeError):
    """
    Represents a rich attribute error.
    
    Parameters
    ----------
    attribute_name : `str`
        The attribute's name that was not found.
    instance : `object`
        The instance that does not have the respective attribute.
    """
    if ATTRIBUTE_ERROR_HAS_RICH_SLOTS:
        __slots__ = ()
        
        attribute_name = AttributeErrorBase.name
        instance = AttributeErrorBase.obj
    else:
        __slots__ = ('attribute_name', 'instance')
    
    def __new__(cls, instance, attribute_name):
        self = AttributeErrorBase.__new__(cls, instance, attribute_name)
        self.instance = instance
        self.attribute_name = attribute_name
        return self
    
    __init__ = object.__init__
    
    
    def __repr__(self):
        """Returns the attribute error's representations."""
        repr_parts = ['<', type(self).__name__]
        
        repr_parts.append(' instance = ')
        repr_parts.append(repr(self.instance))
        
        repr_parts.append(', attribute_name = ')
        repr_parts.append(repr(self.attribute_name))
        
        repr_parts.append('>')
        return ''.join(repr_parts)


def rich_getattr(self, attribute_name):
    raise AttributeError(self, attribute_name)


def rich_eq(self, other):
    self_type = type(self)
    if self_type is not type(other):
        return NotImplemented
    
    slot_descriptors = self_type.__slot_descriptors__
    if (slot_descriptors is not None):
        for slot_descriptor in slot_descriptors:
            if slot_descriptor.__get__(self, self_type) != slot_descriptor.__get__(other, self_type):
                return False
    
    return True


def rich_repr(self):
    self_type = type(self)
    parts = ['<', self_type.__name__]
    
    field_added = False
    
    slot_descriptors = self_type.__slot_descriptors__
    if (slot_descriptors is not None):
        for slot_descriptor in slot_descriptors:
            if field_added:
                parts.append(',')
            else:
                field_added = True
            
            parts.append(' ')
            parts.append(slot_descriptor.__name__)
            parts.append(' = ')
            parts.append(repr(slot_descriptor.__get__(self, self_type)))
    
    parts.append('>')
    return ''.join(parts)


def rich_hash(self):
    self_type = type(self)
    hash_value = 0
    
    slot_descriptors = self_type.__slot_descriptors__
    if (slot_descriptors is not None):
        for shift, slot_descriptor in enumerate(slot_descriptors):
            slot_value = slot_descriptor.__get__(self, self_type)
            try:
                slot_hash_value = hash(slot_value)
            except BaseException as exception:
                # Must have the
                if type(exception) is not TypeError:
                    raise
                
                # Must contain only this frame.
                if exception.__traceback__.tb_next is not None:
                    raise
                
                # MUst have the correct parameters
                exception_parameters = exception.args
                if len(exception_parameters) != 1:
                    raise
                
                maybe_exception_message = exception_parameters[0]
                if type(maybe_exception_message) is not str:
                    raise
                
                if not maybe_exception_message.startswith('unhashable type: '):
                    raise
                
                # Looks good.
                slot_hash_value = object.__hash__(slot_value)
            
            # Rotate the hash value by shift
            slot_hash_value = (slot_hash_value >> (64 - shift)) | ((slot_hash_value << shift) & ((1 << 64) - 1))
            
            hash_value ^= slot_hash_value
    
    return hash_value


RICH_TYPE_FEATURE_FLAG_ATTRIBUTE_ERROR = 1 << 0
RICH_TYPE_FEATURE_FLAG_EQUAL = 1 << 1
RICH_TYPE_FEATURE_FLAG_REPRESENTATION = 1 << 2
RICH_TYPE_FEATURE_FLAG_HASH = 1 << 3



def _get_parent_or_own_function(type_parents, type_attributes, function_name):
    """
    Gets the parents or own function.
    
    Parameters
    ----------
    type_parents : `tuple<type>`
        The sub-types of the creates type.
    
    type_attributes : `dict<str, object>`
        The type attributes of the created type.
    
    Returns
    -------
    function : `None | FunctionType`
    """
    try:
        return type_attributes[function_name]
    except KeyError:
        pass
    
    default = getattr(object, function_name, None)
    
    for type_parent in type_parents:
        try:
            parent_function = getattr(type_parent, function_name)
        except AttributeErrorBase:
            continue
        
        if (default is not None) and (parent_function is default):
            continue
        
        return parent_function


class RichType(type):
    def __new__(
        cls,
        type_name,
        type_parents,
        type_attributes,
        *,
        rich_type_feature_flags = 0,
    ):
        """
        You :know: what this does.
        
        Parameters
        ----------
        type_name : `str`
            The created type's name.
        
        type_parents : `tuple<type>`
            The sub-types of the creates type.
        
        type_attributes : `dict<str, object>`
            The type attributes of the created type.
        
        rich_type_feature_flags : `int` = `0`, Optional (Keyword only)
            Which features should be added and which should not.
        """
        slot_descriptors = None
        for parent in type_parents:
            if isinstance(parent, RichType):
                parent_slot_descriptors = parent.__dict__['__slot_descriptors__']
                if (parent_slot_descriptors is not None):
                    if slot_descriptors is None:
                        slot_descriptors = []
                    
                    slot_descriptors.extend(parent_slot_descriptors)
        
        # This will be populated only after the instance is created,
        # because the descriptors are created in the underlaying C code.
        type_attributes['__slot_descriptors__'] = None
        
        # Add
        if (
            (rich_type_feature_flags & RICH_TYPE_FEATURE_FLAG_ATTRIBUTE_ERROR) and
            (_get_parent_or_own_function(type_parents, type_attributes, '__getattr__') is None)
        ):
            type_attributes['__getattr__'] = rich_getattr
        
        if (
            (rich_type_feature_flags & RICH_TYPE_FEATURE_FLAG_EQUAL) and
            (_get_parent_or_own_function(type_parents, type_attributes, '__eq__') is None)
        ):
            type_attributes['__eq__'] = rich_eq
        
        if (
            (rich_type_feature_flags & RICH_TYPE_FEATURE_FLAG_REPRESENTATION) and
            (_get_parent_or_own_function(type_parents, type_attributes, '__repr__') is None)
        ):
            type_attributes['__repr__'] = rich_repr
        
        # Restore hash as required, since it is not inherited properly.
        hash_function = _get_parent_or_own_function(type_parents, type_attributes, '__hash__')
        if hash_function is None:
            if (rich_type_feature_flags & RICH_TYPE_FEATURE_FLAG_REPRESENTATION):
                hash_function = rich_hash
            else:
                hash_function = object.__hash__
        type_attributes['__hash__'] = hash_function
        
        
        # Get slots, we will use them after to store the descriptors.
        slots = type_attributes.get('__slots__', None)
        
        # Also check attribute shadowing.
        if (slots is not None) and (slot_descriptors is not None):
            for slot_descriptor in slot_descriptors:
                attribute_name = slot_descriptor.__name__
                if 'attribute_name' in slots:
                    raise RuntimeError(f'Attribute shadowing {attribute_name!r}!')
        
        instance = type.__new__(cls, type_name, type_parents, type_attributes)
        
        # Slots are populated after
        if (slots is not None):
            for slot_name in slots:
                # Ignore the ones that start with underscore
                if slot_name.startswith('_'):
                    continue
                
                if slot_descriptors is None:
                    slot_descriptors = []
                
                slot_descriptors.append(getattr(instance, slot_name))
        
        if (slot_descriptors is not None):
            instance.__slot_descriptors__ = tuple(slot_descriptors)
        
        return instance


class RichAttributeErrorBaseType(metaclass = RichType, rich_type_feature_flags = RICH_TYPE_FEATURE_FLAG_ATTRIBUTE_ERROR):
    """
    Base type for generating rich attribute error messages.
    """
    __slots__ = ()
