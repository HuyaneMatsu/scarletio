import vampytest

from ..header_building_and_parsing import build_content_disposition_header


def _iter_options__passing():
    yield 'attachment', {}, True, 'attachment'
    yield 'attachment', {'koishi': 'love'}, True, 'attachment; koishi="love"'
    yield 'attachment', {'koishi': 'love', 'satori': 'sees'}, True, 'attachment; koishi="love"; satori="sees"'
    yield 'attachment', {'koishi': 'love[]'}, True, 'attachment; koishi="love[]"'
    yield 'attachment', {'koishi': ' "ko"lv\\'}, True, 'attachment; koishi="\\ \\"ko\\"lv\\\\"'
    yield 'attachment', {'koishi': 'bűn'}, True, 'attachment; koishi*=utf-8\'\'b%C5%B1n'
    yield 'attachment', {'koishi': 'bűn "\\'}, False, 'attachment; koishi="bűn \\"\\\\"'


def _iter_options__bad_type():
    yield 'koishi loves', {}, True
    yield 'bűn', {}, True
    yield '', {}, True


def _iter_options__bad_parameter():
    yield 'attachment', {'koishi loves': 'hey'}, True
    yield 'attachment', {'bűn': 'hey'}, True
    yield 'attachment', {'': 'hey'}, True


@vampytest._(vampytest.call_from(_iter_options__passing()).returning_last())
@vampytest._(vampytest.call_from(_iter_options__bad_type()).raising(ValueError))
@vampytest._(vampytest.call_from(_iter_options__bad_parameter()).raising(ValueError))
def test__build_content_disposition_header(disposition_type, parameters, quote_fields):
    """
    Tests whether ``build_content_disposition_header`` works as intended.

    Parameters
    ----------
    disposition_type : `str`
        Disposition type. Can be one of following: `'inline'`, `'attachment'`, '`form-data`'.
    parameters : `dict` of (`str`, `str`) items
        Disposition parameters.
    quote_fields : `bool`
        Whether field values should be quoted.
    
    Returns
    -------
    output : `str`
    
    Raises
    ------
    ValueError
    """
    return build_content_disposition_header(disposition_type, parameters, quote_fields)
