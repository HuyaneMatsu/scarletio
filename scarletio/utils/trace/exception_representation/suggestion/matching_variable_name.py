__all__ = ('exists_matching_variable_name',)

from .helpers_variables import _get_variable_names


def exists_matching_variable_name(frame, name):
    """
    Returns whether a variable with the same name exists.
    
    Parameters
    ----------
    frame : `None | FrameProxyBase`
        Frame to get variable names from.
    name : `str`
        Name to check for.
    
    Returns
    -------
    exists : `bool`
    """
    variable_names = _get_variable_names(frame)
    return name in variable_names
