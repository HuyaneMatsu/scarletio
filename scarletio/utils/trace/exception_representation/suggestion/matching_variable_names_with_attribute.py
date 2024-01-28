__all__ = ('get_matching_variable_names_with_attribute',)

from .helpers_familiarity import SUGGESTIONS_MAX
from .helpers_variables import _iter_unique_variables


def get_matching_variable_names_with_attribute(frame, name):
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
    matches : `None | list<str>`
    """
    matches = []
    
    for variable_name, variable_value in _iter_unique_variables(frame):
        if hasattr(variable_value, name):
            matches.append(variable_name)
    
    if not matches:
        return None
    
    del matches[SUGGESTIONS_MAX:]
    matches.sort()
    return matches
