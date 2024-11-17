__all__ = ()

from re import I as re_ignore_case, compile as re_compile


HOST_RP = re_compile(
    '('
    # Private & local networks
    '(?:(?:10|127)(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}(?:\\.(?:0|[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-5])))|'
    '(?:(?:169\\.254|192\\.168)(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5]))(?:\\.(?:0|[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-5])))|'
    '(?:172\\.(?:1[6-9]|2\\d|3[0-1])(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5]))(?:\\.(?:0|[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-5])))'
    ')'
    '|'
    # Private & local hosts
    '(?:(localhost)(\\.+)?)'
    '|'
    # IP address dotted notation octets. Excludes loop back network 0.0.0.0. Excludes reserved space >= 224.0.0.0.
    # Excludes network & broadcast addresses (first & last IP address of each class)
    '('
    '(?:[1-9]\\d?|1\\d\\d|2[01]\\d|22[0-3])'
    '(?:\\.(?:1?\\d{1,2}|2[0-4]\\d|25[0-5])){2}'
    '(?:\\.(?:0|[1-9]\\d?|1\\d\\d|2[0-4]\\d|25[0-5]))'
    ')'
    '|'
    # IPv6 RegEx
    '\\[('
    # 1:2:3:4:5:6:7:8
    '(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|'
    # 1::                              1:2:3:4:5:6:7::
    '(?:[0-9a-fA-F]{1,4}:){1,7}:|'
    # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
    '(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'
    # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
    '(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|'
    # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
    '(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|'
    # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
    '(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|'
    # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
    '(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|'
    # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8
    '[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|'
    # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::
    ':(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|'
    # fe80::7:8%eth0   fe80::7:8%1
    # (link-local IPv6 addresses with zone index)
    'fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]?|::(?:ffff(?::0{1,4})?:)?(?:(?:25[0-5]|(?:2[0-4]|1?[0-9])?[0-9])\\.){3}'
    # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255
    # (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    '(?:25[0-5]|(?:2[0-4]|1?[0-9])?[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1?[0-9])?[0-9])\\.){3}'
    # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33
    # (IPv4-Embedded IPv6 Address)
    '(?:25[0-5]|(?:2[0-4]|1?[0-9])?[0-9])'
    ')\\]|'
    # host name
    '(?:'
    '(?:('
    '(?:xn--|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]'
    '(?:(?:\\.(?:xn--|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9])*)?'
    ')\\.)?'
    # domain name
    '((?:xn--|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9])'
    # TLD identifier
    '\\.'
    '((?:xn--[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]|[a-z\u00a1-\uffff\U00010000-\U0010ffff]){2,})'
    '(\\.+)?'
    ')',
    re_ignore_case,
)


URL_RP = re_compile(
    # Protocol identifier.
    '(?:([a-z0-9.+-]+?):)?'
    '(?:(?:(?<=:)|(?<=^))(?://)?'
    # `user:pass` authentication.
    '(?:([-a-z\u00a1-\uffff\U00010000-\U0010ffff0-9._~%!$&\'()*+,;=]+?)?'
    '(?::([-a-z\u00a1-\uffff\U00010000-\U0010ffff0-9._~%!$&\'()*+,;=:]+)?)?@)?'
    '(?:'
    f'{HOST_RP.pattern!s}'
    ')'
    # port number
    '(?::(\\d{2,5}))?'
    ')?'
    # resource path
    '(/[-a-z\u00a1-\uffff\U00010000-\U0010ffff0-9._~%!$&\'()*+,;=:@/]*)?'
    # query string
    '(?:\\?(\\S*?)?)?'
    # fragment
    '(?:#(\\S+)?)?',
    re_ignore_case,
)


NoneType = type(None)

DEFAULT_PORTS = {
    'http': 80,
    'https': 443,
    'ws': 80,
    'wss': 443,
}

URL_PART_FLAG_DECODED_SET = 1 << 0
URL_PART_FLAG_ENCODED_SET = 1 << 1

# Host flags
HOST_FLAG_LOCAL_IP_V4 = 1 << 0
HOST_FLAG_LOCAL_NAME = 1 << 1
HOST_FLAG_EXTERNAL_IP_V4 = 1 << 2
HOST_FLAG_EXTERNAL_IP_V6 = 1 << 3
HOST_FLAG_EXTERNAL_NAME = 1 << 4
HOST_FLAG_UNAMBIGUOUS = 1 << 5

HOST_MASK_IP_V4 = HOST_FLAG_LOCAL_IP_V4 | HOST_FLAG_EXTERNAL_IP_V4
HOST_MASK_IP_V6 = HOST_FLAG_EXTERNAL_IP_V6
HOST_MASK_IP_ANY = HOST_MASK_IP_V4 | HOST_MASK_IP_V6

HOST_MASK_NAME_ANY = HOST_FLAG_LOCAL_NAME | HOST_FLAG_EXTERNAL_NAME
HOST_MASK_ANY_LOCAL = HOST_FLAG_LOCAL_IP_V4 | HOST_FLAG_LOCAL_NAME
HOST_MASK_ANY_EXTERNAL = HOST_FLAG_EXTERNAL_IP_V4 | HOST_FLAG_EXTERNAL_IP_V6 | HOST_FLAG_EXTERNAL_NAME
