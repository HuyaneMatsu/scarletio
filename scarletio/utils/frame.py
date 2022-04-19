__all__ = ('get_last_module_frame',)

from sys import _getframe as get_frame

MODULE_FRAME_NAME = '<module>'

def get_last_module_frame():
    """
    Gets the last module frame.
    
    Returns
    -------
    frame : `None`, ``FrameType``
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
