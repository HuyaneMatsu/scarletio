import vampytest

from ..frame_ignoring import should_ignore_frame
from ..frame_proxy import FrameProxyVirtual
from ..expression_parsing import ExpressionInfo


def test__should_ignore_frame__do_not_ignore():
    """
    Tests whether ``should_ignore_frame`` works as intended.
    
    Case: do not ignore.
    """    
    file_name = 'satori.py'
    name = 'sit'
    line = 'koishi()'
    
    frame_proxy = FrameProxyVirtual.from_fields(file_name = file_name, name = name)
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, [line], 0, True)
    
    output = should_ignore_frame(frame_proxy)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def test__should_ignore_frame__ignore_from_defaults():
    """
    Tests whether ``should_ignore_frame`` works as intended.
    
    Case: do not ignore.
    """    
    file_name = 'satori.py'
    name = 'sit'
    line = 'koishi()'
    
    frame_proxy = FrameProxyVirtual.from_fields(file_name = file_name, name = name)
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, [line], 0, True)
    
    mocked = vampytest.mock_globals(should_ignore_frame, 2, IGNORED_FRAME_LINES = {(file_name, name): {line}})
    output = mocked(frame_proxy)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__should_ignore_frame__ignore_from_filter():
    """
    Tests whether ``should_ignore_frame`` works as intended.
    
    Case: do not ignore.
    """    
    file_name = 'satori.py'
    name = 'sit'
    line = 'koishi()'
    
    def filter(frame):
        nonlocal file_name
        nonlocal name
        nonlocal line
        
        if frame.file_name != file_name:
            return True
        
        if frame.name != name:
            return True
        
        if frame.line != line:
            return True
        
        return False
    
    frame_proxy = FrameProxyVirtual.from_fields(file_name = file_name, name = name)
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, [line], 0, True)
    
    output = should_ignore_frame(frame_proxy, filter = filter)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)
