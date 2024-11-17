from math import inf, nan

import vampytest

from ....utils import MultiValueDictionary

from ..url_query import normalize_query


def _iter_options__passing():
    # None
    yield (
        None,
        None,
    )
    
    # String (empty)
    yield (
        '',
        None,
    )
    
    # String
    yield (
        'hey=mister&hey=sister',
        MultiValueDictionary([
            ('hey', 'mister'),
            ('hey', 'sister'),
        ]),
    )
    
    # List (empty)
    yield (
        [],
        None,
    )
    
    # List
    yield (
        [
            ('hey', 'mister'),
            ('hey', 'sister'),
        ],
        MultiValueDictionary([
            ('hey', 'mister'),
            ('hey', 'sister'),
        ]),
    )
    
    # Dict (empty)
    yield (
        {},
        None,
    )
    
    # Dict
    yield (
        {
            'hey': 'mister',
            'hello': 'sister',
        },
        MultiValueDictionary([
            ('hey', 'mister'),
            ('hello', 'sister'),
        ]),
    )
    
    # List (check boolean)
    yield (
        [
            ('boolean', True),
            ('boolean', False),
        ],
        MultiValueDictionary([
            ('boolean', 'true'),
            ('boolean', 'false'),
        ]),
    )
    
    # List (check null)
    yield (
        [
            ('none-type', None),
        ],
        MultiValueDictionary([
            ('none-type', 'null'),
        ]),
    )
    
    # List (check integer)
    yield (
        [
            ('integer', 12),
        ],
        MultiValueDictionary([
            ('integer', '12'),
        ]),
    )
    
    # List (check float)
    yield (
        [
            ('float', 12.5),
        ],
        MultiValueDictionary([
            ('float', '12.5'),
        ]),
    )


def _iter_options__type_error():
    # List (check bytes)
    yield (
        [
            ('byte', b'hey=mister'),
        ],
    )
    
    # Bytes
    yield (
        b'',
    )
    
    # Float
    yield (
        12.5,
    )
    
    # Integer
    yield (
        12,
    )
    
    # Boolean
    yield (
        False,
    )


def _iter_options__value_error():
    # Float (inf)
    yield (
        [
            ('float', inf),
        ],
    )
    
    # Float (nan)
    yield (
        [
            ('float', nan),
        ],
    )


@vampytest._(vampytest.call_from(_iter_options__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__type_error()).raising(TypeError))
@vampytest._(vampytest.call_from(_iter_options__value_error()).raising(ValueError))
def test__normalize_query(value):
    """
    Tests whether ``normalize_query`` works as intended.
    
    Parameters
    ----------
    value : `object`
        Value to parse.
    
    Returns
    -------
    output : `None | MultiValueDictionary<str, str>`
    
    Raises
    ------
    TypeError
    ValueError
    """
    output = normalize_query(value)
    vampytest.assert_instance(output, MultiValueDictionary, nullable = True)
    return output

