__all__ = ('get_familiar_variable_names',)

from .helpers_familiarity import _get_familiar_names
from .helpers_variables import _get_variable_names


def get_familiar_variable_names(frame, name):
    """
    Gets all the familiar attribute names of the variable to the given one.
    
    Parameters
    ----------
    frame : `None | FrameProxyBase`
        Frame to get variable names from.
    name : `str`
        Name to check for.
    
    Returns
    -------
    variable_exists_just_was_not_set : `bool`
    familiar_variable_names : `None | list<str>`
    """
    variable_names = _get_variable_names(frame)
    
    try:
        variable_names.remove(name)
    except KeyError:
        variable_exists_just_was_not_set = False
    else:
        variable_exists_just_was_not_set = True
    
    familiar_variable_names = _get_familiar_names(variable_names, name)
    if not familiar_variable_names:
        familiar_variable_names = None
    
    return variable_exists_just_was_not_set, familiar_variable_names
