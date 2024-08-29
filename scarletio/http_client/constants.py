__all__ = ()

from hashlib import md5, sha1, sha256
from re import compile as re_compile
from ssl import (
    OP_NO_COMPRESSION as SSL_OPTION_NO_COMPRESSION, OP_NO_SSLv2 as SSL_OPTION_NO_SSL_V2,
    OP_NO_SSLv3 as SSL_OPTION_SSL_NO_SSL_V3, PROTOCOL_SSLv23 as SSL_PROTOCOL_TLS, SSLContext
)

from ..web_common.headers import ACCEPT, ACCEPT_ENCODING


REQUEST_TIMEOUT_DEFAULT = 60.0
HOST_INFO_CACHE_TIMEOUT = 10.0
CONNECTION_KEEP_ALIVE_TIMEOUT = 15.0


DEFAULT_HEADERS = (
    (ACCEPT, '*/*'),
    (ACCEPT_ENCODING, 'gzip, deflate'),
)


HASH_FUNCTION_BY_DIGEST_LENGTH = {
    16: md5,
    20: sha1,
    32: sha256,
}


JSON_RE = re_compile(r'^application/(?:[\w.+-]+?\+)?json')


SSL_CONTEXT_UNVERIFIED = SSLContext(SSL_PROTOCOL_TLS)
SSL_CONTEXT_UNVERIFIED.options |= SSL_OPTION_NO_SSL_V2 | SSL_OPTION_SSL_NO_SSL_V3 | SSL_OPTION_NO_COMPRESSION
SSL_CONTEXT_UNVERIFIED.set_default_verify_paths()
