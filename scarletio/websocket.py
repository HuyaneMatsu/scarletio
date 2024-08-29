from .web_socket import *
from .web_socket import __all__

from warnings import warn

warn(
    f'`websocket` has been renamed to `web_socket`. Only name is deprecated and will be removed in 2025 August.',
    FutureWarning,
    stacklevel = 2,
)
