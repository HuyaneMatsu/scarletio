__all__ = ()


def proxy_property_factory(attribute_name):
    """
    Creates a new proxy property for the given attribute name.
    
    Parameters
    ----------
    attribute_name : `str`
        The attribute's name.
    
    Returns
    -------
    proxy_property : `property`
    """
    def getter(self):
        nonlocal attribute_name
        return self._get_value(attribute_name)
    
    
    def setter(self, value):
        nonlocal attribute_name
        self._set_overwrite(attribute_name, value)
    
    
    def deller(self):
        nonlocal attribute_name
        self._del_overwrite(attribute_name)
    
    return property(getter, setter, deller)


def proxy_method_factory(attribute_name):
    """
    Crates a new proxy method for the given attribute name.
    
    Parameters
    ----------
    attribute_name : `str`
        The attribute's name.
    
    Returns
    -------
    proxy_method : `FunctionType`
    """
    def proxy_method(self, *position_parameters, **keyword_parameters):
        method = self._get_value(attribute_name)
        return method(*position_parameters, **keyword_parameters)
    
    proxy_method.__name__ = attribute_name
    return proxy_method
