import vampytest

from ..name_deduplication import (
    NAME_DEDUPLICATOR_REGEX_PATTERN_DEFAULT, name_deduplicator_default, name_deduplicator_name_reconstructor_default
)


def _iter_options():
    # increment
    yield (
        ['orin/miau.png', 'orin/miau.png', 'orin/miau.png'],
        ['orin/miau.png', 'orin/miau (1).png', 'orin/miau (2).png'],
    )
    
    # dodge
    yield (
        ['orin/miau (1).png', 'orin/miau.png', 'orin/miau.png'],
        ['orin/miau (1).png', 'orin/miau.png', 'orin/miau (2).png'],
    )
    
    # auto start from bottom
    yield (
        ['orin/miau (5).png', 'orin/miau (5).png', 'orin/miau (5).png'],
        ['orin/miau (5).png', 'orin/miau.png', 'orin/miau (1).png'],
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__name_deduplicator_default(input_names):
    """
    Tests whether ``name_deduplicator_default`` works as intended.
    
    Parameters
    ----------
    input_names : `list<str>`
        The names to input.
    
    Returns
    -------
    output_names : `list<str>`
    """
    name_deduplicator = name_deduplicator_default(
        NAME_DEDUPLICATOR_REGEX_PATTERN_DEFAULT, name_deduplicator_name_reconstructor_default
    )
    name_deduplicator.send(None)
    
    output_names = []
    
    for name in input_names:
        output_name = name_deduplicator.send(name)
        vampytest.assert_instance(output_name, str)
        output_names.append(output_name)
    
    return output_names
