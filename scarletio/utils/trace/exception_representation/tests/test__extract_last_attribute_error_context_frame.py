import vampytest

from ....rich_attribute_error import AttributeError as RichAttributeError

from ...frame_proxy import FrameProxyVirtual

from ..attribute_error_helpers import extract_last_attribute_error_context_frame


def test__extract_last_attribute_error_context_frame__no_frame():
    """
    Tests whether ``extract_last_attribute_error_context_frame`` works as intended.
    
    Case: no frame.
    """
    frames = []
    exception = AttributeError()
    
    output = extract_last_attribute_error_context_frame(exception, frames)
    vampytest.assert_is(output, None)


def test__extract_last_attribute_error_context_frame__has_frame():
    """
    Tests whether ``extract_last_attribute_error_context_frame`` works as intended.
    
    Case: has frame.
    """
    frames = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py'),
        FrameProxyVirtual.from_fields(file_name = 'satori.py'),
    ]
    exception = AttributeError()
    
    output = extract_last_attribute_error_context_frame(exception, frames)
    vampytest.assert_is(output, frames[-1])


def test__extract_last_attribute_error_context_frame__ignore_rich_getattr():
    """
    Tests whether ``extract_last_attribute_error_context_frame`` works as intended.
    
    Case: ignoro rich getattr frame.
    """
    frames = [
        FrameProxyVirtual.from_fields(file_name = 'koishi.py'),
        FrameProxyVirtual.from_fields(file_name = 'satori.py', name = '__getattr__'),
    ]
    exception = RichAttributeError(object(), 'hey_mister')
    
    output = extract_last_attribute_error_context_frame(exception, frames)
    vampytest.assert_is(output, frames[-2])
