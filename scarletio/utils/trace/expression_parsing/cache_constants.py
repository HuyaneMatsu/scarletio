__all__ = ()


from ...weak_value_dictionary import WeakValueDictionary

from collections import OrderedDict


CONSOLE_INPUT_CACHE = OrderedDict()
CONSOLE_INPUT_MAX_SIZE = 1000000
CONSOLE_INPUT_CACHE_OUTFLOW_CHECK = 17

FILE_INFO_CACHE = WeakValueDictionary()

LINE_CACHE_SESSIONS = set()
