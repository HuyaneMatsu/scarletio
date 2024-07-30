import vampytest

from ..frame_ignoring import should_keep_frame_from_filter
from ..frame_proxy import FrameProxyVirtual
from ..expression_parsing import ExpressionInfo


def test__should_keep_frame_from_filter__do_not_ignore():
    """
    Tests whether ``should_keep_frame_from_filter`` works as intended.
    
    Case: do not ignore.
    """    
    file_name = 'satori.py'
    name = 'sit'
    line = 'koishi()'
    
    
    def filter(frame):
        return True
    
    frame_proxy = FrameProxyVirtual.from_fields(file_name = file_name, name = name)
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, [line], 0, True)
    
    output = should_keep_frame_from_filter(frame_proxy, filter)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__should_keep_frame_from_filter__ignore_from_filter():
    """
    Tests whether ``should_keep_frame_from_filter`` works as intended.
    
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
    
    output = should_keep_frame_from_filter(frame_proxy, filter = filter)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
