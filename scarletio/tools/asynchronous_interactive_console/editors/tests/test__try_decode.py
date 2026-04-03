import vampytest

from ..editor_advanced import try_decode


def test__try_decode():
    """
    Tests whether ``try_decode`` works as intended.
    """
    for input_value, expected_output_content, expected_output_data in (
        (b'Shrine Road', 'Shrine Road', None),
        (b'Shrine \xe6\x9d', 'Shrine ', b'\xe6\x9d'),
        (b'Shire \xe6\x9d | \xe6\x9d Road', 'Shire \\xe6\\x9d | \\xe6\\x9d Road', None),
        (b'Shire \xe6\x9d Road \xe6\x9d', 'Shire \\xe6\\x9d Road ', b'\xe6\x9d'),
    ):
        
        content, data = try_decode(input_value)
        vampytest.assert_eq(content, expected_output_content)
        vampytest.assert_eq(data, expected_output_data)
