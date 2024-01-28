__all__ = ('ignore_frame',)

import os
from warnings import warn

from ..analyzer import CallableAnalyzer
from ..docs import copy_docs

from .formatters import format_builtin


DEFAULT_IGNORED_FRAMES = os.environ.get('SCARLETIO_TRACE_DEFAULT_IGNORED_FRAME', '').casefold() not in ('0', 'false')

IGNORED_FRAME_LINES = {}


def ignore_frame(file_name, name, line):
    """
    When rendering an exception traceback, specified frames can be added to being stopped from rendering.
    
    Parameters
    ----------
    file_name : `str`
        The name of the respective file.
    name : `str`
        The name of the respective function.
    line : `str`
        The respective line's stripped content.
    """
    key = (file_name, name)
    
    try:
        lines = IGNORED_FRAME_LINES[key]
    except KeyError:
        lines = set()
        IGNORED_FRAME_LINES[key] = lines
    
    lines.add(line)


def _should_ignore_frame(frame_proxy):
    """
    Returns whether the given frame should be ignored from rending.
    
    Called by ``should_ignore_frame`` before calling it's `filter`.
    
    Parameters
    ----------
    frame_proxy : ``FrameProxyBase``
        Frame proxy to check whether a frame should be ignored.
    
    Returns
    -------
    should_ignore_frame : `bool`
        Whether the frame should be ignored.
    """
    try:
        lines = IGNORED_FRAME_LINES[frame_proxy.file_name, frame_proxy.name]
    except KeyError:
        return False
    
    if frame_proxy.line not in lines:
        return False
    
    return True


if not DEFAULT_IGNORED_FRAMES:
    @copy_docs(_should_ignore_frame)
    def _should_ignore_frame(file_name, name, line):
        return False


def should_ignore_frame(frame_proxy, *, filter = None):
    """
    Returns whether the given frame should be ignored from rending.
    
    Parameters
    ----------
    frame_proxy : ``FrameProxyBase``
        Frame proxy to check whether a frame should be ignored.
    
    filter : `None`, `callable` = `None`, Optional (Keyword only)
        Additional filter to check whether a frame should be shown.
    
    Returns
    -------
    should_ignore : `bool`
    """
    if _should_ignore_frame(frame_proxy):
        return True
    
    if (filter is not None):
        if CallableAnalyzer(filter).get_non_reserved_positional_parameter_count() == 1:
            if not filter(frame_proxy):
                return True
        
        else:
            warn(
                f'`should_ignore_frame` now passes `1` parameter to `filter`, but a filter given with different '
                f'amount. Please update your filter function to accept `1`. Got {format_builtin(filter)!s}.'
            )
            if not filter(frame_proxy.file_name, frame_proxy.name, frame_proxy.line_index, frame_proxy.line):
                return True
    
    return False



# ---- Ignore frames / module_rich_attribute_error ----

from .. import rich_attribute_error as module_rich_attribute_error

ignore_frame(
    module_rich_attribute_error.__spec__.origin, '__getattr__', 'raise AttributeError(self, attribute_name)'
)


del module_rich_attribute_error


# ---- Ignore frames / function_tools ----

from .. import function_tools as module_function_tools

ignore_frame(
    module_function_tools.__spec__.origin,
    '__call__',
    'return self.function(*self.positional_parameters)',
)
ignore_frame(
    module_function_tools.__spec__.origin,
    '__call__',
    'return self.function(*self.positional_parameters, **keyword_parameters)',
)

del module_function_tools
