import vampytest

from ..url_path import normalize_path_parts


def _iter_options():
    yield None, None
    yield ['hey'], ['hey']
    yield ['hey', 'mister'], ['hey', 'mister']
    
    yield ['.'], None
    yield ['.', ''], None
    yield ['.', '.'], None
    yield ['.', '.', ''], None
    yield ['.', '.', 'hey', 'mister'], ['hey', 'mister']
    yield ['hey', '.', 'mister'], ['hey', 'mister']
    yield ['hey', '.', '.', 'mister'], ['hey', 'mister']
    yield ['hey', 'mister', '.'], ['hey', 'mister', '']
    yield ['hey', 'mister', '.', '.'], ['hey', 'mister', '']
    
    yield ['..'], None
    yield ['..', ''], None
    yield ['..', '..'], None
    yield ['..', '..', ''], None
    yield ['..', 'hey', 'mister'], ['hey', 'mister']
    yield ['hey', '..', 'mister'], ['mister']
    yield ['hey', '..', '..', 'mister'], ['mister']
    yield ['hey', 'mister', '..'], ['hey']
    yield ['hey', 'mister', '..', '..'], None


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__normalize_path_parts(input_value):
    """
    Tests whether ``normalize_path_parts`` works as intended.
    
    Parameters
    ----------
    input_value : `None | list<str>`
        Parts to test on.
    
    Returns
    -------
    output : `None | list<str>`
    """
    if (input_value is not None):
        input_value = input_value.copy()
    
    output = normalize_path_parts(input_value)
    vampytest.assert_instance(output, list, nullable = True)
    return output
