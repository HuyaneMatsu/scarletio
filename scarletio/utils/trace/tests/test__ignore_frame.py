import vampytest

from ..frame_ignoring import ignore_frame


def test__ignore_frame():
    """
    Tests whether ``ignore_frame`` works as intended.
    """
    ignore_frame_lines_mock = {}
    
    file_name = 'satori.py'
    name = 'sit'
    line = 'koishi()'
    
    mocked = vampytest.mock_globals(ignore_frame, IGNORED_FRAME_LINES = ignore_frame_lines_mock)

    mocked(file_name, name, line)

    vampytest.assert_eq(
        ignore_frame_lines_mock,
        {(file_name, name): {line}},
    )

