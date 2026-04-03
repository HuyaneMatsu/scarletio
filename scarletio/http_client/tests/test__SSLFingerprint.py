from hashlib import sha256
from ssl import MemoryBIO, PROTOCOL_SSLv23, SSLContext, SSLObject
from types import FunctionType

import vampytest

from ...core import AbstractProtocolBase

from ..ssl_fingerprint import SSLFingerprint

BuiltinFunctionOrMethodType = type(object.__new__)


class TestProtocolType(AbstractProtocolBase):
    __slots__ = ('extra',)
    
    def __new__(cls, extra):
        self = object.__new__(cls)
        self.extra = extra
        return self
    
    
    def get_extra_info(self, name, default = None):
        return self.extra.get(name, default)


class TestSSLObject(SSLObject):
    __slots__ = ('_sslobj', '_certificate', )
    
    __init__ = object.__init__
    
    def __new__(cls, ssl_context, certificate):
        ssl_object = ssl_context._wrap_bio(MemoryBIO(), MemoryBIO(), True, None)
        
        self = object.__new__(cls)
        self._sslobj = ssl_object
        self._certificate = certificate
        return self
    
    
    def getpeercert(self, binary_form = False):
        assert binary_form
        return self._certificate


def _assert_fields_set(fingerprint):
    """
    Tests whether ``SSLFingerprint`` has all of its attributes set.
    """
    vampytest.assert_instance(fingerprint, SSLFingerprint)
    vampytest.assert_instance(fingerprint.hash_function, FunctionType, BuiltinFunctionOrMethodType)
    vampytest.assert_instance(fingerprint.value, bytes)


def test__SSLFingerprint__new():
    """
    Tests whether ``SSLFingerprint.__new__`` works as intended.
    """
    value = b'a' * 32
    
    fingerprint = SSLFingerprint(value)
    _assert_fields_set(fingerprint)
    
    vampytest.assert_eq(fingerprint.value, value)


def test__SSLFingerprint__new__invalid_length():
    """
    Tests whether ``SSLFingerprint.__new__`` works as intended.
    
    Case: Invalid length.
    """
    value = b'a' * 33
    
    try:
        SSLFingerprint(value)
    except ValueError as received_exception:
        exception = received_exception
    else:
        exception = None
    
    vampytest.assert_is_not(exception, None)
    vampytest.assert_in('invalid length', repr(exception).casefold())


def test__SSLFingerprint__new__insecure():
    """
    Tests whether ``SSLFingerprint.__new__`` works as intended.
    
    Case: Insecure.
    """
    value = b'a' * 16
    
    try:
        SSLFingerprint(value)
    except ValueError as received_exception:
        exception = received_exception
    else:
        exception = None
    
    vampytest.assert_is_not(exception, None)
    vampytest.assert_in('insecure', repr(exception).casefold())


def test__SSLFingerprint__eq():
    """
    Tests whether ``SSLFingerprint.__eq__`` works as intended.
    """
    fingerprint_0 = SSLFingerprint(b'a' * 32)
    fingerprint_1 = SSLFingerprint(b'a' * 32)
    fingerprint_2 = SSLFingerprint(b'b' * 32)
    
    vampytest.assert_ne(fingerprint_0, object())
    vampytest.assert_eq(fingerprint_0, fingerprint_1)
    vampytest.assert_ne(fingerprint_0, fingerprint_2)


def test__SSLFingerprint__repr():
    """
    Tests whether ``SSLFingerprint.__repr__`` works as intended.
    """
    value = b'a' * 32
    
    fingerprint = SSLFingerprint(value)
    
    output = repr(fingerprint)
    vampytest.assert_instance(output, str)


def test__SSLFingerprint__hash():
    """
    Tests whether ``SSLFingerprint.__hash__`` works as intended.
    """
    value = b'a' * 32
    
    fingerprint = SSLFingerprint(value)
    
    output = hash(fingerprint)
    vampytest.assert_instance(output, int)


def test__SSLFingerprint__check__success():
    """
    Tests whether ``AbstractProtocolBase.check`` works as intended.
    
    Case: success.
    """
    hash_value = b'abcdefgh' * 64
    value = sha256(hash_value).digest()
    
    ssl_context =  SSLContext(PROTOCOL_SSLv23)
    
    ssl_object = TestSSLObject(ssl_context, hash_value)
    protocol = TestProtocolType({'ssl_object': ssl_object})
    
    fingerprint = SSLFingerprint(value)
    
    fingerprint.check(protocol)


def test__SSLFingerprint__check__failure_different_hash():
    """
    Tests whether ``AbstractProtocolBase.check`` works as intended.
    
    Case: success.
    """
    hash_value_0 = b'abcdefgh' * 64
    hash_value_1 = b'abcdefg0' * 64
    value = sha256(hash_value_0).digest()
    
    ssl_context =  SSLContext(PROTOCOL_SSLv23)
    
    ssl_object = TestSSLObject(ssl_context, hash_value_1)
    protocol = TestProtocolType({'ssl_object': ssl_object})
    
    fingerprint = SSLFingerprint(value)
    
    with vampytest.assert_raises(ValueError):
        fingerprint.check(protocol)


def test__SSLFingerprint__check__no_ssl_object():
    """
    Tests whether ``AbstractProtocolBase.check`` works as intended.
    
    Case: no ssl object.
    """
    hash_value = b'abcdefgh' * 64
    
    value = sha256(hash_value).digest()
    protocol = TestProtocolType({})
    
    fingerprint = SSLFingerprint(value)
    
    fingerprint.check(protocol)
