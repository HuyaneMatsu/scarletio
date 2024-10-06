__all__ = ()

from functools import partial as partial_func

from ...traps import Task, TaskGroup, skip_poll_cycle

from ....web_common import HttpReadWriteProtocol


class HttpServer:
    __slots__ = ('loop', 'handler', 'protocols', 'close_connection_task', 'server', 'port', 'host')
    
    async def __new__(cls, loop, handler, host, port, *, ssl = None):
        self = object.__new__(cls)
        self.loop = loop
        self.handler = handler
        self.protocols = set()
        self.close_connection_task = None
        self.server = None
        self.host = host
        self.port = port

        factory = partial_func(HttpServerProtocol, loop, self)
        server = await loop.create_server_to(factory, host, port, ssl = ssl)
        
        self.server = server
        await server.start()
        return self
    
    
    def register(self, protocol):
        self.protocols.add(protocol)
    
    
    def unregister(self, protocol):
        self.protocols.discard(protocol)
    
    
    def close(self):
        close_connection_task = self.close_connection_task
        if close_connection_task is None:
            close_connection_task = Task(self.loop, self._close())
            self.close_connection_task = close_connection_task
        
        return close_connection_task
    
    
    async def _close(self):
        server = self.server
        if server is None:
            return
        
        server.close()
        await server.wait_closed()
        
        loop = self.loop
        
        # Skip 1 full loop
        await skip_poll_cycle(loop)
        
        await TaskGroup(loop, (loop.create_task(protocol.close()) for protocol in self.protocols)).wait_all()
        self.server = None


class HttpServerProtocol(HttpReadWriteProtocol):
    __slots__ = ('handler_task', 'server',)
    
    def __new__(cls, loop, server):
        self = HttpReadWriteProtocol.__new__(cls, loop)
        self.handler_task = None
        self.server = server
        return self
    
    
    def connection_made(self, transport):
        HttpReadWriteProtocol.connection_made(self, transport)
        self.server.register(self)
        self.handler_task = Task(self._loop, self.lifetime_handler())
    
    
    async def lifetime_handler(self):
        try:
            request = await self.read_http_request()
            
            response = await self.server.handler(request)
            self.write_http_response(**response)
            await self.drain()
            HttpReadWriteProtocol.close(self)
        
        except:
            transport = self._transport
            if transport is not None:
                transport.close()
                transport.abort()
            raise
        
        finally:
            self.handler_task = None
            self.server.unregister(self)
    
    
    async def close(self):
        HttpReadWriteProtocol.close(self)
        
        handler_task = self.handler_task
        if (handler_task is not None):
            handler_task.cancel()
