__all__ = ('get_frame_module', 'get_last_module_frame',)

import sys
from importlib.util import module_from_spec
from sys import _getframe as get_frame


MODULE_FRAME_NAME = '<module>'

def get_last_module_frame():
    """
    Gets the last module frame.
    
    Returns
    -------
    frame : `None`, `FrameType`
    """
    frame = get_frame()
    
    while True:
        frame = frame.f_back
        if frame is None:
            break
        
        # They might falsely name frames with auto generated functions, so check variables as well
        if (frame.f_code.co_name != MODULE_FRAME_NAME):
            continue
        
        # Try to not compare locals with globals if we are inside of a function.
        if (frame.f_locals is not frame.f_globals):
            continue
        
        break
    
    return frame


def get_frame_module(frame):
    """
    Gets from which module the frame is from.
    
    Parameters
    ----------
    frame : `None`, `FrameType`
        The frame to get it's module of.
    
    Returns
    -------
    module : `None`, `ModuleType`
    """
    if frame is None:
        return
    
    spec = frame.f_globals.get('__spec__', None)
    if spec is not None:
        try:
            return sys.modules[spec.name]
        except KeyError:
            pass
        
        return module_from_spec(spec)
    
    system_parameters = sys.argv
    if len(system_parameters) < 1:
        return
    
    executed_file_name = system_parameters[0]
    
    if frame.f_code.co_filename == executed_file_name:
        return sys.modules.get('__main__', None)
