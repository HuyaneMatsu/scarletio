import vampytest

from ..helpers import iter_labels_with_searches
from ..resolve_configuration import ResolveConfiguration


def _iter_options():
    resolve_configuration = ResolveConfiguration()
    resolve_configuration.option_required_dot_count = 1
    resolve_configuration.searches = None
    resolve_configuration.searches_fallback = None
    
    yield (
        resolve_configuration,
        None,
        [],
    )
    
    resolve_configuration = ResolveConfiguration()
    resolve_configuration.option_required_dot_count = 1
    resolve_configuration.searches = (
        (b'wanna',),
        (b'cart', b'people'),
    )
    resolve_configuration.searches_fallback = None
    
    yield (
        resolve_configuration,
        None,
        [
            (b'wanna',),
            (b'cart', b'people'),
        ],
    )
    
    resolve_configuration = ResolveConfiguration()
    resolve_configuration.option_required_dot_count = 1
    resolve_configuration.searches = None
    resolve_configuration.searches_fallback = None
    
    yield (
        resolve_configuration,
        (b'hey', b'mister'),
        [
            (b'hey', b'mister'),
        ],
    )
    
    resolve_configuration = ResolveConfiguration()
    resolve_configuration.option_required_dot_count = 2
    resolve_configuration.searches = None
    resolve_configuration.searches_fallback = None
    
    yield (
        resolve_configuration,
        (b'hey', b'mister'),
        [
            (b'hey', b'mister'),
        ],
    )
    
    resolve_configuration = ResolveConfiguration()
    resolve_configuration.option_required_dot_count = 1
    resolve_configuration.searches = (
        (b'wanna',),
        (b'cart', b'people'),
    )
    resolve_configuration.searches_fallback = None
    
    yield (
        resolve_configuration,
        (b'hey', b'mister'),
        [
            (b'hey', b'mister'),
        ],
    )
    
    resolve_configuration = ResolveConfiguration()
    resolve_configuration.option_required_dot_count = 2
    resolve_configuration.searches = (
        (b'wanna',),
        (b'cart', b'people'),
    )
    resolve_configuration.searches_fallback = None
    
    yield (
        resolve_configuration,
        (b'hey', b'mister'),
        [
            (b'wanna', b'hey', b'mister'),
            (b'cart', b'people', b'hey', b'mister'),
            (b'hey', b'mister'),
        ],
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__iter_labels_with_searches(sort_list, initial_labels):
    """
    Tests whether ``iter_labels_with_searches`` works as intended.
    
    Parameters
    ----------
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration.
    
    initial_labels : `None | tuple<bytes>`
        Labels to query.
    
    Returns
    -------
    output : `list<tuple<bytes>>`
    """
    output = [*iter_labels_with_searches(sort_list, initial_labels)]
    for element in output:
        vampytest.assert_instance(element, tuple)
    return output
