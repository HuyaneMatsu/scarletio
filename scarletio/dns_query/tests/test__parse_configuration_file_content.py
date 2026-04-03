import vampytest

from ..resolve_configuration import parse_configuration_file_content


def _iter_options():
    yield (
        (
            '# comment\n'
            '   # comment\n'
            'uhum=no\n'
            '   [section] # comment\n'
            '  key = value   \n'
            'shrimp =   \n'
            '   fry  \n'
            '[cook]\n'
            'yummy=yes\n'
            '[cooked]'
        ),
        {
            '' : {
                'uhum' : 'no',
            },
            'section' : {
                'key' : 'value',
                'shrimp' : '',
                'fry' : '',
            },
            'cook' : {
                'yummy' : 'yes',
            },
        },
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__parse_configuration_file_content(content):
    """
    Tests whether ``parse_configuration_file_content`` works as intended.
    
    Parameters
    ----------
    content : `str`
        The file's content.
    
    Returns
    -------
    output : `dict<str, dict<str, str>>`
    """
    output = parse_configuration_file_content(content)
    
    vampytest.assert_instance(output, dict)
    for section_name, section in output.items():
        vampytest.assert_instance(section_name, str)
        vampytest.assert_instance(section, dict)
        for key, value in section.items():
            vampytest.assert_instance(key, str)
            vampytest.assert_instance(value, str)
    
    return output
