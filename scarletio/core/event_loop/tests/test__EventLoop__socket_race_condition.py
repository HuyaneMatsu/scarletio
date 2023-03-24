import socket as module_socket
from http import HTTPStatus
from time import sleep as blocking_sleep

import vampytest

from .http_server import HttpServer

from ...top_level import get_event_loop
from ...traps import skip_ready_cycle

from ....utils import IgnoreCaseMultiValueDictionary


async def _handle_request(request):
    """
    Http request handler.
    
    This function is a coroutine.
    
    Parameters
    ----------
    request : ``RawRequestMessage``
        Received http request.
    
    Returns
    -------
    response : `dict` of `object`
    """
    body = b'hello world'
    
    return {
        'status': HTTPStatus.OK,
        'headers': IgnoreCaseMultiValueDictionary({
            'Content-Length': str(len(body)),
        }),
        'body': body,
    }


async def test__EventThread__socket_receive__racing():
    """
    Tests socket race condition of ``EventThread.socket_receive``.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    http_server = await HttpServer(loop, _handle_request, '127.0.0.1', 6969)
    
    try:
        socket = module_socket.socket()
        
        with socket:
            task = loop.create_task(_test__EventThread__socket_receive__racing(loop, http_server, socket))
            task.apply_timeout(10.0)
            await task
    finally:
        await http_server.close()


async def _test__EventThread__socket_receive__racing(loop, http_server, socket):
    """
    Used by ``test__EventThread__socket_receive__racing``. Wrapped in timeout.
    
    This function is a coroutine.
    
    Parameters
    ----------
    loop : ``EventThread``
        The event loop in context.
    http_server : ``HttpServer``
        Test http server.
    socket : `Socket`
        Writing socket.
    """
    socket.setblocking(False)
    await loop.socket_connect(socket, (http_server.host, http_server.port))
    
    task = loop.create_task(loop.socket_receive(socket, 1024))
    await skip_ready_cycle()
    task.cancel()
    
    loop.create_task(loop.socket_send_all(socket, b'GET / HTTP/1.1\r\n\r\n'))
    data = await loop.socket_receive(socket, 1024)
    
    await loop.socket_receive(socket, 1024)
    
    vampytest.assert_true(data.startswith(b'HTTP/1.1 200 OK'))


async def test__EventThread__socket_receive_into__racing():
    """
    Tests socket race condition of ``EventThread.socket_receive_into``.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    http_server = await HttpServer(loop, _handle_request, '127.0.0.1', 6969)
    
    try:
        socket = module_socket.socket()
        
        with socket:
            task = loop.create_task(_test__EventThread__socket_receive_into__racing(loop, http_server, socket))
            task.apply_timeout(10.0)
            await task
    finally:
        await http_server.close()


async def _test__EventThread__socket_receive_into__racing(loop, http_server, socket):
    """
    Used by ``test__EventThread__socket_receive_into__racing``. Wrapped in timeout.
    
    This function is a coroutine.
    
    Parameters
    ----------
    loop : ``EventThread``
        The event loop in context.
    http_server : ``HttpServer``
        Test http server.
    socket : `Socket`
        Writing socket.
    """
    socket.setblocking(False)
    await loop.socket_connect(socket, (http_server.host, http_server.port))
    
    data = bytearray(1024)
    
    with memoryview(data) as buffer:
        task = loop.create_task(loop.socket_receive_into(socket, buffer[:1024]))
        
        await skip_ready_cycle()
        task.cancel()
        
        task = loop.create_task(loop.socket_send_all(socket, b'GET / HTTP/1.1\r\n\r\n'))
        number_of_bytes = await loop.socket_receive_into(socket, buffer[:1024])
        
        await loop.socket_receive_into(socket, buffer[number_of_bytes:])
        vampytest.assert_true(data.startswith(b'HTTP/1.1 200 OK'))
    
    await task



async def test__EventThread__socket_send_all__racing():
    """
    Tests socket race condition of ``EventThread.socket_send_all``.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    read_socket = module_socket.socket()
    socket = module_socket.socket()
    with read_socket, socket:
        task = loop.create_task(_test__EventThread__socket_send_all__racing(loop, read_socket, socket))
        task.apply_timeout(10.0)
        await task


async def _test__EventThread__socket_send_all__racing(loop, read_socket, write_socket):
    """
    Used by ``test__EventThread__socket_send_all__racing``. Wrapped in timeout.
    
    This function is a coroutine.
    
    Parameters
    ----------
    loop : ``EventThread``
        The event loop in context.
    read_socket : `Socket`
        Reading socket.
    write_socket : `Socket`
        Writing socket.
    """
    read_socket.bind(('127.0.0.1', 0))
    read_socket.listen(1)
    
    write_socket.setblocking(False)
    task = loop.create_task(loop.socket_connect(write_socket, read_socket.getsockname()))
    
    await skip_ready_cycle()
    server = read_socket.accept()[0]
    server.setblocking(False)

    with server:
        await task
        
        with vampytest.assert_raises(BlockingIOError):
            while True:
                write_socket.send(b' ' * 5)
        
        task = loop.create_task(loop.socket_send_all(write_socket, b'hello'))
        
        await skip_ready_cycle()
        task.cancel()
        
        async def receive_until():
            data = b''
            while not data:
                data = await loop.socket_receive(server, 1024)
                data = data.strip()
            return data
        
        task = loop.create_task(receive_until())
        
        await loop.socket_send_all(write_socket, b'world')
        data = await task
        vampytest.assert_true(data.endswith(b'world'))


async def test__EventThread__socket_connect__racing():
    """
    Tests socket race condition of ``EventThread.socket_connect``.
    
    This function is a coroutine.
    """
    loop = get_event_loop()
    
    read_socket = module_socket.socket()
    write_socket = module_socket.socket()
    with read_socket, write_socket:
        task = loop.create_task(_test__EventThread__socket_connect__racing(loop, read_socket, write_socket))
        task.apply_timeout(10.0)
        await task


async def _test__EventThread__socket_connect__racing(loop, read_socket, write_socket):
    """
    Used by ``test__EventThread__socket_connect__racing``. Wrapped in timeout.
    
    This function is a coroutine.
    
    Parameters
    ----------
    loop : ``EventThread``
        The event loop in context.
    read_socket : `Socket`
        Reading socket.
    write_socket : `Socket`
        Writing socket.
    """
    read_socket.bind(('127.0.0.1', 0))
    address = read_socket.getsockname()
    write_socket.setblocking(False)

    task = loop.create_task(loop.socket_connect(write_socket, address))
    
    await skip_ready_cycle()
    task.cancel()

    read_socket.listen(1)
    
    counter = 0
    
    while True:
        try:
            await loop.socket_connect(write_socket, address)
        except ConnectionRefusedError:
            # Linux
            await loop.socket_connect(write_socket, address)
            break
        
        except OSError as err:
            # windows checks
            if getattr(err, 'winerror', 0) == 10056:
                break
            
            if getattr(err, 'winerror', 0) != 10022:
                raise
            
            counter += 1
            if counter >= 128:
                raise
            
            blocking_sleep(0.01)
        
        else:
            break
