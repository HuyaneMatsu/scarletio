import vampytest

from ...utils import MultiValueDictionary

from ..content_type import ContentType, ContentTypeParsingError, parse_content_type


def _iter_options():
    # none
    yield (
        None,
        (
            ContentType.create_empty(),
            None,
        ),
    )
    # empty string
    yield (
        '',
        (
            ContentType.create_empty(),
            None,
        ),
    )
    
    # minimalistic
    yield (
        'koishi',
        (
            ContentType(
                'koishi',
                None,
                None,
                None,
            ),
            None,
        ),
    )
    
    # type_ + space + upper
    yield (
        '   KoiShi   ',
        (
            ContentType(
                'koishi',
                None,
                None,
                None,
            ),
            None,
        ),
    )
    
    # type_ + tab
    yield (
        '\t\tKoiShi\t\t',
        (
            ContentType(
                'koishi',
                None,
                None,
                None,
            ),
            None,
        ),
    )
    
    # sub-type
    yield (
        'koishi/json',
        (
            ContentType(
                'koishi',
                'json',
                None,
                None,
            ),
            None,
        )
    )
    
    # sub-type + space + upper
    yield (
        'koishi/   jSon  ',
        (
            ContentType(
                'koishi',
                'json',
                None,
                None,
            ),
            None,
        )
    )
    
    # sub-type + suffix
    yield (
        'koishi/json+satori',
        (
            ContentType(
                'koishi',
                'json',
                'satori',
                None,
            ),
            None,
        ),
    )
    
    # suffix
    yield (
        'koishi/+satori',
        (
            ContentType(
                'koishi',
                None,
                'satori',
                None,
            ),
            None,
        ),
    )
    
    # suffix + space + upper
    yield (
        'koishi/+   sAtoRi   ',
        (
            ContentType(
                'koishi',
                None,
                'satori',
                None,
            ),
            None,
        ),
    )
    
    # parameter + more
    yield (
        'koishi;hey=nyan;mokou=hot',
        (
            ContentType(
                'koishi',
                None,
                None,
                MultiValueDictionary((
                    ('hey', 'nyan'),
                    ('mokou', 'hot'),
                )),
            ),
            None,
        ),
    )
    
    # parameter + duplicate
    yield (
        'koishi;hey=nyan;hey=nya;hey=;hey=nyan',
        (
            ContentType(
                'koishi',
                None,
                None,
                MultiValueDictionary((
                    ('hey', 'nyan'),
                    ('hey', 'nya'),
                    ('hey', ''),
                )),
            ),
            None,
        ),
    )
    
    # parameter + upper
    yield (
        'koishi;Hey=Nyan',
        (
            ContentType(
                'koishi',
                None,
                None,
                MultiValueDictionary((
                    ('hey', 'Nyan'),
                )),
            ),
            None,
        ),
    )
    
    # parameters + empty
    yield (
        'koishi;=;;',
        (
            ContentType(
                'koishi',
                None,
                None,
                None,
            ),
            None,
        ),
    )
    
    # parameters + space
    yield (
        'koishi;  hey   =    mister',
        (
            ContentType(
                'koishi',
                None,
                None,
                MultiValueDictionary((
                    ('hey', 'mister'),
                )),
            ),
            None,
        ),
    )
    
    # parameters + space + quote
    yield (
        'koishi;  hey   =    "mister \\";\\\\"  ; hey=nyan',
        (
            ContentType(
                'koishi',
                None,
                None,
                MultiValueDictionary((
                    ('hey', 'mister \";\\'),
                    ('hey', 'nyan')
                )),
            ),
            None,
        ),
    )
    
    # unexpected type
    yield (
        'koishi koishi',
        (
            ContentType(
                'koishi',
                None,
                None,
                None
            ),
            ContentTypeParsingError(
                'koishi koishi',
                7,
                ';/'
            ),
        ),
    )
    
    # unexpected sub_type
    yield (
        'koishi/json json',
        (
            ContentType(
                'koishi',
                'json',
                None,
                None
            ),
            ContentTypeParsingError(
                'koishi/json json',
                12,
                ';+'
            ),
        ),
    )
    
    # unexpected affix
    yield (
        'koishi/json+satori satori',
        (
            ContentType(
                'koishi',
                'json',
                'satori',
                None
            ),
            ContentTypeParsingError(
                'koishi/json+satori satori',
                19,
                ';'
            ),
        ),
    )
    
    # unexpected parameter key
    yield (
        'koishi;hey hey=mister',
        (
            ContentType(
                'koishi',
                None,
                None,
                MultiValueDictionary((
                    ('hey', ''),
                )),
            ),
            ContentTypeParsingError(
                'koishi;hey hey=mister',
                11,
                ';='
            ),
        ),
    )
    
    # unexpected parameter value
    yield (
        'koishi;hey=mister mister',
        (
            ContentType(
                'koishi',
                None,
                None,
                MultiValueDictionary((
                    ('hey', 'mister'),
                )),
            ),
            ContentTypeParsingError(
                'koishi;hey=mister mister',
                18,
                ';'
            ),
        ),
    )
    
    # unexpected parameter value (first quoted)
    yield (
        'koishi;hey="mister mister" sister',
        (
            ContentType(
                'koishi',
                None,
                None,
                MultiValueDictionary((
                    ('hey', 'mister mister'),
                )),
            ),
            ContentTypeParsingError(
                'koishi;hey="mister mister" sister',
                27,
                ';'
            ),
        ),
    )
    
    # unexpected parameter value (second quoted)
    yield (
        'koishi;hey=sister "mister mister"',
        (
            ContentType(
                'koishi',
                None,
                None,
                MultiValueDictionary((
                    ('hey', 'sister'),
                )),
            ),
            ContentTypeParsingError(
                'koishi;hey=sister "mister mister"',
                18,
                ';'
            ),
        ),
    )


@vampytest._(vampytest.call_from(_iter_options()).returning_last())
def test__parse_content_type(string):
    """
    Tests whether ``parse_content_type`` works as intended.
    
    Parameters
    ----------
    string : `None | str`
        Value to parse from.
    
    Returns
    -------
    output : `(ContentType, None | ContentTypeParsingError)`
    """
    output = parse_content_type(string)
    vampytest.assert_instance(output, tuple)
    vampytest.assert_eq(len(output), 2)
    vampytest.assert_instance(output[0], ContentType)
    vampytest.assert_instance(output[1], ContentTypeParsingError, nullable = True)
    return output
