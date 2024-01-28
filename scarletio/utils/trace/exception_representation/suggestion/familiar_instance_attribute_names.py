__all__ = ('get_familiar_instance_attribute_names',)

from .helpers_familiarity import _get_familiar_names


def _get_instance_attributes(instance):
    """
    Gets the attribute names of the given instance.
    
    Parameter
    ---------
    instance : `object`
        The object to get its attribute names of.
    
    Returns
    -------
    attribute_names : `set<str>`
    """
    attribute_names = {*object.__dir__(instance)}
    
    attribute_names_getter = type(instance).__dir__
    if (attribute_names_getter is not None) and (attribute_names_getter is not object.__dir__):
        try:
            custom_names = attribute_names_getter(instance)
        except Exception:
            pass
        else:
            attribute_names.update(custom_names)
    
    attribute_names.update()
    return attribute_names


def get_familiar_instance_attribute_names(instance, name):
    """
    Gets all the familiar attribute names of the instance to the given one.
    
    Parameters
    ----------
    instance : `object`
        The object to check.
    name : `str`
        The attribute's name to check.
    
    Returns
    -------
    attribute_exists_just_was_not_set : `bool`
    familiar_attribute_names : `list<str>`
    """
    names = _get_instance_attributes(instance)
    
    try:
        names.remove(name)
    except KeyError:
        attribute_exists_just_was_not_set = False
    else:
        attribute_exists_just_was_not_set = True
        
    familiar_attribute_names = _get_familiar_names(names, name)
    if not familiar_attribute_names:
        familiar_attribute_names = None
    
    return attribute_exists_just_was_not_set, familiar_attribute_names
