__all__ = ('Task',)

import sys
from datetime import datetime as DateTime
from threading import current_thread
from types import AsyncGeneratorType as CoroutineGeneratorType, CoroutineType, GeneratorType
from warnings import warn

from ...utils import alchemy_incendiary, copy_docs, export, ignore_frame, include, render_frames_into
from ...utils.trace import render_exception_into

from ..exceptions import CancelledError, InvalidStateError

from .future import Future
from .future_repr import (
    render_callbacks_into, render_coroutine_into, render_result_into, render_state_into, render_waits_into
)
from .future_states import (
    FUTURE_STATE_CANCELLED, FUTURE_STATE_CANCELLING_SELF, FUTURE_STATE_DESTROYED, FUTURE_STATE_MASK_DONE,
    FUTURE_STATE_RESULT_RAISE, FUTURE_STATE_RESULT_RETURN, FUTURE_STATE_SILENCED
)


FUTURE_MASK_CANCEL_WITH_EXCEPTION = FUTURE_STATE_RESULT_RAISE | FUTURE_STATE_CANCELLED


ignore_frame(__spec__.origin, 'get_result', 'raise self._result')
ignore_frame(__spec__.origin, '__iter__', 'yield self')
ignore_frame(__spec__.origin, '_step', 'result = self._coroutine.throw(CancelledError())')
ignore_frame(__spec__.origin, '_step', 'result = self._coroutine.send(None)')

EventThread = include('EventThread')

CONSTRUCTOR_CHANGE_DEPRECATED = DateTime.utcnow() > DateTime(2023, 12, 12)


@export
class Task(Future):
    """
    A Future-like object that runs a Python coroutine.
    
    Tasks are used to run coroutines in event loops. If a coroutine awaits on a ``Future`, the ``Task`` suspends the
    execution of the coroutine and waits for the completion of the ``Future``. When the ``Future`` is done, the
    execution of the wrapped coroutine resumes.
    
    Attributes
    ----------
    _blocking : `bool`
        Whether the task is already being awaited, so it blocks the respective coroutine.
    
    _callbacks : `list` of `callable`
        The callbacks of the task, which are queued up on the respective event loop to be called, when the task is
        finished. These callback should accept `1` parameter, the task itself.
        
        Note, if the task is already done, then the newly added callbacks are queued up instantly on the respective
        event loop to be called.
    
    _coroutine : `CoroutineType`, `GeneratorType`
        The wrapped coroutine.
    
    _loop : ``EventThread``
        The loop to what the created task is bound.
    
    _result : `None`, `object`
        The result of the task. Defaults to `None`.
    
    _state : `str`
        The state of the task.
    
    _waited_future : `None`, ``Future``
        The future on what's result the future is waiting right now.
    """
    __slots__ = ('_coroutine', '_waited_future')
    
    def __new__(cls, loop, coroutine):
        """
        Creates a new ``Task`` object running the given coroutine on the given event loop.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop on what the coroutine will run.
        
        coroutine : `CoroutineType`, `GeneratorType`
            The coroutine, what the task will on the respective event loop.
        """
        if isinstance(coroutine, EventThread):
            loop, coroutine = coroutine, loop
            
            if CONSTRUCTOR_CHANGE_DEPRECATED:
                warn(
                    (
                        f'`{cls.__name__}(coroutine, loop)` is deprecated and will be removed in 2024 Jun.'
                        f'Please use `{cls.__name__}(loop, coroutine)` instead accordingly.'
                    ),
                    FutureWarning,
                    stacklevel = 2,
                )
        
        self = object.__new__(cls)
        self._blocking = False
        self._callbacks = []
        self._coroutine = coroutine
        self._loop = loop
        self._result = None
        self._state = 0
        self._waited_future = None
        
        loop.call_soon(self._step)
        
        return self
    
    
    def __repr__(self):
        """Returns the task's representation."""
        repr_parts = ['<', self.__class__.__name__]
        
        state = self._state
        repr_parts, field_added = render_state_into(repr_parts, False, state)
        repr_parts, field_added = render_coroutine_into(repr_parts, field_added, self._coroutine)
        repr_parts, field_added = render_waits_into(repr_parts, field_added, self._waited_future)
        repr_parts, field_added = render_result_into(repr_parts, field_added, state, self._result)
        repr_parts, field_added = render_callbacks_into(repr_parts, field_added, self._callbacks)
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    @copy_docs(Future.cancel)
    def cancel(self):
        state = self._state
        
        if state & FUTURE_STATE_MASK_DONE:
            state |= FUTURE_STATE_SILENCED
            result = 0
        else:
            waited_future = self._waited_future
            if (waited_future is None) or (not waited_future.cancel()):
                state |= FUTURE_STATE_CANCELLING_SELF
            
            result = 1
        
        self._state = state
        return result
    
    
    @copy_docs(Future.cancel_with)
    def cancel_with(self, exception):
        state = self._state
        if state & FUTURE_STATE_MASK_DONE:
            state |= FUTURE_STATE_SILENCED
            result = 0
        
        else:
            if isinstance(exception, type):
                exception = exception()
            
            if isinstance(exception, StopIteration):
                raise TypeError(
                    f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
                )
            
            waited_future = self._waited_future
            if (waited_future is None) or waited_future.cancel():
                state |= FUTURE_STATE_CANCELLING_SELF
            
            self._result = exception
            result = 1
        
        self._state = state
        return result
    
    
    @copy_docs(Future.is_cancelling)
    def is_cancelling(self):
        waited_future = self._waited_future
        if (waited_future is not None):
            return waited_future.is_cancelled() or waited_future.is_cancelling()
        
        return Future.is_cancelling(self)
    
    
    def set_result(self, result):
        """
        Tasks do not support `.set_result` operation.
        
        Parameters
        ----------
        result : `object`
            The object to set as result.
        
        Raises
        ------
        RuntimeError
            Tasks do not support `.set_result` operation.
        """
        raise RuntimeError(
            f'`{self.__class__.__name__}` does not support `.set_result` operation.'
        )
    
    
    def set_result_if_pending(self, result):
        """
        Tasks do not support `.set_result_if_pending` operation.
        
        Parameters
        ----------
        result : `object`
            The object to set as result.
        
        Raises
        ------
        RuntimeError
            Tasks do not support `.set_result_if_pending` operation.
        """
        raise RuntimeError(
            f'`{self.__class__.__name__}` does not support `.set_result_if_pending` operation.'
        )
    
    
    @copy_docs(Future.set_exception)
    def set_exception(self, exception):
        """
        Tasks do not support `.set_exception` operation.
        
        Parameters
        ----------
        exception : `BaseException`, `type<BaseException>`
            The exception to set as the task's exception.
        
        Raises
        ------
        RuntimeError
            Tasks do not support `.set_exception` operation.
        """
        raise RuntimeError(
            f'`{self.__class__.__name__}` does not support `.set_exception` operation.'
        )
    
    
    @copy_docs(Future.set_exception_if_pending)
    def set_exception_if_pending(self, exception):
        """
        Tasks do not support `.set_exception_if_pending` operation.
        
        Parameters
        ----------
        exception : `BaseException`, `type<BaseException>`
            The exception to set as the task's exception.
        
        Raises
        ------
        RuntimeError
            Tasks do not support `.set_exception_if_pending` operation.
        """
        raise RuntimeError(
            f'`{self.__class__.__name__}` does not support `.set_exception_if_pending` operation.'
        )
    
    
    # Task running
    
    def _step(self):
        """
        Does a step, by giving control to the wrapped coroutine by the task.
        
        Raises
        ------
        InvalidStateError
            If the task is already done.
        """
        state = self._state
        if state & FUTURE_STATE_MASK_DONE:
            # If a task is destroyed it may happen that we are still stepping it.
            if state & FUTURE_STATE_DESTROYED:
                return
            
            raise InvalidStateError(
                self,
                '_step',
                message = f'`{self.__class__.__name__}._step` already done of {self!r}.',
            )
        
        self._loop.current_task = self
        
        try:
            # Call either coroutine.throw(err) or coroutine.send(None).
            if state & FUTURE_STATE_CANCELLING_SELF:
                state &= ~FUTURE_STATE_CANCELLING_SELF
                self._state = state
                
                result = self._coroutine.throw(CancelledError())
            else:
                result = self._coroutine.send(None)
            
        except StopIteration as retrieved_exception:
            # Cancellation has higher priority than result
            state = self._state
            if state & FUTURE_STATE_CANCELLING_SELF:
                state |= FUTURE_STATE_CANCELLED
                
                if (self._result is not None):
                    state |= FUTURE_STATE_RESULT_RAISE
                
            else:
                self._result = retrieved_exception.value
                state |= FUTURE_STATE_RESULT_RETURN
            
            self._state = state
            self._loop._schedule_callbacks(self)
        
        except CancelledError as retrieved_exception:
            self._state |= FUTURE_MASK_CANCEL_WITH_EXCEPTION
            
            result = self._result
            if (result is None):
                self._result = retrieved_exception
            else:
                result.__cause__ = retrieved_exception
            
            self._loop._schedule_callbacks(self)
        
        except BaseException as retrieved_exception:
            # Exception has higher priority than cancellation
            self._result = retrieved_exception
            self._state |= FUTURE_STATE_RESULT_RAISE
            self._loop._schedule_callbacks(self)
        
        else:
            if isinstance(result, Future) and result._blocking:
                result._blocking = False
                result.add_done_callback(self._wake_up)
                
                self._waited_future = result
                
                state = self._state
                if state & FUTURE_STATE_CANCELLING_SELF:
                    if result.cancel():
                        self._state = state & ~FUTURE_STATE_CANCELLING_SELF
            else:
                self._loop.call_soon(self._step)
        
        finally:
            self._loop.current_task = None
            self = None # Need to set `self` as `None`. Else `self` might never get garbage collected.
    
    
    def _wake_up(self, future):
        """
        Callback used by ``._step`` when the wrapped coroutine waits on a future to be marked as done.
        
        Parameters
        ----------
        future : ``Future``
            The future for what's completion the task is waiting for.
        """
        try:
            self._waited_future = None
            
            self._step()
        finally:
            # set self as `None`, so when exception occurs, self can be garbage collected.
            self = None
    
    
    # Task utils

    @property
    def name(self):
        """
        Returns the task's wrapped coroutine's name.
        
        Returns
        -------
        name : `str`
        """
        coroutine = self._coroutine
        try:
            return coroutine.__name__
        except AttributeError:
            return coroutine.__class__.__name__
    
    
    @property
    def qualname(self):
        """
        Returns the task's wrapped coroutine's qualname.
        
        Returns
        -------
        qualname : `str`
        """
        coroutine = self._coroutine
        try:
            return coroutine.__qualname__
        except AttributeError:
            return coroutine.__class__.__qualname__
    
    # Stack related | will need a rewrite # TODO
    
    def get_stack(self, limit = -1):
        """
        Return the list of stack frames for the task. If the task is already done, returns an empty list.
        
        If there are recursive frames puts `None` at the end of the list.
        
        Parameters
        ----------
        limit : `int` = `-1`, Optional
            The maximal amount of stacks to fetch. By giving it as negative integer, there will be no stack limit
            to fetch back.
        
        Returns
        -------
        frames : `list` of (`None`, `FrameType`)
            The stack frames of the task.
        """
        frames = []
        
        coroutine = self._coroutine
        if isinstance(coroutine, GeneratorType):
            frame = coroutine.gi_frame
        elif isinstance(coroutine, CoroutineType):
            frame = coroutine.cr_frame
        elif isinstance(coroutine, CoroutineGeneratorType):
            frame = coroutine.ag_frame
        else:
            frame = None
        
        if frame is None:
            return frames
        
        while limit:
            limit -= 1
            
            if frame in frames:
                frames.append(frame)
                frames.append(None)
                return frames
            
            frames.append(frame)
            
            if isinstance(coroutine, GeneratorType):
                coroutine = coroutine.gi_yieldfrom
            elif isinstance(coroutine, CoroutineType):
                coroutine = coroutine.cr_await
            elif isinstance(coroutine, CoroutineGeneratorType):
                coroutine = coroutine.ag_await
            else:
                coroutine = None
            
            if coroutine is not None:
                if isinstance(coroutine, GeneratorType):
                    frame = coroutine.gi_frame
                elif isinstance(coroutine, CoroutineType):
                    frame = coroutine.cr_frame
                elif isinstance(coroutine, CoroutineGeneratorType):
                    frame = coroutine.ag_frame
                else:
                    frame = None
                
                if frame is not None:
                    continue
            
            self = self._waited_future
            if self is None:
                break
            
            del frames[-1]
            if not isinstance(self, Task):
                break
            
            coroutine = self._coroutine
            
            if isinstance(coroutine, GeneratorType):
                frame = coroutine.gi_frame
            elif isinstance(coroutine, CoroutineType):
                frame = coroutine.cr_frame
            elif isinstance(coroutine, CoroutineGeneratorType):
                frame = coroutine.ag_frame
            else:
                frame = None
                
            if frame is None:
                break
        
        return frames
    
    
    def print_stack(self, limit = -1, file = None):
        """
        Prints the stack or traceback of the task.
        
        Parameters
        ----------
        limit : `int` = `-1`, Optional
            The maximal amount of stacks to print. By giving it as negative integer, there will be no stack limit
            to print out.
        file : `None`, `I/O stream` = `None`, Optional
            The file to print the stack to. Defaults to `sys.stderr`.
        
        Notes
        -----
        If the task is finished with an exception, then `limit` is ignored when printing traceback.
        """
        local_thread = current_thread()
        if isinstance(local_thread, EventThread):
            return local_thread.run_in_executor(alchemy_incendiary(self._print_stack, (self, limit, file),))
        else:
            self._print_stack(self, limit, file)
    
    
    @staticmethod
    def _print_stack(self, limit, file):
        """
        Prints the stack or traceback of the task to the given `file`.
        
        Parameters
        ----------
        limit : `int`
            The maximal amount of stacks to print. By giving it as negative integer, there will be no stack limit
            to print out,
        file : `None`, `I/O stream`
            The file to print the stack to. Defaults to `sys.stderr`.
        
        Notes
        -----
        This function calls blocking operations and should not run inside of an event loop.
        
        If the task is finished with an exception, then `limit` is ignored when printing traceback.
        """
        if file is None:
            file = sys.stdout
        
        if self._state & FUTURE_STATE_RESULT_RAISE:
            exception = self._result
        else:
            exception = None
        
        if exception is None:
            frames = self.get_stack(limit)
            if frames:
                recursive = (frames[-1] is None)
                if recursive:
                    del frames[-1]
                
                extracted = ['Stack for ', repr(self), ' (most recent call last):\n']
                extracted = render_frames_into(frames, extend = extracted)
                if recursive:
                    extracted.append(
                        'Last frame is a repeat from a frame above. Rest of the recursive part is not rendered.'
                    )
            else:
                extracted = ['No stack for ', repr(self), '\n']
        else:
            extracted = ['Traceback for ', repr(self), ' (most recent call last):\n']
            extracted = render_exception_into(exception, extend = extracted)
        
        file.write(''.join(extracted))
    
    # Deprecations
    
    @property
    def _should_cancel(self):
        """
        Deprecated and will be removed in 2024 february.
        """
        warn(
            f'`{self.__class__.__name__}._should_cancel` is deprecated and will be removed in 2024 february.',
            FutureWarning,
            stacklevel = 2,
        )
        return True if self._state & FUTURE_STATE_CANCELLING_SELF else False
    
    
    @_should_cancel.setter
    def _should_cancel(self, value):
        warn(
            f'`{self.__class__.__name__}._should_cancel` is deprecated and will be removed in 2024 february.',
            FutureWarning,
            stacklevel = 2,
        )
        state = self._state
        if value:
            state |= FUTURE_STATE_CANCELLING_SELF
        else:
            state &= ~FUTURE_STATE_CANCELLING_SELF
        
        self._state = state
