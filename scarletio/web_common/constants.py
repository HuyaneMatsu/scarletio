__all__ = ()

from re import compile as re_compile


KEEP_ALIVE_HEADER_RP = re_compile('\\s*([^ \\t=]+)\\s*=\\s*([^ \\t,$]+)\\s*(?:,|$)')

KEEP_ALIVE_CONNECTION_TIMEOUT_DEFAULT = 15.0
KEEP_ALIVE_MAX_REQUESTS_DEFAULT = 0

KEEP_ALIVE_CONNECTION_TIMEOUT_KEY = 'timeout'
KEEP_ALIVE_MAX_REQUESTS_KEY = 'max'
