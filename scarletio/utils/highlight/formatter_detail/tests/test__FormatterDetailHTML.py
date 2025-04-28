from html import escape as html_escape

import vampytest

from ..html import FormatterDetailHTML


def _assert_fields_set(formatter_detail):
    """
    Asserts whether every fields are set of the given formatter detail.
    
    Parameters
    ----------
    formatter_detail : ``FormatterDetail``
        The formatter detail to test.
    """
    vampytest.assert_instance(formatter_detail, FormatterDetailHTML)
    vampytest.assert_instance(formatter_detail.html_class, str, nullable = True)


def test__FormatterDetail__new():
    """
    Tests whether ``FormatterDetail.__new__`` works as intended.
    """
    html_class = 'pudding'
    
    formatter_detail = FormatterDetailHTML(html_class)
    _assert_fields_set(formatter_detail)
    
    vampytest.assert_eq(formatter_detail.html_class, html_class)


def test__FormatterDetail__repr():
    """
    Tests whether ``FormatterDetail.__repr__`` works as intended.
    """
    html_class = 'pudding'
    
    formatter_detail = FormatterDetailHTML(html_class)
    
    output = repr(formatter_detail)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    keyword_parameters = {
        'html_class': 'pudding',
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
            'html_class': 'flan',
        },
        False,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__FormatterDetailHTML__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``FormatterDetailHTML.__eq__`` works as intended.
    
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
    formatter_detail_0 = FormatterDetailHTML(**keyword_parameters_0)
    formatter_detail_1 = FormatterDetailHTML(**keyword_parameters_1)
    
    output = formatter_detail_0 == formatter_detail_1
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__start():
    yield (
        {
            'html_class': None,
        },
        [],
    )
    
    yield (
        {
            'html_class': 'pudding',
        },
        ['<span class="', 'pudding', '">'],
    )


@vampytest._(vampytest.call_from(_iter_options__start()).returning_last())
def test__FormatterDetailHTML__start(keyword_parameters):
    """
    Tests whether ``FormatterDetailHTML.start`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail = FormatterDetailHTML(**keyword_parameters)
    
    output = [*formatter_detail.start()]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output


def _iter_options__transform_content():
    yield (
        {
            'html_class': None,
        },
        '\n',
        ['<br>'],
    )
    
    yield (
        {
            'html_class': None,
        },
        'miau',
        ['miau'],
    )
    
    yield (
        {
            'html_class': None,
        },
        'áááá',
        [html_escape('áááá')],
    )


@vampytest._(vampytest.call_from(_iter_options__transform_content()).returning_last())
def test__FormatterDetailHTML__transform_content(keyword_parameters, content):
    """
    Tests whether ``FormatterDetailHTML.transform_content`` works as intended.
    
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
    formatter_detail = FormatterDetailHTML(**keyword_parameters)
    
    output = [*formatter_detail.transform_content(content)]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output


def _iter_options__end():
    yield (
        {
            'html_class': None,
        },
        [],
    )
    
    yield (
        {
            'html_class': 'pudding',
        },
        ['</span>'],
    )


@vampytest._(vampytest.call_from(_iter_options__end()).returning_last())
def test__FormatterDetailHTML__end(keyword_parameters):
    """
    Tests whether ``FormatterDetailHTML.end`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail = FormatterDetailHTML(**keyword_parameters)
    
    output = [*formatter_detail.end()]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output


def _iter_options__transition():
    yield (
        {
            'html_class': None,
        },
        {
            'html_class': None,
        },
        [],
    )
    
    yield (
        {
            'html_class': 'pudding',
        },
        {
            'html_class': 'pudding',
        },
        [],
    )
    
    yield (
        {
            'html_class': None,
        },
        {
            'html_class': 'pudding',
        },
        ['<span class="', 'pudding', '">'],
    )
    
    yield (
        {
            'html_class': 'pudding',
        },
        {
            'html_class': None,
        },
        ['</span>'],
    )
    
    yield (
        {
            'html_class': 'pudding',
        },
        {
            'html_class': 'flan',
        },
        ['</span>', '<span class="', 'flan', '">'],
    )


@vampytest._(vampytest.call_from(_iter_options__transition()).returning_last())
def test__FormatterDetailHTML__transition(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``FormatterDetailHTML.transition`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail_0 = FormatterDetailHTML(**keyword_parameters_0)
    formatter_detail_1 = FormatterDetailHTML(**keyword_parameters_1)
    
    output = [*formatter_detail_0.transition(formatter_detail_1)]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output
