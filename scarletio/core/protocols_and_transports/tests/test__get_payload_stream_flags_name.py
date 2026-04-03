import vampytest

from ..payload_stream import (
    STREAM_FLAG_DONE_ABORTED, STREAM_FLAG_DONE_CANCELLED, STREAM_FLAG_DONE_EXCEPTION, STREAM_FLAG_DONE_SUCCESS,
    STREAM_FLAG_WAIT_CHUNK, STREAM_FLAG_WAIT_WHOLE, _get_payload_stream_flags_name
)


def _iter_options():
    yield 0, 'none'
    yield STREAM_FLAG_WAIT_WHOLE, 'wait~whole'
    yield STREAM_FLAG_WAIT_CHUNK, 'wait~chunk'
    yield STREAM_FLAG_DONE_SUCCESS, 'done~success'
    yield STREAM_FLAG_DONE_EXCEPTION, 'done~exception'
    yield STREAM_FLAG_DONE_CANCELLED, 'done~cancelled'
    yield STREAM_FLAG_DONE_ABORTED, 'done~aborted'
    yield STREAM_FLAG_WAIT_CHUNK | STREAM_FLAG_DONE_CANCELLED, 'wait~chunk, done~cancelled'


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__get_payload_stream_flags_name(flags):
    """
    Tests whether ``test__get_payload_stream_flags_name`` works as intended.
    
    Parameters
    ----------
    flags : `int`
        Flags to get their name of.
    
    Returns
    -------
    output : `str`
    """
    output = _get_payload_stream_flags_name(flags)
    vampytest.assert_instance(output, str)
    return output
