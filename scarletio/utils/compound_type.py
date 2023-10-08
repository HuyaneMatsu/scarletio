__all__ = ('Compound', 'CompoundMetaType', 'Theory')

import reprlib
from itertools import chain
from types import GetSetDescriptorType, MemberDescriptorType, FunctionType, BuiltinMethodType, MethodType

from .analyzer import CallableAnalyzer


SLOT_TYPES = frozenset((GetSetDescriptorType, MemberDescriptorType))

COMPOUND_META_TYPE_MAP = {}


def is_slot_of(attribute_name, attribute_value, type_):
    """
    Returns whether `value` is a slot of any class from `types`.
    
    Parameters
    ----------
    attribute_name : `str`
        The attribute's name.
    attribute_value : `object`
        Value to be checked to be a slot of any type from `types`.
    type_ : `type_`
        The parent type.
    
    Returns
    -------
    is_slot_of : `bool`
    """
    for slot_type in SLOT_TYPES:
        if isinstance(attribute_value, slot_type):
            break
    else:
        return False
    
    slot_owner_type = getattr(attribute_value, '__objclass__', None)
    if slot_owner_type is None:
        return False
    
    name = getattr(attribute_value, '__name__', None)
    if name is None:
        return False
    
    if name != attribute_name:
        return False
    
    if slot_owner_type not in type_.__mro__:
        return False
    
    return True


def _redirect_constructor(cls, type_name, base_types, type_attributes):
    """
    Used by ``ignore_meta_type`` to redirect `metatype.__new__` calls.
    
    Parameters
    ----------
    cls : `type`
        The base type.
    type_name : `str`
        The created type's future name.
    base_types : `tuple` of `type`
        Base types to inherit from.
    type_attributes : `dict` of (`str`, `object`) items
        Attributes of the created type.
    
    Returns
    -------
    created_type : `type`
        The created type.
    """
    return type.__new__(cls.__wrapped_meta_type__, type_name, base_types, type_attributes)


def ignore_meta_type(meta_type):
    """
    Ignores meta type on creation.
    
    Parameters
    ----------
    meta_type : `type`
        The meta type to ignore.
    
    Returns
    -------
    redirect : `type`
    """
    return type(
        f'{meta_type}Redirect',
        (
            meta_type,
        ), {
            '__new__': _redirect_constructor,
            '__wrapped_meta_type__': meta_type,
        }
    )


class Theory:
    """
    Represents a theoretical value, which should be implemented by other types.
    
    Attributes
    ----------
    theorem : `object`
        The legend itself.
    """
    __slots__ = ('theorem',)
    
    def __new__(cls, theorem):
        self = object.__new__(cls)
        self.theorem = theorem
        return self
    
    
    def __call__(self, *positional_parameters, **keyword_parameters):
        """
        Calls the theory.
        
        Parameters
        ----------
        *positional_parameters : Positional parameters
            Positional parameters to call the theory with.
        *keyword_parameters : Keyword parameters
            Keyword parameters to call the theory with. 
        
        Returns
        -------
        return_value : `object`
            The returned value by the theory.
        
        Raises
        ------
        BaseException
            Exception raised by the theory.
        """
        return self.theorem(*positional_parameters, **keyword_parameters)
    
    
    def __dir__(self):
        """Returns the attributes of the theory including the theorem's."""
        return sorted({*object.__dir__(self), *dir(self.theorem)})
    
    
    def __getattr__(self, attribute_name):
        """Returns the attribute of the theorem."""
        return getattr(self.theorem, attribute_name)


def collect_attributes_per_type_from_type_attributes(type_attributes):
    """
    Collects attributes per type from type attribute dictionary.
    
    Parameters
    ----------
    type_attributes : `dict` of (`str`, `object`) items
        Type attributes of a class.
    
    Returns
    -------
    instance_attributes : `None` or `set` of `name`
        A set of attribute names mentioned in the type attributes.
    theoretical_type_attributes : `None`, `dict` of (`str`, `object`) items
        Theoretical defined type attributes.
    implemented_type_attributes : `None`, `dict` of (`str`, `object`) items
        Implemented type attributes.
    leftover_type_attributes : `dict` of (`str`, `object`) items
        Additional type attributes which should not be touched.
    """
    instance_attributes = type_attributes.pop('__slots__', None)
    if instance_attributes is None:
        instance_attributes = None
    
    # Can happen that you mess up, but you should not focus on this error, go go maniac!
    elif isinstance(instance_attributes, str):
        instance_attributes = {instance_attributes}
    
    else:
        instance_attributes = {*instance_attributes}
        if not instance_attributes:
            instance_attributes = None
    
    
    theoretical_type_attributes = None
    implemented_type_attributes = None
    leftover_type_attributes = {}
    
    
    for attribute_name, attribute_value in type_attributes.items():
        if attribute_name == '__annotations__':
            continue
        
        if attribute_name in {'__module__', '__qualname__'}:
            leftover_type_attributes[attribute_name] = attribute_value
            continue
        
        if (instance_attributes is not None) and (attribute_name in instance_attributes):
            continue
        
        if isinstance(attribute_value, Theory):
            if (theoretical_type_attributes is None):
                theoretical_type_attributes = {}
            
            theoretical_type_attributes[attribute_name] = attribute_value.theorem
        
        else:
            if (implemented_type_attributes is None):
                implemented_type_attributes = {}
            
            implemented_type_attributes[attribute_name] = attribute_value
    
    return instance_attributes, theoretical_type_attributes, implemented_type_attributes, leftover_type_attributes


class CompoundMetaType(type):
    """
    Stops class creation and redirects it into compound component creation instead.
    """
    __source_meta_type__ = None
    
    def __new__(cls, type_name, base_types, type_attributes, *, build = False, **keyword_parameters):
        """
        Creates a new compound component.
        
        Parameters
        ----------
        type_name : `str`
            The created component's name.
        base_types : `tuple` of `type`
            types from which the type inherits from.
        type_attributes : `dict` of (`str`, `object`) items
            Attributes defined in the type body.
        build : `bool` = `False`, Optional (Keyword only)
            Whether the type should be built.
        **keyword_parameters : Keyword parameters
            Additional keyword parameters.
        
        Returns
        -------
        compound : ``CompoundMetaType``
            The created compound.
        
        Raises
        ------
        TypeError
            - If a base-type is a not a type.
            - Unexpected base-type.
            - If a base-type is a not a type.
            - Only the first type can bo a non-component type.
            - Get-descriptor mismatch.
            - Instance attribute overwritten with other get-property.
            - Both method is implemented.
            - Method parameter mismatch.
            - If a type  attribute is never implemented.
            - Constant value mismatch.
            - Keyword parameters are not supported when building a component.
        """
        if build:
            compound = cls.__build__(type_name, base_types, type_attributes, keyword_parameters)
        
        else:
            if keyword_parameters:
                raise TypeError(
                    f'Keyword parameters are not supported when building a component. '
                    f'Got type_name = {type_name!r}; keyword_parameters = {keyword_parameters!r}.'
                )
            
            compound = cls.__create_component__(type_name, base_types, type_attributes)
        
        return compound
    
    
    @classmethod
    def __build__(cls, type_name, base_types, type_attributes, keyword_parameters):
        """
        Merges the compounds together.
        
        Parameters
        ----------
        type_name : `str`
            The created type's future name.
        base_types : `tuple` of `type`
            The types to inherit from.
        type_attributes : `dict` of (`str`, `object`) items
            The attributes defined inside of the type body.
        keyword_parameters : `dict` of (`str`, `object`) items
            Additional keyword parameters.
        
        Returns
        -------
        compound : `type`
            The created compound.
        
        Raises
        ------
        TypeError
            - If a base-type is a not a type.
            - Only the first type can bo a non-component type.
            - Get-descriptor mismatch.
            - Instance attribute overwritten with other get-property.
            - Both method is implemented.
            - Method parameter mismatch.
            - If a type  attribute is never implemented.
            - Constant value mismatch.
        """
        source_meta_type = cls.__source_meta_type__
        if (source_meta_type is None):
            build_type = type
            created_type = cls
        
        else:
            build_type = source_meta_type
            created_type = source_meta_type
        
        
        new_base_types, new_type_attributes = build_type_structure(type_name, base_types, type_attributes)
        
        return build_type.__new__(created_type, type_name, new_base_types, new_type_attributes, **keyword_parameters)
    
    
    @classmethod
    def __create_component__(cls, type_name, base_types, type_attributes):
        """
        Creates a new compound component.
        
        Parameters
        ----------
        type_name : `str`
            The created component's name.
        base_types : `tuple` of `type`
            types from which the type inherits from.
        type_attributes : `dict` of (`str`, `object`) items
            Attributes defined in the type body.
        
        Returns
        -------
        compound : ``CompoundMetaType``
            The created compound.
        
        Raises
        ------
        TypeError
            - If a base-type is a not a type.
            - Unexpected base-type.
        """
        for base_type in base_types:
            if not isinstance(base_type, type):
                raise TypeError(
                    f'Base types can only be `type` instances, got {base_type!r}; type_name = {type_name!r};'
                    f'base_types = {base_types}.'
                )
            
            if base_type is object:
                continue
            
            if base_type is Compound:
                continue
            
            raise TypeError(
                f'Base types can only be `object` or `{Compound.__name__}`, got {base_type!r};'
                f'type_name = {type_name!r}; base_types = {base_types}.'
            )
        
        
        (
            instance_attributes,
            theoretical_type_attributes,
            implemented_type_attributes,
            leftover_type_attributes,
        ) = collect_attributes_per_type_from_type_attributes( 
            type_attributes,
        )
        
        return type.__new__(
            cls,
            type_name,
            (
                Compound,
            ),
            {
                **leftover_type_attributes,
                '__instance_attributes__': instance_attributes,
                '__theoretical_type_attributes__': theoretical_type_attributes,
                '__implemented_type_attributes__': implemented_type_attributes,
            }
        )
    
    
    @classmethod
    def with_(cls, other):
        """
        Meta type merging to allow compounding
        
        Parameters
        ----------
        other : `type`
            The other type to merge with.
        
        Raises
        ------
        TypeError
            - If `other` is not a type.
        """
        if not isinstance(other, type):
            raise TypeError(
                f'`other` must be a type, got {other!r}.'
            )
        
        if not issubclass(other, type):
            other = type(other)
        
        if other is type:
            return cls
        
        if hasattr(other, '__source_meta_type__'):
            return other
        
        try:
            return COMPOUND_META_TYPE_MAP[other]
        except KeyError:
            pass
        
        merge_type = type(
            f'{other.__name__}CompoundMergeType',
            (
                cls, other,
            ), {
                '__source_meta_type__': other,
            }
        )
        COMPOUND_META_TYPE_MAP[other] = merge_type
        return merge_type
    
    
    def __dir__(sub_type):
        """Lists the attributes of the compound component."""
        directory = {*type.__dir__(sub_type)}
        
        type_instance_attributes = sub_type.__instance_attributes__
        if (type_instance_attributes is not None):
            directory.update(type_instance_attributes)
        
        theoretical_type_attributes = sub_type.__theoretical_type_attributes__
        if (theoretical_type_attributes is not None):
            directory.update(theoretical_type_attributes.keys())
        
        implemented_type_attributes = sub_type.__implemented_type_attributes__
        if (implemented_type_attributes is not None):
            directory.update(implemented_type_attributes.keys())
        
        return sorted(directory)
    
    
    def __getattr__(sub_type, attribute_name):
        """Gets an attribute of the sub type. It can be either instance attribute, implemented or theoretical."""
        type_instance_attributes = sub_type.__instance_attributes__
        if (type_instance_attributes is not None):
            if attribute_name in type_instance_attributes:
                return NotImplemented
        
        theoretical_type_attributes = sub_type.__theoretical_type_attributes__
        if (theoretical_type_attributes is not None):
            try:
                return theoretical_type_attributes[attribute_name]
            except KeyError:
                pass
        
        implemented_type_attributes = sub_type.__implemented_type_attributes__
        if (implemented_type_attributes is not None):
            try:
                return implemented_type_attributes[attribute_name]
            except KeyError:
                pass
        
        raise AttributeError(attribute_name)


class Compound(metaclass = ignore_meta_type(CompoundMetaType)):
    """
    Compound component base type. Inherit from it to create a type component.
    """
    __slots__ = ()
    
    __instance_attributes__ = None
    __theoretical_type_attributes__ = None
    __implemented_type_attributes__ = None
    
    def __new__(cls):
        """
        Compound components do not support instancing.
        
        Sub-typing is supported, but the attributes are only proxied. Sub-types have no meaning by themselves.
        
        Raises
        -------
        RuntimeError
        """
        raise RuntimeError(
            f'{cls.__name__} does not supports instancing.'
        )


class CompoundLayer:
    """
    Represents a layer when building a type.
    
    Attributes
    ----------
    implemented_type_attributes : `None`, `dict` of (`str`, `object`) items
        Implemented type attributes by the component.
    instance_attributes : `None`, `set` of `str`
        The instance attributes to implement.
    implemented : `bool`
        Whether the layer is already implemented.
    theoretical_type_attributes : `None`, `dict` of (`str`, `object`) items
        Theoretical type attributes which an other component should implement.
    type_name : `str`
        The represented type's or the component's name.
    """
    __slots__ = (
        'implemented_type_attributes', 'instance_attributes', 'implemented', 'theoretical_type_attributes',
        'type_name'
    )
    
    def __new__(
        cls, type_name, instance_attributes, theoretical_type_attributes, implemented_type_attributes,
        implemented
    ):
        """
        Parameters
        ----------
        type_name : `str`
            The represented type's or the component's name.
        instance_attributes : `None`, `set` of `str`
            The instance attributes to implement.
        theoretical_type_attributes : `None`, `dict` of (`str`, `object`) items
            Theoretical type attributes which an other component should implement.
        implemented_type_attributes : `None`, `dict` of (`str`, `object`) items
            Implemented type attributes by the component.
        implemented : `bool`
            Whether the layer is already implemented.
        """
        self = object.__new__(cls)
        self.type_name = type_name
        self.instance_attributes = instance_attributes
        self.theoretical_type_attributes = theoretical_type_attributes
        self.implemented_type_attributes = implemented_type_attributes
        self.implemented = implemented
        return self
    
    
    @classmethod
    def from_component(cls, component, *, implemented = False):
        """
        Creates a new component layer from the given component.
        
        Parameters
        ----------
        component : ``CompoundMetaType``
            Compound component.
        implemented : `bool` = `False`, Optional (Keyword only)
            Whether the layer is already implemented.
        
        Returns
        -------
        self : ``ComponentLayer``
        """
        instance_attributes = component.__instance_attributes__
        if (instance_attributes is not None):
            instance_attributes = instance_attributes.copy()
        
        theoretical_type_attributes = component.__theoretical_type_attributes__
        if (theoretical_type_attributes is not None):
            theoretical_type_attributes = theoretical_type_attributes.copy()
        
        implemented_type_attributes = component.__implemented_type_attributes__
        if (implemented_type_attributes is not None):
            implemented_type_attributes = implemented_type_attributes.copy()
        
        return cls(
            component.__name__,
            instance_attributes,
            theoretical_type_attributes,
            implemented_type_attributes,
            implemented,
        )
    
    
    @classmethod
    def from_type(cls, type_, *, implemented = False):
        """
        Creates a new component layer from the given type.
        
        Parameters
        ----------
        type_ : `type`
            Base type to inherit from.
        implemented : `bool` = `False`, Optional (Keyword only)
            Whether the layer is already implemented.
        
        Returns
        -------
        self : ``ComponentLayer``
        """
        instance_attributes = None
        type_attributes = None
        
        type_directory = type_.__dict__
        for attribute_name in dir(type_):
            if attribute_name in {'__doc__', '__slots__', '__annotations__', '__module__', '__qualname__', '__class__'}:
                continue
            
            try:
                attribute_value = type_directory[attribute_name]
            except KeyError:
                attribute_value = getattr(type_, attribute_name)
            
            try:
                default_implementation =  getattr(object, attribute_name)
            except AttributeError:
                pass
            else:
                if attribute_value is default_implementation:
                    continue
            
            if attribute_name == '__new__':
                if type(attribute_value) is staticmethod:
                    attribute_value = attribute_value.__func__
            
            elif attribute_name in {'__subclasshook__', '__init_subclass__'}:
                if type(attribute_value) is MethodType:
                    attribute_value = attribute_value.__func__
                    if attribute_value is getattr(getattr(object, attribute_name), '__func__', None):
                        continue
                    
                elif type(attribute_value) is BuiltinMethodType:
                    continue
            
            
            if is_slot_of(attribute_name, attribute_value, type_):
                if instance_attributes is None:
                    instance_attributes = set()
                    
                instance_attributes.add(attribute_name)
            
            else:
                if type_attributes is None:
                    type_attributes = {}
                    
                type_attributes[attribute_name] = attribute_value
        
        
        return cls(
            type_.__name__,
            instance_attributes,
            None,
            type_attributes,
            implemented
        )
    
    
    @classmethod
    def from_name_and_attributes(cls, type_name, type_attributes,*, implemented = False):
        """
        Creates a new component layer from the given `type_name` - `type_attributes` pair.
        
        Parameters
        ----------
        type_name : `str`
            The created component's name.
        type_attributes : `dict` of (`str`, `object`) items
            Attributes defined in the type body.
        implemented : `bool` = `False`, Optional (Keyword only)
            Whether the layer is already implemented.
        
        Returns
        -------
        self : ``ComponentLayer``
            The created component layer.
        leftover_type_attributes : `dict` of (`str`, `object`) items
            Additional type attributes which should not be touched.
        """
        (
            instance_attributes,
            theoretical_type_attributes,
            implemented_type_attributes,
            leftover_type_attributes,
        ) = collect_attributes_per_type_from_type_attributes(type_attributes)
        
        
        return (
            cls(
                type_name,
                instance_attributes,
                theoretical_type_attributes,
                implemented_type_attributes,
                implemented,
            ),
            leftover_type_attributes,
        )
    
    
    def iter_attribute_names(self):
        """
        Iterates over the attributes mentioned in the layer.
        
        This method is an iterable generator.
        
        Yields
        ------
        attribute_name : `str`
        """
        instance_attributes = self.instance_attributes
        if (instance_attributes is not None):
            yield from instance_attributes
        
        theoretical_type_attributes = self.theoretical_type_attributes
        if (theoretical_type_attributes is not None):
            yield from theoretical_type_attributes.keys()
        
        implemented_type_attributes = self.implemented_type_attributes
        if (implemented_type_attributes is not None):
            yield from implemented_type_attributes
    
    
    def get_implementation_detail_of(self, attribute_name, *, exhaust = False):
        """
        Gets the implementation details for the given attribute name.
        
        Parameters
        ----------
        attribute_name : `str`
            The attribute's name to get it's implementation of.
        exhaust : `bool` = `False`, Optional (Keyword only)
            Whether the attribute should be discarded up use.
        
        Returns
        -------
        implementation_detail : `None`, ``ImplementationDetail``
        """
        instance_attributes = self.instance_attributes
        if (instance_attributes is not None) and (attribute_name in instance_attributes):
            if exhaust:
                instance_attributes.discard(attribute_name)
                if not instance_attributes:
                    self.instance_attributes = None
            
            return ImplementationDetail(True, self.implemented, None, self.type_name, attribute_name)
        
        
        theoretical_type_attributes = self.theoretical_type_attributes
        if (theoretical_type_attributes is not None):
            try:
                implementation = theoretical_type_attributes[attribute_name]
            except KeyError:
                pass
            else:
                if exhaust:
                    theoretical_type_attributes.pop(attribute_name)
                    if not theoretical_type_attributes:
                        self.theoretical_type_attributes = None
                
                return ImplementationDetail(False, False, implementation, self.type_name, attribute_name)
        
        
        implemented_type_attributes = self.implemented_type_attributes
        if (implemented_type_attributes is not None):
            try:
                implementation = implemented_type_attributes[attribute_name]
            except KeyError:
                pass
            else:
                if exhaust:
                    implemented_type_attributes.pop(attribute_name)
                    if not implemented_type_attributes:
                        self.implemented_type_attributes = None
                
                return ImplementationDetail(False, True, implementation, self.type_name, attribute_name)
        
        
        return None


class ImplementationDetail:
    """
    Represents details about and attribute's implementation.
    
    Attributes
    ----------
    instance_attribute : `bool`
        Whether the implementation is an instance attribute.
    implemented : `bool`
        Whether the instance attribute is implemented.
    implementation : `None`, `object`
        The implementation.
    implementation_source : `None`, `str`
        From where the implementation is coming from.
    name : `str`
        The name of the represented attribute.
    """
    __slots__ = ('instance_attribute', 'implemented', 'implementation', 'implementation_source', 'name')
    
    def __new__(cls, instance_attribute, implemented, implementation, implementation_source, name):
        """
        Creates a new ``ImplementationDetail``.
        
        Parameters
        ----------
        instance_attribute : `bool`
            Whether the implementation is an instance attribute.
        implemented : `bool`
            Whether the instance attribute is implemented.
        implementation : `None`, `object`
            The implementation.
        implementation_source : `str`
            From where the implementation is coming from.
        name : `str`
            The name of the represented attribute.
        """
        self = object.__new__(cls)
        self.instance_attribute = instance_attribute
        self.implemented = implemented
        self.implementation = implementation
        self.implementation_source = implementation_source
        self.name = name
        return self
    
    
    def __repr__(self):
        """Returns the implementation detail's representation."""
        repr_parts = ['<', self.__class__.__name__, ' ', self.implementation_source, '.', self.name, ' ']
        
        if self.instance_attribute:
            repr_parts.append('instance_attribute')
        
        elif self.is_get_descriptor():
            repr_parts.append('get_descriptor')
        
        elif self.is_method():
            repr_parts.append('method')
            
        
        
        if self.implemented:
            repr_parts.append(', implemented = True')
            
            repr_parts.append(', implementation = ')
            
            implementation = self.implementation
            if isinstance(implementation, FunctionType):
                implementation_representation = repr(implementation)
            else:
                implementation_representation = reprlib.repr(implementation)
            repr_parts.append(implementation_representation)
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def is_get_descriptor(self):
        """
        Returns whether the implementation detail is a property.
        
        Returns
        -------
        is_get_descriptor : `bool`
        """
        if self.instance_attribute:
            return True
        
        implementation = self.implementation
        if (implementation is None):
            return False
        
        if isinstance(implementation, property):
            return True
        
        # Check for custom descriptors, all should implemented
        if (
            (getattr(implementation, '__get__', None) is not None) and
            (getattr(implementation, '__set__', None) is not None) and
            (getattr(implementation, '__delete__', None) is not None)
        ):
            return True
        
        return False
    
    
    def is_method(self):
        """
        Returns whether the implementation is a method.
        
        Returns
        -------
        is_method : `bool`
        """
        if self.instance_attribute:
            return False
        
        implementation = self.implementation
        if (implementation is None):
            return False
        
        return isinstance(implementation, FunctionType)
    
    
    def is_constant(self):
        """
        Returns whether the implementation is a constant.
        
        Returns
        -------
        is_method : `bool`
        """
        if self.instance_attribute:
            return False
        
        implementation = self.implementation
        if implementation is None:
            return True
        
        if implementation is NotImplemented:
            return False
        
        if isinstance(implementation, FunctionType):
            return False
        
        if (
            hasattr(implementation, '__get__') or
            hasattr(implementation, '__set__') or
            hasattr(implementation, '__delete__')
        ):
            return False
        
        return True
    
    
    def is_implemented(self):
        """
        Returns whether the implementation detail was ever really implemented.
        
        Returns
        -------
        is_implemented : `bool`
        """
        if self.instance_attribute:
            return True
        
        if not self.implemented:
            return False
        
        if self.implementation is NotImplemented:
            return False
        
        return True
    
    
    def apply_layer_implementation(self, layer_implementation, attribute_name):
        """
        Applies an implementation of an other layer.
        
        Parameters
        ----------
        layer_implementation : ``ImplementationDetail``
            The implementation detail to apply.
        attribute_name : `str`
            The respective attribute's name.
        
        Raises
        ------
        TypeError
            - Get-descriptor mismatch.
            - Instance attribute overwritten with other get-property.
            - Constant value mismatch.
        """
        _check_get_descriptor_match(self, layer_implementation)
        _check_instance_attribute_overwritability(self, layer_implementation)
        _check_method_match(self, layer_implementation)
        _check_constant_match(self, layer_implementation)
        _maybe_transfer_method_implementation(self, layer_implementation)
        _maybe_transfer_implementation(self, layer_implementation)


class CompoundLogicUnit:
    """
    Defines lookup logic unit for building component types.
    
    The existence of these units only comes from design, since some nice OOP design makes the implementation simpler.
    
    Attributes
    ----------
    attribute_names : `set` of `str`
        The attribute names of the layer to resolve.
    base_layer : ⅞none`, ``ComponentLayer``
        The base type's layer.
    component_layers : `list` of ``ComponentLayer``
        Component layers.
    type_layer : ``ComponentLayer``
        The first priority layer.
    """
    __slots__ = ('attribute_names', 'base_layer', 'component_layers', 'type_layer')
    
    def __new__(cls, type_layer):
        """
        Creates a new compound logic unit.
        
        Parameters
        ----------
        type_layer : ``ComponentLayer``
            The first priority layer.
        """
        attribute_names = {*type_layer.iter_attribute_names()}
        
        self = object.__new__(cls)
        self.attribute_names = attribute_names
        self.base_layer = None
        self.component_layers = []
        self.type_layer = type_layer
        
        return self
    
    
    def add_component_layers(self, layer):
        """
        Adds a component layer to the logic.
        
        > New layers are always added to the end, so order matters.
        
        Parameters
        ----------
        layer : ``ComponentLayer``
        """
        self.component_layers.append(layer)
        self.attribute_names.update(layer.iter_attribute_names())
    
    
    def add_base_layer(self, layer):
        """
        Adds a base type layer to the type.
        
        Parameters
        ----------
        layer : ``ComponentLayer``
        """
        self.base_layer = layer
        self.attribute_names.update(layer.iter_attribute_names())
    
    
    def iter_all_layer(self):
        """
        Iterates over all the registered layers in order.
        
        This method is an iterable generator.
        
        Yields
        ------
        layer : ``CompoundLayer``
        """
        yield self.type_layer
        
        base_layer = self.base_layer
        if (base_layer is not None):
            yield base_layer
        
        yield from self.component_layers
    
    
    def exhaust_attribute_names(self):
        """
        Exhaust the attribute names of the compound logic.
        
        This method is an iterable generator.
        
        Yields
        ------
        attribute_name : `str`
        """
        attribute_names = self.attribute_names
        while attribute_names:
            yield attribute_names.pop()
    
    
    def try_get_base_implementation_for(self, attribute_name):
        """
        tries to get implementation details for the base implementation of the given `attribute_name`.
        
        Returns
        -------
        implementation_detail : `None, ``ImplementationDetail``
        
        Raises
        ------
        TypeError
            - Get-descriptor mismatch.
            - Instance attribute overwritten with other get-property.
            - Constant value mismatch.
        """
        type_layer_implementation_detail = self.type_layer.get_implementation_detail_of(attribute_name, exhaust = True)
        
        base_layer = self.base_layer
        if (base_layer is None):
            base_layer_implementation_detail = None
        
        else:
            base_layer_implementation_detail = base_layer.get_implementation_detail_of(attribute_name, exhaust = True)
        
        
        if (type_layer_implementation_detail is None):
            if (base_layer_implementation_detail is None):
                return None
            
            else:
                return base_layer_implementation_detail
        
        else:
            if (base_layer_implementation_detail is None):
                return type_layer_implementation_detail
        
        
        _check_get_descriptor_match(base_layer_implementation_detail, type_layer_implementation_detail)
        _check_instance_attribute_overwritability(base_layer_implementation_detail, type_layer_implementation_detail)
        _check_constant_match(base_layer_implementation_detail, type_layer_implementation_detail)
        
        _maybe_transfer_instance_attribute_implementation(
            base_layer_implementation_detail, type_layer_implementation_detail
        )
        
        _maybe_transfer_implementation(base_layer_implementation_detail, type_layer_implementation_detail)
        
        return type_layer_implementation_detail


def _check_get_descriptor_match(source_implementation_detail, added_implementation_detail):
    """
    Checks whether the source one is a get descriptor but the other one is not.
    
    Parameters
    ----------
    source_implementation_detail : ``ImplementationDetail``
        Priority source implementation.
    added_implementation_detail : ``ImplementationDetail``
        The added implementation.
    
    Raises
    ------
    TypeError
        - Get-descriptor mismatch.
    """
    if source_implementation_detail.is_get_descriptor() != added_implementation_detail.is_get_descriptor():
        raise TypeError(
            f'Implementation of `{source_implementation_detail.name}` at '
            f'`{source_implementation_detail.implementation_source}` is defined as a `get-descriptor`'
            f', meanwhile at `{added_implementation_detail.implementation_source}` is not. '
            f'Got `{source_implementation_detail!r}`; `{added_implementation_detail!r}`.'
        )


def _check_instance_attribute_overwritability(source_implementation_detail, added_implementation_detail):
    """
    Checks whether the source one is a get descriptor but the other one is not.
    
    Parameters
    ----------
    source_implementation_detail : ``ImplementationDetail``
        Priority source implementation.
    added_implementation_detail : ``ImplementationDetail``
        The added implementation.
    
    Raises
    ------
    TypeError
        - Instance attribute overwritten with other get-property.
    """
    if source_implementation_detail.instance_attribute and source_implementation_detail.implemented:
        if (not added_implementation_detail.instance_attribute):
            raise TypeError(
                f'`{source_implementation_detail.name}` is implemented as instance attribute at '
                f'`{source_implementation_detail.implementation_source}`, but at'
                f'`{added_implementation_detail.implementation_source}` it is not. '
                f'Got `{source_implementation_detail!r}`; `{added_implementation_detail!r}`.'
            )


def _check_method_match(source_implementation_detail, added_implementation_detail):
    """
    Checks whether the source implementation method matches the added implementation one.
    
    Parameters
    ----------
    source_implementation_detail : ``ImplementationDetail``
        Priority source implementation.
    added_implementation_detail : ``ImplementationDetail``
        The added implementation.
    
    Raises
    ------
    TypeError
        - Both method is implemented.
        - Method parameter mismatch.
    """
    if source_implementation_detail.is_method() and added_implementation_detail.is_method():
        if source_implementation_detail.implemented and added_implementation_detail.implemented:
            raise TypeError(
                f'`{source_implementation_detail.name}` is implemented at '
                f'`{source_implementation_detail.implementation_source}` and at '
                f'`{added_implementation_detail.implementation_source}` as well. '
                f'Got `{source_implementation_detail!r}`; `{added_implementation_detail!r}`.'
            )
        
        source_implementation = source_implementation_detail.implementation
        added_implementation = added_implementation_detail.implementation
        
        if (source_implementation is not None) and (added_implementation is not None):
            if not CallableAnalyzer(source_implementation) % CallableAnalyzer(added_implementation):
                raise TypeError(
                    f'`{source_implementation_detail.name}` is implemented differently at '
                    f'`{source_implementation_detail.implementation_source}` than at '
                    f'`{added_implementation_detail.implementation_source}`. '
                    f'Got `{source_implementation_detail!r}`; `{added_implementation_detail!r}`.'
                )


def _check_constant_match(source_implementation_detail, added_implementation_detail):
    """
    Checks for constant variable matching.
    
    Parameters
    ----------
    source_implementation_detail : ``ImplementationDetail``
        Priority source implementation.
    added_implementation_detail : ``ImplementationDetail``
        The added implementation.
    
    Raises
    ------
    TypeError
        - Constant value mismatch.
    """
    if source_implementation_detail.is_constant() and added_implementation_detail.is_constant():
        if source_implementation_detail.implemented and added_implementation_detail.implemented:
            source_implementation = source_implementation_detail.implementation
            added_implementation = added_implementation_detail.implementation
            
            if source_implementation != added_implementation:
                raise TypeError(
                    f'`{source_implementation_detail.name}` is implemented differently at '
                    f'`{source_implementation_detail.implementation_source}` than at '
                    f'`{added_implementation_detail.implementation_source}`. '
                    f'Got `{source_implementation_detail!r}`; `{added_implementation_detail!r}`.'
                )


def _maybe_transfer_instance_attribute_implementation(source_implementation_detail, added_implementation_detail):
    """
    If both implementations are instance attributes and if one is implemented, marks both implemented.
    
    Parameters
    ----------
    source_implementation_detail : ``ImplementationDetail``
        Priority source implementation.
    added_implementation_detail : ``ImplementationDetail``
        The added implementation.
    """
    if source_implementation_detail.instance_attribute and added_implementation_detail.instance_attribute:
        if source_implementation_detail.implemented ^ added_implementation_detail.implemented:
            if source_implementation_detail.implemented:
                added_implementation_detail.implementation_source = source_implementation_detail.implementation_source
            else:
                source_implementation_detail.implementation_source = added_implementation_detail.implementation_source
            
            source_implementation_detail.implemented = True
            added_implementation_detail.implemented = True


def _maybe_transfer_method_implementation(source_implementation_detail, added_implementation_detail):
    """
    If both implementations are methods, transfer the implementation to one from the other if applicable.
    
    Parameters
    ----------
    source_implementation_detail : ``ImplementationDetail``
        Priority source implementation.
    added_implementation_detail : ``ImplementationDetail``
        The added implementation.
    """
    if source_implementation_detail.is_method() and added_implementation_detail.is_method():
        if source_implementation_detail.implemented ^ added_implementation_detail.implemented:
            if source_implementation_detail.implemented:
                added_implementation_detail.implementation_source = source_implementation_detail.implementation_source
                added_implementation_detail.implementation = source_implementation_detail.implementation
            else:
                source_implementation_detail.implementation_source = added_implementation_detail.implementation_source
                source_implementation_detail.implementation = added_implementation_detail.implementation
            
            source_implementation_detail.implemented = True
            added_implementation_detail.implemented = True


def _maybe_transfer_implementation(source_implementation_detail, added_implementation_detail):
    """
    Tries to transfer implementation if only one is implemented.
    
    Parameters
    ----------
    source_implementation_detail : ``ImplementationDetail``
        Priority source implementation.
    added_implementation_detail : ``ImplementationDetail``
        The added implementation.
    """
    if (source_implementation_detail.implemented and source_implementation_detail.implementation is NotImplemented):
        source_implementation_detail.implemented = added_implementation_detail.implemented
        source_implementation_detail.implementation = added_implementation_detail.implementation
        source_implementation_detail.instance_attribute = added_implementation_detail.instance_attribute
    
    elif (added_implementation_detail.implemented and added_implementation_detail.implementation is NotImplemented):
        added_implementation_detail.implemented = source_implementation_detail.implemented
        added_implementation_detail.implementation = source_implementation_detail.implementation
        added_implementation_detail.instance_attribute = source_implementation_detail.instance_attribute



def separate_base_type_from_components(base_types):
    """
    Separates base types from compound components and returns the result.
    
    Parameters
    ----------
    base_types : `tuple` of `type`
        base types to create a new type with.
    
    Returns
    -------
    direct_inherit_type : `None`, `type`
        The directly inherited type.
    components : `None`, `list` of ``CompoundMetaType``
        Compound components.
    
    Raises
    ------
    TypeError
        - If a base-type is a not a type.
        - Only the first type can bo a non-component type.
    """
    components = None
    direct_inherit_type = None
    
    for base_type in base_types:
        if (base_type is object) or (base_type is Compound):
            continue
        
        if not isinstance(base_type, type):
            raise TypeError(
                f'Base types can only be `type` instances, got {base_type!r}; base_types = {base_types}.'
            )
        
        if isinstance(base_type, CompoundMetaType):
            if (components is None):
                components = []
            
            components.append(base_type)
        
        else:
            if (direct_inherit_type is None):
                direct_inherit_type = base_type
            
            else:
                raise TypeError(
                    f'Only one type can be non-component base type, got {base_type!r}; base_types = {base_types}.'
                )
    
    return direct_inherit_type, components


def build_type_structure(type_name, base_types, type_attributes):
    """
    Builds type structure from the given type constructor parameters.
    
    Parameters
    ----------
    type_name : `str`
        The created type's future name.
    base_types : `tuple` of `type`
        The types to inherit from.
    type_attributes : `dict` of (`str`, `object`) items
        The attributes defined inside of the type body.
    
    Returns
    -------
    new_base_types : `tuple` of `type`
        The new base types.
    new_type_attributes : `dict` of (`str`, `object`) items
        The new type attributes.
    
    Raises
    ------
    TypeError
        - If a base-type is a not a type.
        - Only the first type can bo a non-component type.
        - Get-descriptor mismatch.
        - Instance attribute overwritten with other get-property.
        - Both method is implemented.
        - Method parameter mismatch.
        - If a type  attribute is never implemented.
        - Constant value mismatch.
    """
    direct_inherit_type, components = separate_base_type_from_components(base_types)
    
    base_layer, new_type_attributes = CompoundLayer.from_name_and_attributes(type_name, type_attributes)
    logic = CompoundLogicUnit(base_layer)
    
    if (direct_inherit_type is not None):
        logic.add_base_layer(CompoundLayer.from_type(direct_inherit_type, implemented = True))
    
    if (components is not None):
        for component in components:
            logic.add_component_layers(CompoundLayer.from_component(component))
    
    
    type_attribute_implementations = {}
    
    for attribute_name in logic.exhaust_attribute_names():
        implementation_detail = logic.try_get_base_implementation_for(attribute_name)
        
        for layer in logic.component_layers:
            layer_implementation = layer.get_implementation_detail_of(attribute_name, exhaust = True)
            if (layer_implementation is None):
                continue
            
            if implementation_detail is None:
                implementation_detail = layer_implementation
                continue
            
            implementation_detail.apply_layer_implementation(layer_implementation, attribute_name)
            continue
        
        
        if (implementation_detail is None):
            raise TypeError(
                f'`{attribute_name}` is never implemented. Unknown source.'
            )
        
        if not implementation_detail.is_implemented():
            raise TypeError(
                f'`{attribute_name}` is never implemented. Source: {implementation_detail.implementation_source!r}.'
            )
        
        type_attribute_implementations[attribute_name] = implementation_detail
    
    
    implemented_instance_attributes = []
    new_instance_attributes = []
    
    for attribute_name, implementation_detail in type_attribute_implementations.items():
        if not implementation_detail.instance_attribute:
            continue
        
        if implementation_detail.implemented:
            implemented_instance_attributes.append(attribute_name)
        
        else:
            new_instance_attributes.append(attribute_name)
    
    for attribute_name in chain(implemented_instance_attributes, new_instance_attributes):
        del type_attribute_implementations[attribute_name]
    
    
    new_instance_attributes.sort()
    
    new_type_attributes['__slots__'] = tuple(new_instance_attributes)
    
    for attribute_name, implementation_detail in type_attribute_implementations.items():
        new_type_attributes[attribute_name] = implementation_detail.implementation
    
    if direct_inherit_type is None:
        new_base_types = ()
    
    else:
        new_base_types = (direct_inherit_type,)
    
    return new_base_types, new_type_attributes
