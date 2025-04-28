import vampytest

from ..base import FormatterDetailBase


def _assert_fields_set(formatter_detail):
    """
    Asserts whether every fields are set of the given formatter detail.
    
    Parameters
    ----------
    formatter_detail : ``FormatterDetail``
        The formatter detail to test.
    """
    vampytest.assert_instance(formatter_detail, FormatterDetailBase)


def test__FormatterDetail__new():
    """
    Tests whether ``FormatterDetail.__new__`` works as intended.
    """
    formatter_detail = FormatterDetailBase()
    _assert_fields_set(formatter_detail)


def test__FormatterDetail__repr():
    """
    Tests whether ``FormatterDetail.__repr__`` works as intended.
    """
    formatter_detail = FormatterDetailBase()
    
    output = repr(formatter_detail)
    vampytest.assert_instance(output, str)


def _iter_options__eq():
    keyword_parameters = {}
    
    yield (
        keyword_parameters,
        keyword_parameters,
        True,
    )


@vampytest._(vampytest.call_from(_iter_options__eq()).returning_last())
def test__FormatterDetailBase__eq(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``FormatterDetailBase.__eq__`` works as intended.
    
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
    formatter_detail_0 = FormatterDetailBase(**keyword_parameters_0)
    formatter_detail_1 = FormatterDetailBase(**keyword_parameters_1)
    
    output = formatter_detail_0 == formatter_detail_1
    vampytest.assert_instance(output, bool)
    return output


def _iter_options__start():
    yield (
        {},
        [],
    )


@vampytest._(vampytest.call_from(_iter_options__start()).returning_last())
def test__FormatterDetailBase__start(keyword_parameters):
    """
    Tests whether ``FormatterDetailBase.start`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail = FormatterDetailBase(**keyword_parameters)
    
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
def test__FormatterDetailBase__transform_content(keyword_parameters, content):
    """
    Tests whether ``FormatterDetailBase.transform_content`` works as intended.
    
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
    formatter_detail = FormatterDetailBase(**keyword_parameters)
    
    output = [*formatter_detail.transform_content(content)]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output


def _iter_options__end():
    yield (
        {},
        [],
    )


@vampytest._(vampytest.call_from(_iter_options__end()).returning_last())
def test__FormatterDetailBase__end(keyword_parameters):
    """
    Tests whether ``FormatterDetailBase.end`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail = FormatterDetailBase(**keyword_parameters)
    
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


@vampytest._(vampytest.call_from(_iter_options__transition()).returning_last())
def test__FormatterDetailBase__transition(keyword_parameters_0, keyword_parameters_1):
    """
    Tests whether ``FormatterDetailBase.transition`` works as intended.
    
    Parameters
    ----------
    keyword_parameters : `dict<str, object>`
        Keyword parameters to create instance with.
    
    Returns
    -------
    output : `list<str>`
    """
    formatter_detail_0 = FormatterDetailBase(**keyword_parameters_0)
    formatter_detail_1 = FormatterDetailBase(**keyword_parameters_1)
    
    output = [*formatter_detail_0.transition(formatter_detail_1)]
    
    for element in output:
        vampytest.assert_instance(element, str)
    
    return output
