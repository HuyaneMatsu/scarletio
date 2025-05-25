import vampytest

from ...exceptions import CancelledError
from ...top_level import create_event_loop

from ..future import Future
from ..future_repr import (
    EXCEPTION_REPR_LENGTH_MAX, get_exception_short_representation, render_callbacks_into, render_coroutine_into,
    render_future_into, render_result_into, render_state_into, render_waits_into
)
from ..future_states import FUTURE_STATE_CANCELLED, FUTURE_STATE_RESULT_RAISE, FUTURE_STATE_RESULT_RETURN
from ..task import Task


def _callback_0():
    pass


def _callback_1():
    pass


async def _coroutine_0():
    pass


def _iter_options__get_exception_short_representation():
    yield ValueError(), 'ValueError()'
    yield ValueError('hi'), 'ValueError(\'hi\')'
    yield ValueError('a' * (EXCEPTION_REPR_LENGTH_MAX + 1)), '<ValueError ...>'


@vampytest._(vampytest.call_from(_iter_options__get_exception_short_representation()).returning_last())
def test__get_exception_short_representation(input_value):
    """
    Tests whether ``get_exception_short_representation`` works as intended.
    
    Parameters
    ----------
    input_value : `BaseException`
        Exception to get its representation of.
    
    Returns
    -------
    output : `str`
    """
    return get_exception_short_representation(input_value)


def _iter_options__render_callbacks_into():
    yield (
        False,
        None,
        (
            '',
            False,
        )
    )
    
    yield (
        True,
        None,
        (
            '',
            True,
        )
    )
    
    yield (
        False,
        [],
        (
            '',
            False,
        )
    )
    
    yield (
        True,
        [],
        (
            '',
            True,
        )
    )
    
    yield (
        False,
        [_callback_0, _callback_1],
        (
            ' callbacks = [_callback_0(), _callback_1()]',
            True,
        )
    )
    
    yield (
        True,
        [_callback_0, _callback_1],
        (
            ', callbacks = [_callback_0(), _callback_1()]',
            True,
        )
    )


@vampytest._(vampytest.call_from(_iter_options__render_callbacks_into()).returning_last())
def test__render_callbacks_into(field_added, callbacks):
    """
    Tests whether ``render_callbacks_into`` works as intended.
    
    Parameters
    ----------
    field_added : `bool`
        Whether any fields were added already.
    callbacks : `None | list<callable>`
        The callbacks to render.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    into, field_added = render_callbacks_into([], field_added, callbacks)
    return ''.join(into), field_added


def _iter_options__render_state_into():
    yield (
        False,
        0,
        (
            ' state = pending',
            True,
        )
    )
    
    yield (
        True,
        0,
        (
            ', state = pending',
            True,
        )
    )


@vampytest._(vampytest.call_from(_iter_options__render_state_into()).returning_last())
def test__render_state_into(field_added, state):
    """
    Tests whether ``render_state_into`` works as intended.
    
    Parameters
    ----------
    field_added : `bool`
        Whether any fields were added already.
    state : `int`
        The state of the future stored as a bitwise flags.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    into, field_added = render_state_into([], field_added, state)
    return ''.join(into), field_added


def _iter_options__render_result_into():
    yield (
        False,
        FUTURE_STATE_CANCELLED,
        None,
        (
            '',
            False,
        )
    )
    
    yield (
        True,
        FUTURE_STATE_CANCELLED,
        None,
        (
            '',
            True,
        )
    )
    
    yield (
        False,
        FUTURE_STATE_CANCELLED | FUTURE_STATE_RESULT_RAISE,
        CancelledError(),
        (
            '',
            False,
        )
    )
    
    yield (
        True,
        FUTURE_STATE_CANCELLED | FUTURE_STATE_RESULT_RAISE,
        CancelledError(123),
        (
            ', cancellation_exception = CancelledError(123)',
            True,
        )
    )
    
    yield (
        False,
        FUTURE_STATE_CANCELLED | FUTURE_STATE_RESULT_RAISE,
        ValueError(),
        (
            ' cancellation_exception = ValueError()',
            True,
        )
    )
    
    yield (
        True,
        FUTURE_STATE_CANCELLED | FUTURE_STATE_RESULT_RAISE,
        ValueError(),
        (
            ', cancellation_exception = ValueError()',
            True,
        )
    )

    yield (
        False,
        FUTURE_STATE_CANCELLED | FUTURE_STATE_RESULT_RAISE,
        ValueError('a' * (EXCEPTION_REPR_LENGTH_MAX + 1)), 
        (
            ' cancellation_exception = <ValueError ...>',
            True,
        )
    )
    
    yield (
        False,
        FUTURE_STATE_RESULT_RAISE,
        ValueError(),
        (
            ' exception = ValueError()',
            True,
        )
    )
    
    yield (
        True,
        FUTURE_STATE_RESULT_RAISE,
        ValueError(),
        (
            ', exception = ValueError()',
            True,
        )
    )
    
    yield (
        False,
        FUTURE_STATE_RESULT_RAISE,
        ValueError('a' * (EXCEPTION_REPR_LENGTH_MAX + 1)), 
        (
            ' exception = <ValueError ...>',
            True,
        )
    )
    
    yield (
        False,
        FUTURE_STATE_RESULT_RETURN,
        None,
        (
            ' result = None',
            True,
        ),
    )

    yield (
        True,
        FUTURE_STATE_RESULT_RETURN,
        None,
        (
            ', result = None',
            True,
        ),
    )

    yield (
        False,
        FUTURE_STATE_RESULT_RETURN,
        69,
        (
            ' result = 69',
            True,
        ),
    )

    yield (
        False,
        FUTURE_STATE_RESULT_RETURN,
        'koishi',
        (
            ' result = \'koishi\'',
            True,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options__render_result_into()).returning_last())
def test__render_result_into(field_added, state, result):
    """
    Tests whether ``render_result_into`` works as intended.
    
    Parameters
    ----------
    field_added : `bool`
        Whether any fields were added already.
    state : `int`
        The state of the future stored as a bitwise flags.
    result : `object`
        Future result.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    into, field_added = render_result_into([], field_added, state, result)
    return ''.join(into), field_added


def _iter_options__render_coroutine_into():
    coroutine = object()
    
    yield (
        False,
        coroutine,
        (
            ' coroutine = <object() from unknown location; unknown state>',
            True,
        ),
    )
    
    yield (
        True,
        coroutine,
        (
            ', coroutine = <object() from unknown location; unknown state>',
            True,
        ),
    )


@vampytest._(vampytest.call_from(_iter_options__render_coroutine_into()).returning_last())
def test__render_coroutine_into(field_added, coroutine):
    """
    Tests whether ``render_coroutine_into`` works as intended.
    
    Parameters
    ----------
    field_added : `bool`
        Whether any fields were added already.
    coroutine : `CoroutineType`, `GeneratorType`
        The coroutine to render.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    into, field_added = render_coroutine_into([], field_added, coroutine)
    return ''.join(into), field_added


def _iter_options__render_waits_into():
    loop = create_event_loop()
    try:
        yield (
            False,
            None,
            (
                '',
                False,
            ),
        )
        
        yield (
            True,
            None,
            (
                '',
                True,
            ),
        )
        
        future = Future(loop)
        
        yield (
            False,
            future,
            (
                f' waits = {future!r}',
                True,
            ),
        )
        
        yield (
            True,
            future,
            (
                f', waits = {future!r}',
                True,
            ),
        )
        
        task = Task(loop, _coroutine_0())
        
        yield (
            False,
            task,
            (
                f' waits = <{task.__class__.__name__} coroutine = {task.qualname}, ...>',
                True,
            ),
        )
        
        yield (
            True,
            task,
            (
                f', waits = <{task.__class__.__name__} coroutine = {task.qualname}, ...>',
                True,
            ),
        )
    finally:
        loop.stop()


@vampytest._(vampytest.call_from(_iter_options__render_waits_into()).returning_last())
def test__render_waits_into(field_added, future):
    """
    Tests whether ``render_waits_into`` works as intended.
    
    Parameters
    ----------
    field_added : `bool`
        Whether any fields were added already.
    future : ``Future```
        The coroutine to render.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    into, field_added = render_waits_into([], field_added, future)
    return ''.join(into), field_added


def _iter_options__render_future_into():
    loop = create_event_loop()
    try:
        future = Future(loop)
        
        yield (
            False,
            future,
            (
                f' future = <{future.__class__.__name__} ...>',
                True,
            ),
        )
        
        yield (
            True,
            future,
            (
                f', future = <{future.__class__.__name__} ...>',
                True,
            ),
        )
        
        task = Task(loop, _coroutine_0())
        
        yield (
            False,
            task,
            (
                f' future = <{task.__class__.__name__} ...>',
                True,
            ),
        )
        
        yield (
            True,
            task,
            (
                f', future = <{task.__class__.__name__} ...>',
                True,
            ),
        )
    finally:
        loop.stop()


@vampytest._(vampytest.call_from(_iter_options__render_future_into()).returning_last())
def test__render_future_into(field_added, future):
    """
    Tests whether ``render_future_into`` works as intended.
    
    Parameters
    ----------
    field_added : `bool`
        Whether any fields were added already.
    future : ``Future```
        The coroutine to render.
    
    Returns
    -------
    into : `list<str>`
    field_added : `bool`
    """
    into, field_added = render_future_into([], field_added, future)
    return ''.join(into), field_added
