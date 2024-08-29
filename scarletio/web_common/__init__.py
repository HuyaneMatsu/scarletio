from .basic_auth import *
from .compressors import *
from .cookiejar import *
from .exceptions import *
from .form_data import *
from .header_building_and_parsing import *
from .headers import *
from .helpers import *
from .http_message import *
from .http_protocol import *
from .http_stream_writer import *
from .mime_type import *
from .multipart import *
from .quoting import *
from .url import *
from .web_socket_frame import *

from . import headers

__all__ = (
    'headers',
    *basic_auth.__all__,
    *compressors.__all__,
    *cookiejar.__all__,
    *exceptions.__all__,
    *form_data.__all__,
    *header_building_and_parsing.__all__,
    *headers.__all__,
    *helpers.__all__,
    *http_message.__all__,
    *http_protocol.__all__,
    *http_stream_writer.__all__,
    *mime_type.__all__,
    *multipart.__all__,
    *quoting.__all__,
    *url.__all__,
    *web_socket_frame.__all__,
)


# Deprecations

from warnings import warn

def __getattr__(attribute_name):
    if attribute_name == 'Formdata':
        warn(
            (
                f'`Formdata` has been renamed to `FormData`.'
                f'`Formdata` will be removed in 2025 August.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return FormData
    
    raise AttributeError(attribute_name)
