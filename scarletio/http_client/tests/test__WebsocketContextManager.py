from types import CoroutineType, GeneratorType

import vampytest

from ...core import Task, get_event_loop
from ...web_socket import WebSocketClient, WebSocketCommonProtocol

from ..web_socket_context_manager import WebSocketContextManager


def _assert_fields_set(web_socket_context_manager):
    """
    Asserts whether every fields are set of the given ``WebSocketContextManager``.
    
    Parameters
    ----------
    web_socket_context_manager : ``WebSocketContextManager``
        Thee instance to test.
    """
    vampytest.assert_instance(web_socket_context_manager, WebSocketContextManager)
    vampytest.assert_instance(web_socket_context_manager.coroutine, CoroutineType, GeneratorType, nullable = True)
    vampytest.assert_instance(web_socket_context_manager.web_socket, WebSocketClient, nullable = True)


async def web_socket_coroutine():
    """
    Does a dummy web socket, actually is not doing anything and returns a response.
    
    Returns
    -------
    web_socket : ``ClientResponse``
    """
    loop = get_event_loop()
    return WebSocketCommonProtocol.__new__(WebSocketClient, loop, '1.1.1.1', 96)


async def enter_and_exit(web_socket_context_manager):
    """
    Enters an exits the given web socket context manager.
    
    Parameters
    ----------
    web_socket_context_manager : ``WebSocketContextManager``
        The web socket context manager to enter and exit.
    
    Returns
    -------
    response : ``ClientResponse``
    """
    response = await web_socket_context_manager.__aenter__()
    await web_socket_context_manager.__aexit__(None, None, None)
    return response


async def test__WebSocketContextManager__new():
    """
    Tests whether ``WebSocketContextManager.__new__`` works as intended.
    
    This function is a coroutine.
    """
    coroutine = web_socket_coroutine()
    
    try:
        web_socket_context_manager = WebSocketContextManager(coroutine)
        
        _assert_fields_set(web_socket_context_manager)
        vampytest.assert_is(web_socket_context_manager.coroutine, coroutine)
        vampytest.assert_is(web_socket_context_manager.web_socket, None)
    
    finally:
        coroutine.close()


async def test__WebSocketContextManager__await():
    """
    Tests whether ``WebSocketContextManager.__await__`` works as intended.
    
    This function is a coroutine.
    """
    coroutine = web_socket_coroutine()
    
    try:
        web_socket_context_manager = WebSocketContextManager(coroutine)
        
        task = Task(get_event_loop(), web_socket_context_manager.__await__())
        task.apply_timeout(0.1)
        await task
        
        _assert_fields_set(web_socket_context_manager)
        vampytest.assert_is(web_socket_context_manager.coroutine, None)
        vampytest.assert_is_not(web_socket_context_manager.web_socket, None)
    
    finally:
        coroutine.close()


async def test__WebSocketContextManager__aenter():
    """
    Tests whether ``WebSocketContextManager.__aenter__`` works as intended.
    
    This function is a coroutine.
    """
    coroutine = web_socket_coroutine()
    
    try:
        web_socket_context_manager = WebSocketContextManager(coroutine)
        
        task = Task(get_event_loop(), web_socket_context_manager.__aenter__())
        task.apply_timeout(0.1)
        response = await task
        
        _assert_fields_set(web_socket_context_manager)
        vampytest.assert_is(web_socket_context_manager.coroutine, None)
        vampytest.assert_is(web_socket_context_manager.web_socket, response)
        
        vampytest.assert_is_not(response, None)
    
    finally:
        coroutine.close()
    

async def test__WebSocketContextManager__aexit():
    """
    Tests whether ``WebSocketContextManager.__aenter__`` works as intended.
    
    This function is a coroutine.
    """
    coroutine = web_socket_coroutine()
    
    try:
        web_socket_context_manager = WebSocketContextManager(coroutine)
        
        task = Task(get_event_loop(), enter_and_exit(web_socket_context_manager))
        task.apply_timeout(0.1)
        response = await task
        
        _assert_fields_set(web_socket_context_manager)
        vampytest.assert_is(web_socket_context_manager.coroutine, None)
        vampytest.assert_is(web_socket_context_manager.web_socket, None)
        
        vampytest.assert_true(response.closed)
    
    finally:
        coroutine.close()
    

async def test__WebSocketContextManager__repr__created():
    """
    Tests whether ``WebSocketContextManager.__repr__`` works as intended.
    
    Case: Created.
    
    This function is a coroutine.
    """
    coroutine = web_socket_coroutine()
    
    try:
        web_socket_context_manager = WebSocketContextManager(coroutine)
        
        output = repr(web_socket_context_manager)
        vampytest.assert_instance(output, str)
    
    finally:
        coroutine.close()


async def test__WebSocketContextManager__repr__entered():
    """
    Tests whether ``WebSocketContextManager.__repr__`` works as intended.
    
    Case: entered.
    
    This function is a coroutine.
    """
    coroutine = web_socket_coroutine()
    
    try:
        web_socket_context_manager = WebSocketContextManager(coroutine)
        
        task = Task(get_event_loop(), web_socket_context_manager.__aenter__())
        task.apply_timeout(0.1)
        await task
        
        output = repr(web_socket_context_manager)
        vampytest.assert_instance(output, str)
    
    finally:
        coroutine.close()


async def test__WebSocketContextManager__repr__exited():
    """
    Tests whether ``WebSocketContextManager.__repr__`` works as intended.
    
    Case: exited.
    
    This function is a coroutine.
    """
    coroutine = web_socket_coroutine()
    
    try:
        web_socket_context_manager = WebSocketContextManager(coroutine)
        
        task = Task(get_event_loop(), enter_and_exit(web_socket_context_manager))
        task.apply_timeout(0.1)
        await task
        
        output = repr(web_socket_context_manager)
        vampytest.assert_instance(output, str)
    
    finally:
        coroutine.close()
