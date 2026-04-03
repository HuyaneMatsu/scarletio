__all__ = ()

# import sub-modules

from .compilation import *
from .display_state import *
from .editor_base import *
from .editor_simple import *
from .line_render_intermediate import *
from .prefix_trimming import *
from .terminal_control_commands import *

# only import advanced editor when it supposed to work

try:
    import termios
    import tty
except ImportError:
    editor_advanced = None
else:
    from .editor_advanced import *

# collect editors

from .editor_base import EditorBase

from .editor_simple import EditorSimple

if (editor_advanced is None):
    EditorAdvanced = None
else:
    from .editor_advanced import EditorAdvanced

# define `can_use_advanced_editor`

from os import get_terminal_size
from sys import platform as PLATFORM

def can_use_advanced_editor():
    if (EditorAdvanced is None):
        return False
    
    if PLATFORM != 'linux':
        return False
    
    try:
        get_terminal_size()
    except OSError:
        return False
    
    return True
