import vampytest

from ...ansi import ANSITextDecoration

from ..ansi import FormatterDetailANSI


def _assert_fields_set(formatter_detail):
    """
    Asserts whether every fields are set of the given formatter detail.
    
    Parameters
    ----------
    formatter_detail : ``FormatterDetail``
        The formatter detail to test.
    """
    vampytest.assert_instance(formatter_detail, FormatterDetailANSI)
    vampytest.assert_instance(formatter_detail.background_color, tuple, nullable = True)
    vampytest.assert_instance(formatter_detail.foreground_color, tuple, nullable = True)
    vampytest.assert_instance(formatter_detail.text_decoration, int, nullable = True)


def test__FormatterDetail__new():
    """
    Tests whether ``FormatterDetail.__new__`` works as intended.
    """
    text_decoration = ANSITextDecoration.bold
    background_color = (4, 6, 8)
    foreground_color = (12, 24, 36)
    
    formatter_detail = FormatterDetailANSI(text_decoration, background_color, foreground_color)
    _assert_fields_set(formatter_detail)
    
    vampytest.assert_eq(formatter_detail.text_decoration, text_decoration)
    vampytest.assert_eq(formatter_detail.background_color, background_color)
    vampytest.assert_eq(formatter_detail.foreground_color, foreground_color)


def test__FormatterDetail__repr():
    """
    Tests whether ``FormatterDetail.__repr__`` works as intended.
    """
    text_decoration = ANSITextDecoration.bold
    background_color = (4, 6, 8)
    foreground_color = (12, 24, 36)
    
    formatter_detail = FormatterDetailANSI(text_decoration, background_color, foreground_color)
    
    output = repr(formatter_detail)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    keyword_parameters = {
        'text_decoration': ANSITextDecoration.bold,
        'background_color': (4, 6, 8),
        'foreground_color': (12, 24, 36),
    }
    
    yield (
        keyword_parameters,
        keyword_parameters,
        True,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'text_decoration': ANSITextDecoration.dim,
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'background_color': (4, 12, 8),
        },
        False,
    )
    
    yield (
        keyword_parameters,
        {
            **keyword_parameters,
            'foreground_color': (12, 26, 36),
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__FormatterDetailANSI__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``FormatterDetailANSI.__eq__`` works as intended.
    
    Parameters
    ----------
    keyword_parameters_0 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    keyword_parameters_1 : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `bool`
    """
    formatter_detail_0 = FormatterDetailANSI(**keyword_parameters_0)
    formatter_detail_1 = FormatterDetailANSI(**keyword_parameters_1)
    
    output = formatter_detail_0 == formatter_detail_1
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__start():
    yield (
        {},
        [],
    )
    
    yield (
        {
            'text_decoration': ANSITextDecoration.bold,
            'background_color': (4, 6, 8),
            'foreground_color': (12, 24, 36),
        },
        [
            '\033[', str(ANSITextDecoration.bold), ';', '48;2;', '4', ';', '6', ';', '8', ';', '38;2;', '12', ';',
            '24', ';', '36', 'm'
        ],
    )


@vampytest._(vampytest.call_from(_iter_options__start()).returning_last())
def test__FormatterDetailANSI__start(keyword_parameters):
    """
    Tests whether ``FormatterDetailANSI.start`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail = FormatterDetailANSI(**keyword_parameters)
    
    output = [*formatter_detail.start()]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output


def _iter_options__transform_content():
    yield (
        {},
        '\n',
        ['\n'],
    )
    
    yield (
        {},
        'miau',
        ['miau'],
    )
    
    yield (
        {},
        'áááá',
        ['áááá'],
    )


@vampytest._(vampytest.call_from(_iter_options__transform_content()).returning_last())
def test__FormatterDetailANSI__transform_content(keyword_parameters, content):
    """
    Tests whether ``FormatterDetailANSI.transform_content`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Parameters
    ----------
    content : `str`
        Content to transform.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail = FormatterDetailANSI(**keyword_parameters)
    
    output = [*formatter_detail.transform_content(content)]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output


def _iter_options__end():
    yield (
        {},
        [
            '\033[', '0', 'm'
        ],
    )


@vampytest._(vampytest.call_from(_iter_options__end()).returning_last())
def test__FormatterDetailANSI__end(keyword_parameters):
    """
    Tests whether ``FormatterDetailANSI.end`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail = FormatterDetailANSI(**keyword_parameters)
    
    output = [*formatter_detail.end()]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output


def _iter_options__transition():
    yield (
        {},
        {},
        [],
    )
    
    yield (
        {
            'text_decoration': ANSITextDecoration.bold,
            'background_color': (4, 6, 8),
            'foreground_color': (12, 24, 36),
        },
        {
            'text_decoration': ANSITextDecoration.bold,
            'background_color': (4, 6, 8),
            'foreground_color': (12, 24, 36),
        },
        [],
    )
    
    yield (
        {
            'text_decoration': ANSITextDecoration.bold,
            'background_color': (4, 6, 8),
            'foreground_color': (12, 24, 36),
        },
        {
            'text_decoration': ANSITextDecoration.bold,
            'background_color': (4, 6, 8),
            'foreground_color': None,
        },
        [
            '\033[', '0', ';', str(ANSITextDecoration.bold), ';', '48;2;', '4', ';', '6', ';', '8', 'm'
        ],
    )
    
    yield (
        {
            'text_decoration': ANSITextDecoration.bold,
            'background_color': (4, 6, 8),
            'foreground_color': (12, 24, 36),
        },
        {
            'text_decoration': ANSITextDecoration.bold,
            'background_color': (4, 6, 8),
            'foreground_color': (12, 24, 37),
        },
        [
            '\033[', '38;2;', '12', ';', '24', ';', '37', 'm'
        ],
    )


@vampytest._(vampytest.call_from(_iter_options__transition()).returning_last())
def test__FormatterDetailANSI__transition(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``FormatterDetailANSI.transition`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail_0 = FormatterDetailANSI(**keyword_parameters_0)
    formatter_detail_1 = FormatterDetailANSI(**keyword_parameters_1)
    
    output = [*formatter_detail_0.transition(formatter_detail_1)]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output
