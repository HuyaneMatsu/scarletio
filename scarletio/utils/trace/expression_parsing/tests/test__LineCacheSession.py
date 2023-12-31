import vampytest

from ..cache_constants import LINE_CACHE_SESSIONS
from ..line_cache_session import LineCacheSession


def test__LineCacheSession__new():
    """
    Tests whether ``LineCacheSession.__new__`` works as intended
    """
    session = LineCacheSession()
    
    vampytest.assert_instance(session, LineCacheSession)
    vampytest.assert_instance(session.memorized_file_infos, set)
    

def test__LineCacheSession__repr():
    """
    Tests whether ``LineCacheSession.__repr__`` works as intended
    """
    session = LineCacheSession()
    
    output = repr(session)
    vampytest.assert_instance(output, str)
    

def test__LineCacheSession__context():
    """
    Tests whether ``LineCacheSession`` context works as intended
    """
    session = LineCacheSession()
    
    vampytest.assert_eq(LINE_CACHE_SESSIONS, set())
    
    with session:
        vampytest.assert_eq(LINE_CACHE_SESSIONS, {session})
    
    vampytest.assert_eq(LINE_CACHE_SESSIONS, set())
