from types import CoroutineType, GeneratorType

import vampytest

from ...core import Task, get_event_loop
from ...utils import IgnoreCaseMultiValueDictionary
from ...web_common import HttpReadWriteProtocol, URL
from ...web_common.headers import METHOD_GET

from ..client_request import ClientRequest
from ..client_response import ClientResponse
from ..connection import Connection
from ..connector_base import ConnectorBase
from ..request_context_manager import RequestContextManager


def _assert_fields_set(request_context_manager):
    """
    Asserts whether every fields are set of the given ``RequestContextManager``.
    
    Parameters
    ----------
    request_context_manager : ``RequestContextManager``
        Thee instance to test.
    """
    vampytest.assert_instance(request_context_manager, RequestContextManager)
    vampytest.assert_instance(request_context_manager.coroutine, CoroutineType, GeneratorType, nullable = True)
    vampytest.assert_instance(request_context_manager.response, ClientResponse, nullable = True)


async def request_coroutine():
    """
    Does a dummy request, actually is not doing anything and returns a response.
    
    Returns
    -------
    response : ``ClientResponse``
    """
    loop = get_event_loop()
    
    request = ClientRequest(
        loop,
        METHOD_GET,
        URL('https://orindance.party/'),
        IgnoreCaseMultiValueDictionary(),
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
    )
    
    connector = ConnectorBase(loop)
    connection = Connection(connector, request.connection_key, HttpReadWriteProtocol(loop), 2)
    
    # If we do not call `request.begin` we do not send anything. Teehee
    return ClientResponse(request, connection)


async def enter_and_exit(request_context_manager):
    """
    Enters an exits the given request context manager.
    
    Parameters
    ----------
    request_context_manager : ``RequestContextManager``
        The request context manager to enter and exit.
    
    Returns
    -------
    response : ``ClientResponse``
    """
    response = await request_context_manager.__aenter__()
    await request_context_manager.__aexit__(None, None, None)
    return response


async def test__RequestContextManager__new():
    """
    Tests whether ``RequestContextManager.__new__`` works as intended.
    
    This function is a coroutine.
    """
    coroutine = request_coroutine()
    
    try:
        request_context_manager = RequestContextManager(coroutine)
        
        _assert_fields_set(request_context_manager)
        vampytest.assert_is(request_context_manager.coroutine, coroutine)
        vampytest.assert_is(request_context_manager.response, None)
    
    finally:
        coroutine.close()


async def test__RequestContextManager__await():
    """
    Tests whether ``RequestContextManager.__await__`` works as intended.
    
    This function is a coroutine.
    """
    coroutine = request_coroutine()
    
    try:
        request_context_manager = RequestContextManager(coroutine)
        
        task = Task(get_event_loop(), request_context_manager.__await__())
        task.apply_timeout(0.1)
        await task
        
        _assert_fields_set(request_context_manager)
        vampytest.assert_is(request_context_manager.coroutine, None)
        vampytest.assert_is_not(request_context_manager.response, None)
    
    finally:
        coroutine.close()


async def test__RequestContextManager__aenter():
    """
    Tests whether ``RequestContextManager.__aenter__`` works as intended.
    
    This function is a coroutine.
    """
    coroutine = request_coroutine()
    
    try:
        request_context_manager = RequestContextManager(coroutine)
        
        task = Task(get_event_loop(), request_context_manager.__aenter__())
        task.apply_timeout(0.1)
        response = await task
        
        _assert_fields_set(request_context_manager)
        vampytest.assert_is(request_context_manager.coroutine, None)
        vampytest.assert_is(request_context_manager.response, response)
        
        vampytest.assert_is_not(response, None)
    
    finally:
        coroutine.close()
    

async def test__RequestContextManager__aexit():
    """
    Tests whether ``RequestContextManager.__aenter__`` works as intended.
    
    This function is a coroutine.
    """
    coroutine = request_coroutine()
    
    try:
        request_context_manager = RequestContextManager(coroutine)
        
        task = Task(get_event_loop(), enter_and_exit(request_context_manager))
        task.apply_timeout(0.1)
        response = await task
        
        _assert_fields_set(request_context_manager)
        vampytest.assert_is(request_context_manager.coroutine, None)
        vampytest.assert_is(request_context_manager.response, None)
        
        vampytest.assert_true(response.closed)
    
    finally:
        coroutine.close()
    

async def test__RequestContextManager__repr__created():
    """
    Tests whether ``RequestContextManager.__repr__`` works as intended.
    
    Case: Created.
    
    This function is a coroutine.
    """
    coroutine = request_coroutine()
    
    try:
        request_context_manager = RequestContextManager(coroutine)
        
        output = repr(request_context_manager)
        vampytest.assert_instance(output, str)
    
    finally:
        coroutine.close()


async def test__RequestContextManager__repr__entered():
    """
    Tests whether ``RequestContextManager.__repr__`` works as intended.
    
    Case: entered.
    
    This function is a coroutine.
    """
    coroutine = request_coroutine()
    
    try:
        request_context_manager = RequestContextManager(coroutine)
        
        task = Task(get_event_loop(), request_context_manager.__aenter__())
        task.apply_timeout(0.1)
        await task
        
        output = repr(request_context_manager)
        vampytest.assert_instance(output, str)
    
    finally:
        coroutine.close()


async def test__RequestContextManager__repr__exited():
    """
    Tests whether ``RequestContextManager.__repr__`` works as intended.
    
    Case: exited.
    
    This function is a coroutine.
    """
    coroutine = request_coroutine()
    
    try:
        request_context_manager = RequestContextManager(coroutine)
        
        task = Task(get_event_loop(), enter_and_exit(request_context_manager))
        task.apply_timeout(0.1)
        await task
        
        output = repr(request_context_manager)
        vampytest.assert_instance(output, str)
    
    finally:
        coroutine.close()
