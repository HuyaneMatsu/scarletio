import vampytest

from ..resolve_configuration import merge_configuration


def _iter_options():
    yield (
        {},
        {
            'nyan' : {
                'key': 'value',
            },
        },
        {
            'nyan' : {
                'key': 'value',
            },
        },
    )
    
    yield (
        {
            'nyan' : {
                'key': 'value',
            },
        },
        {
            'nyan' : {
                'key': 'cook',
            },
        },
        {
            'nyan' : {
                'key': 'cook',
            },
        },
    )
    
    yield (
        {
            'nyan' : {
                'key': 'value',
            },
        },
        {
            'nyan' : {
                'key': '',
            },
        },
        {
            'nyan' : {
                'key': 'value',
            },
        },
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__merge_configuration(merge_to, merge_from):
    """
    Tests whether ``merge_configuration`` works as intended.
    
    Parameters
    ----------
    merge_to : `dict<str, dict<str, str>>`
        The original configuration to merge the other one to.
    
    merge_from : `dict<str, dict<str, str>>`
        Configuration to merge from.
    
    Returns
    -------
    output : `dict<str, dict<str, str>>`
    """
    merge_to = {section_name : section.copy() for section_name, section in merge_to.items()}
    merge_configuration(merge_to, merge_from)
    return merge_to
