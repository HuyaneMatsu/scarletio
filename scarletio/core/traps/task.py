__all__ = ('Task',)

import reprlib, sys
from threading import current_thread
from types import AsyncGeneratorType as CoroutineGeneratorType, CoroutineType, GeneratorType

from ...utils import alchemy_incendiary, copy_docs, ignore_frame, include, render_frames_into
from ...utils.trace import format_callback, format_coroutine, render_exception_into

from ..exceptions import CancelledError, InvalidStateError

from .future import (
    FUTURE_STATE_FINISHED, FUTURE_STATE_PENDING, FUTURE_STATE_RETRIEVED, Future, get_exception_short_representation,
    get_future_state_name
)


ignore_frame(__spec__.origin, 'get_result', 'raise exception')
ignore_frame(__spec__.origin, '__iter__', 'yield self')
ignore_frame(__spec__.origin, '_step', 'result = coroutine.throw(exception)')
ignore_frame(__spec__.origin, '_step', 'result = coroutine.send(None)')
ignore_frame(__spec__.origin, '_wake_up', 'future.get_result()')
ignore_frame(__spec__.origin, '__call__', 'future.get_result()')

EventThread = include('EventThread')


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
    
    _exception : `None`, `BaseException`
        The exception raised by task's internal coroutine. Defaults to `None`.
    _loop : ``EventThread``
        The loop to what the created task is bound.
    _result : `None`, `Any`
        The result of the task. Defaults to `None`.
    _state : `str`
        The state of the task.
        
        Can be set as one of the following:
        
        +---------------------------+-----------+
        | Respective name           | Value     |
        +===========================+===========+
        | FUTURE_STATE_PENDING      | `0`       |
        +---------------------------+-----------+
        | FUTURE_STATE_CANCELLED    | `1`       |
        +---------------------------+-----------+
        | FUTURE_STATE_FINISHED     | `2`       |
        +---------------------------+-----------+
        | FUTURE_STATE_RETRIEVED    | `3`       |
        +---------------------------+-----------+
        
        Note, that states are checked by memory address and not by equality. Also ``FUTURE_STATE_RETRIEVED`` is used
        only if `__debug__` is set as `True`.
    
    _coroutine : `CoroutineType`, `GeneratorType`
        The wrapped coroutine.
    _should_cancel : `bool`
        Whether the task is cancelled, and at it's next step a ``CancelledError`` would be raised into it's coroutine.
    _waited_future : `None`, ``Future``
        The future on what's result the future is waiting right now.
    """
    __slots__ = ('_coroutine', '_should_cancel', '_waited_future')
    
    def __new__(cls, coroutine, loop):
        """
        Creates a new ``Task`` object running the given coroutine on the given event loop.
        
        Parameters
        ----------
        coroutine : `CoroutineType`, `GeneratorType`
            The coroutine, what the task will on the respective event loop.
        loop : ``EventThread``
            The event loop on what the coroutine will run.
        """
        self = object.__new__(cls)
        self._loop = loop
        self._state = FUTURE_STATE_PENDING

        self._result = None
        self._exception = None
        
        self._callbacks = []
        self._blocking = False

        self._should_cancel = False
        self._waited_future = None
        self._coroutine = coroutine
        
        loop.call_soon(self._step)

        return self
    
    
    def get_stack(self, limit=-1):
        """
        Return the list of stack frames for the task. If the task is already done, returns an empty list.
        
        Parameters
        ----------
        limit : `int` = `-1`, Optional
            The maximal amount of stacks to fetch. By giving it as negative integer, there will be no stack limit
            to fetch back.
        
        Returns
        -------
        frames : `list` of `frame`
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
    
    
    def __repr__(self):
        """Returns the task's representation."""
        repr_parts = ['<', self.__class__.__name__, ' ']
        
        state = self._state
        repr_parts.append(get_future_state_name(state))
        
        if self._should_cancel:
            repr_parts.append(' (cancelling)')
        
        repr_parts.append(' coroutine = ')
        repr_parts.append(format_coroutine(self._coroutine))
        
        waited_future = self._waited_future
        if waited_future is not None:
            repr_parts.append(', waits for = ')
            if type(waited_future) is type(self):
                repr_parts.append(waited_future.qualname)
            else:
                repr_parts.append(repr(waited_future))
        
        if (not self._should_cancel) and (state >= FUTURE_STATE_FINISHED):
            exception = self._exception
            if exception is None:
                result = self._result
                if (result is not None):
                    repr_parts.append(', result = ')
                    repr_parts.append(reprlib.repr(result))
            else:
                repr_parts.append(', exception = ')
                repr_parts.append(get_exception_short_representation(exception))
        
        callbacks = self._callbacks
        limit = len(callbacks)
        if limit:
            repr_parts.append(', callbacks = [')
            index = 0
            while True:
                callback = callbacks[index]
                repr_parts.append(format_callback(callback))
                index += 1
                if index == limit:
                    break
                
                repr_parts.append(', ')
                continue
            
            repr_parts.append(']')
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
    def print_stack(self, limit=-1, file=None):
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
        
        exception = self._exception
        
        if exception is None:
            frames = self.get_stack(limit)
            if frames:
                recursive = (frames[-1] is None)
                if recursive:
                    del frames[-1]
                
                extracted = ['Stack for ', repr(self), ' (most recent call last):\n']
                extracted = render_frames_into(frames, extend=extracted)
                if recursive:
                    extracted.append(
                        'Last frame is a repeat from a frame above. Rest of the recursive part is not rendered.'
                    )
            else:
                extracted = ['No stack for ', repr(self), '\n']
        else:
            extracted = ['Traceback for ', repr(self), ' (most recent call last):\n']
            extracted = render_exception_into(exception, extend=extracted)
        
        file.write(''.join(extracted))
    
    if __debug__:
        @copy_docs(Future.cancel)
        def cancel(self):
            state = self._state
            if state != FUTURE_STATE_PENDING:
                if state == FUTURE_STATE_FINISHED:
                    self._state = FUTURE_STATE_RETRIEVED
                
                return 0
            
            waited_future = self._waited_future
            if (waited_future is None) or (not waited_future.cancel()):
                self._should_cancel = True
            
            return 1
        
    else:
        @copy_docs(Future.cancel)
        def cancel(self):
            if self._state != FUTURE_STATE_PENDING:
                return 0
            
            waited_future = self._waited_future
            if (waited_future is None) or (not waited_future.cancel()):
                self._should_cancel = True
            
            return 1
    
    
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
        
        
    def set_result(self, result):
        """
        Tasks do not support `.set_result` operation.
        
        Parameters
        ----------
        result : `Any`
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
        result : `Any`
            The object to set as result.
        
        Raises
        ------
        RuntimeError
            Tasks do not support `.set_result_if_pending` operation.
        """
        raise RuntimeError(
            f'`{self.__class__.__name__}` does not support `.set_result_if_pending` operation.'
        )
    
    
    # We will not send an exception to a task, but we will cancel it.
    # The exception will show up as ``._exception`` tho.
    # We also wont change the state of the Task, it will be changed, when the next `._step` is done with the
    # #cancelling.
    @copy_docs(Future.set_exception)
    def set_exception(self, exception):
        if self._state != FUTURE_STATE_PENDING:
            raise InvalidStateError(self, 'set_exception')
        
        if (self._waited_future is None) or self._waited_future.cancel():
            self._should_cancel = True
        
        if isinstance(exception, type):
            exception = exception()
        
        if isinstance(exception, StopIteration):
            raise TypeError(
                f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
            )
        
        self._exception = exception
    
    
    @copy_docs(Future.set_exception_if_pending)
    def set_exception_if_pending(self, exception):
        if self._state != FUTURE_STATE_PENDING:
            return 0
        
        if (self._waited_future is None) or self._waited_future.cancel():
            self._should_cancel = True
        
        if isinstance(exception, type):
            exception = exception()
        
        if isinstance(exception, StopIteration):
            raise TypeError(
                f'{exception} cannot be raised to a(n) `{self.__class__.__name__}`; {self!r}.'
            )
        
        self._exception = exception
        return 1
    
    
    def clear(self):
        """
        Tasks do not support `.clear` operation.
        
        Raises
        ------
        RuntimeError
            Tasks do not support `.clear` operation.
        """
        raise RuntimeError(
            f'`{self.__class__.__name__}` does not support `.clear` operation.'
        )
    
    
    def _step(self):
        """
        Does a step, by giving control to the wrapped coroutine by the task.
        
        Raises
        ------
        InvalidStateError
            If the task is already done.
        """
        if self._state != FUTURE_STATE_PENDING:
            raise InvalidStateError(
                self,
                '_step',
                message = f'`{self.__class__.__name__}._step` already done of {self!r}.',
            )
        
        coroutine = self._coroutine
        self._waited_future = None
        
        self._loop.current_task = self
        try:
            # Get cancellation exception
            if self._should_cancel:
                self._should_cancel = False
                
                exception = self._exception
                if exception is None:
                    exception = CancelledError()
            
                # call either coroutine.throw(err) or coroutine.send(None).
                result = coroutine.throw(exception)
            else:
                result = coroutine.send(None)
            
        except StopIteration as exception:
            if self._should_cancel:
                # the task is cancelled meanwhile
                self._should_cancel = False
                Future.set_exception(self, CancelledError())
            else:
                Future.set_result(self, exception.value)
        
        except CancelledError:
            Future.cancel(self)
        
        except BaseException as exception:
            Future.set_exception(self, exception)
        
        else:
            if isinstance(result, Future) and result._blocking:
                result._blocking = False
                result.add_done_callback(self._wake_up)
                self._waited_future = result
                if self._should_cancel:
                    if result.cancel():
                        self._should_cancel = False
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
            self._step()
        finally:
            # set self as `None`, so when exception occurs, self can be garbage collected.
            self = None
