import vampytest

from ..frame_ignoring import should_keep_frame_from_defaults
from ..frame_proxy import FrameProxyVirtual
from ..expression_parsing import ExpressionInfo


def test__should_keep_frame_from_defaults__do_not_ignore():
    """
    Tests whether ``should_keep_frame_from_defaults`` works as intended.
    
    Case: do not ignore.
    """    
    file_name = 'satori.py'
    name = 'sit'
    line = 'koishi()'
    
    frame_proxy = FrameProxyVirtual.from_fields(file_name = file_name, name = name)
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, [line], 0, True)
    
    output = should_keep_frame_from_defaults(frame_proxy)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, True)


def test__should_keep_frame_from_defaults__ignore_from_defaults():
    """
    Tests whether ``should_keep_frame_from_defaults`` works as intended.
    
    Case: do not ignore.
    """    
    file_name = 'satori.py'
    name = 'sit'
    line = 'koishi()'
    
    frame_proxy = FrameProxyVirtual.from_fields(file_name = file_name, name = name)
    frame_proxy.expression_info = ExpressionInfo(frame_proxy.expression_key, [line], 0, True)
    
    mocked = vampytest.mock_globals(should_keep_frame_from_defaults, 2, IGNORED_FRAME_LINES = {(file_name, name): {line}})
    output = mocked(frame_proxy)
    
    vampytest.assert_instance(output, bool)
    vampytest.assert_eq(output, False)
