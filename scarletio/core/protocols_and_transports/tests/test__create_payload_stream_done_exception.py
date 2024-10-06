import vampytest

from ..payload_stream import _create_payload_stream_done_exception


def test__create_payload_stream_done_exception():
    """
    Tests whether ``_create_payload_stream_done_exception`` works as intended.
    """
    output = _create_payload_stream_done_exception(0)
    vampytest.assert_instance(output, ConnectionError)
