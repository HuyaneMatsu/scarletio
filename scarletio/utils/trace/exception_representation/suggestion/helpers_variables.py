__all__ = ()


def _get_variable_names(frame):
    """
    Gets the variable names from the given frame proxy for suggestions.
    
    Parameters
    ----------
    frame : `None | FrameProxyBase`
        Frame to get variable names from.
    
    Returns
    -------
    variable_names : `set<str>`
    """
    variable_names = set()
    
    if (frame is not None):
        locals = frame.locals
        if (locals is not None):
            variable_names.update(locals.keys())
        
        globals = frame.globals
        if (globals is not None):
            variable_names.update(globals.keys())
        
        builtins = frame.builtins
        if (builtins is not None):
            variable_names.update(builtins.keys())
        
    return variable_names


def _iter_variables(frame_proxy):
    """
    Iterates over the variables of the frame profy for suggestions.
    
    Parameters
    ----------
    frame_proxy : `None | FrameProxyBase`
        Frame proxy to get variables of.
    
    Yields
    ------
    variable_name : `str`
    variable_value : `object`
    """
    if (frame_proxy is not None):
        locals = frame_proxy.locals
        if (locals is not None):
            yield from locals.items()
        
        globals = frame_proxy.globals
        if (globals is not None):
            yield from globals.items()
        
        builtins = frame_proxy.builtins
        if (builtins is not None):
            yield from builtins.items()


def _iter_unique_variables(frame_proxy):
    """
    Iterates over the variables of the frame profy for suggestions.
    If a variable name is present twice, only yields it the first time.
    
    Parameters
    ----------
    frame_proxy : `None | FrameProxyBase`
        Frame proxy to get variables of.
    
    Yields
    ------
    variable_name : `str`
    variable_value : `object`
    """
    length = 0
    collected = set()
    
    for variable_name, variable_value in  _iter_variables(frame_proxy):
        collected.add(variable_name)
        new_length = len(collected)
        if length != new_length:
            yield variable_name, variable_value
        
        length = new_length
