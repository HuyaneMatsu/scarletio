from .async_executing import *
from .event import *
from .future import *
from .future_chaining import *
from .future_states import *
from .future_wrapper_async import *
from .future_wrapper_base import *
from .future_wrapper_sync import *
from .handle_cancellers import *
from .locks import *
from .queues import *
from .task import *
from .task_group import *
from .task_suppression import *
from .task_thread_switcher import *
from .timeouting import *


__all__ = (
    'FutureSyncWrapper',
    'FutureAsyncWrapper',
    *async_executing.__all__,
    *event.__all__,
    *future.__all__,
    *future_chaining.__all__,
    *future_states.__all__,
    *future_wrapper_async.__all__,
    *future_wrapper_base.__all__,
    *future_wrapper_sync.__all__,
    *handle_cancellers.__all__,
    *locks.__all__,
    *queues.__all__,
    *task.__all__,
    *task_group.__all__,
    *task_suppression.__all__,
    *task_thread_switcher.__all__,
    *timeouting.__all__,
)

# Deprecations

from warnings import warn


class FutureSyncWrapper(FutureWrapperSync):
    """
    Deprecated and will be removed in 2024 february. Please use ``FutureWrapperSync`` instead.
    """
    __slots__ = ()
        
    def __new__(cls, future, loop):
        warn(
            (
                f'`{cls.__name__}` is deprecated and will be removed in 2024. '
                f'Please use {FutureWrapperSync.__name__} instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return FutureWrapperSync.__new__(cls, future, loop)


class FutureAsyncWrapper(FutureWrapperAsync):
    """
    Deprecated and will be removed in 2024 february. Please use ``FutureWrapperAsync`` instead.
    """
    __slots__ = ()
    
    def __new__(cls, future, loop):
        warn(
            (
                f'`{cls.__name__}` is deprecated and will be removed in 2024. '
                f'Please use {FutureWrapperAsync.__name__} instead.'
            ),
            FutureWarning,
            stacklevel = 2,
        )
        return FutureWrapperAsync.__new__(cls, future, loop)
