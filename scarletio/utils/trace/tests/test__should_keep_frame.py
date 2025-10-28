import vampytest

from ..frame_ignoring import should_keep_frame
from ..frame_proxy import FrameProxyVirtual
from ..tests.helper_create_dummy_expression_info import create_dummy_expression_info


def test__should_keep_frame__do_not_ignore():
    """
    Tests whether ``should_keep_frame`` works as intended.
    
    Case: do not ignore.
    """    
    file_name = 'satori.py'
    name = 'sit'
    line = 'koishi()'
    
    frame_proxy = FrameProxyVirtual.from_fields(file_name = file_name, name = name)
    frame_proxy.expression_info = create_dummy_expression_info(frame_proxy.expression_key, line)
    
    output = should_keep_frame(frame_proxy)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__should_keep_frame__ignore_from_defaults():
    """
    Tests whether ``should_keep_frame`` works as intended.
    
    Case: do not ignore.
    """    
    file_name = 'satori.py'
    name = 'sit'
    line = 'koishi()'
    
    frame_proxy = FrameProxyVirtual.from_fields(file_name = file_name, name = name)
    frame_proxy.expression_info = create_dummy_expression_info(frame_proxy.expression_key, line)
    
    mocked = vampytest.mock_globals(should_keep_frame, 2, IGNORED_FRAME_LINES = {(file_name, name): {line}})
    output = mocked(frame_proxy)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)


def test__should_keep_frame__ignore_from_filter():
    """
    Tests whether ``should_keep_frame`` works as intended.
    
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
    frame_proxy.expression_info = create_dummy_expression_info(frame_proxy.expression_key, line)
    
    output = should_keep_frame(frame_proxy, filter = filter)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
