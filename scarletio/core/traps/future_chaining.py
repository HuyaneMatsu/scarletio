__all__ = ('shield',)

from ...utils import set_docs

from .future import FUTURE_STATE_FINISHED, FUTURE_STATE_PENDING, FUTURE_STATE_RETRIEVED, Future


class _FutureChainer:
    """
    Chains a future's result into an other one used as a callback of the source future.
    
    Attributes
    ----------
    target : ``Future``
        The target future to chain the result into if applicable.
    """
    __slots__ = ('target',)
    
    def __init__(self, target):
        """
        Creates a new ``_FutureChainer`` with the given target future.
        
        Parameters
        ----------
        target : ``Future``
            The target future to chain the result into if applicable.
        """
        self.target = target
    
    if __debug__:
        def __call__(self, future):
            # remove chain remover
            target = self.target
            callbacks = target._callbacks
            for index in range(len(callbacks)):
                callback = callbacks[index]
                if (type(callback) is _ChainRemover) and (callback.target is future):
                    del callbacks[index]
                    break
            
            # set result
            state = future._state
            if state == FUTURE_STATE_FINISHED:
                future._state = FUTURE_STATE_RETRIEVED
                if future._exception is None:
                    target.set_result(future._result)
                else:
                    target.set_exception(future._exception)
                return
            
            if state == FUTURE_STATE_RETRIEVED:
                if future._exception is None:
                    target.set_result(future._result)
                else:
                    target.set_exception(future._exception)
                return
            
            # if state == FUTURE_STATE_CANCELLED: normally, but the future can be cleared as well.
            target.cancel()
    
    else:
        def __call__(self, future):
            # remove chain remover
            target = self.target
            callbacks = target._callbacks
            for index in range(len(callbacks)):
                callback = callbacks[index]
                if type(callback) is _ChainRemover and callback.target is future:
                    del callbacks[index]
                    break
            
            # set result
            if future._state == FUTURE_STATE_FINISHED:
                exception = future._exception
                if exception is None:
                    target.set_result(future._result)
                else:
                    target.set_exception(exception)
                return
            
            # if state == FUTURE_STATE_CANCELLED: normally, but the future can be cleared as well.
            target.cancel()
    
    set_docs(__call__,
        """
        Chains the source future's result into the target one.
        
        Parameters
        ----------
        future : ``Future``
            The source future to chain it's result from.
        """
    )

class _ChainRemover:
    """
    Removes the ``_FutureChainer`` callback of the source future if the chained target future is marked as done before.
    
    Parameters
    -------
    target : ``Future``
        The source future.
    """
    __slots__ = ('target',)
    
    def __init__(self, target):
        self.target = target
    
    def __call__(self, future):
        # remove chainer
        callbacks = self.target._callbacks
        for index in range(len(callbacks)):
            callback = callbacks[index]
            if (type(callback) is _FutureChainer) and (callback.target is future):
                del callbacks[index]
                if __debug__:
                    # because this might be the only place, where we retrieve the result, we will just silence it.
                    future.__silence__()
                break


def shield(awaitable, loop):
    """
    Protects the given `awaitable` from being cancelled.
    
    Parameters
    ----------
    awaitable : `awaitable`
        The awaitable object to shield.
    loop : ``EventThread``
        The event loop to run the `awaitable` on.
    
    Returns
    -------
    un_protected : ``Future``
        If the given `awaitable` is a finished task, returns it, else returns a ``Future``, to what the original
        awaitable's result will be chained to.
    
    Raises
    -------
    TypeError
        The given `awaitable` is not `awaitable`.
    """
    protected = loop.ensure_future(awaitable)
    if protected._state != FUTURE_STATE_PENDING:
        return protected # already done, we can return
    
    un_protected = Future(loop)
    protected._callbacks.append(_FutureChainer(un_protected))
    un_protected._callbacks.append(_ChainRemover(protected))
    return un_protected
