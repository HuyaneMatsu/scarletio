from ...core import TransportLayerBase

from contextlib import contextmanager as to_context_manager


RESPONSE_DATAS = None
REQUEST_DATAS = None
NEW_TRANSPORT = False


def set_response_datas(response_data):
    global RESPONSE_DATAS
    RESPONSE_DATAS = response_data


def get_response_data():
    global RESPONSE_DATAS
    if RESPONSE_DATAS is None:
        raise RuntimeError()
    
    do_return, value = RESPONSE_DATAS.pop(0)
    if not RESPONSE_DATAS:
        RESPONSE_DATAS = None
    
    if do_return:
        return value
    
    raise value


def clear_request_data():
    global REQUEST_DATAS
    global NEW_TRANSPORT
    REQUEST_DATAS = None
    NEW_TRANSPORT = True


def add_request_data(request_data):
    global REQUEST_DATAS
    global NEW_TRANSPORT
    
    if REQUEST_DATAS is None:
        REQUEST_DATAS = []
        NEW_TRANSPORT = True
    
    if NEW_TRANSPORT:
        NEW_TRANSPORT = False
        REQUEST_DATAS.append(b'')
    
    REQUEST_DATAS[-1] += request_data


def get_request_datas():
    return REQUEST_DATAS


def set_new_transport():
    global NEW_TRANSPORT
    NEW_TRANSPORT = True


class TestingTransportLayerBase(TransportLayerBase):
    __slots__ = ('_loop', '_protocol')
    
    def __new__(cls, loop, protocol):
        self = object.__new__(cls)
        self._loop = loop
        self._protocol = protocol
        return self
    
    def get_protocol(self):
        return self._protocol
    
    def set_protocol(self, protocol):
        self._protocol = protocol
    
    def write(self, data):
        add_request_data(data)
    
    def send_to(self, data):
        add_request_data(data)


async def create_datagram_connection_to(
    self,
    protocol_factory,
    local_address,
    remote_address,
    *,
    socket_family = 0,
    socket_protocol = 0,
    socket_flags = 0,
    reuse_port = False,
    allow_broadcast = False,
):
    response_data = get_response_data()
    set_new_transport()
    protocol = protocol_factory()
    transport = TestingTransportLayerBase(self, protocol)
    protocol.connection_made(transport)
    protocol.datagram_received(response_data, remote_address)
    protocol.eof_received()
    return protocol


async def create_connection_to(
    self,
    protocol_factory,
    host_name,
    port,
    *,
    local_address = None,
    server_host_name = None,
    socket_family = 0,
    socket_flags = 0,
    socket_protocol = 0,
    ssl_context = None,
):
    response_data = get_response_data()
    set_new_transport()
    protocol = protocol_factory()
    transport = TestingTransportLayerBase(self, protocol)
    protocol.connection_made(transport)
    protocol.data_received(response_data)
    protocol.eof_received()
    return protocol


@to_context_manager
def patch_event_loop(event_loop):
    original_create_datagram_connection_to = type(event_loop).create_datagram_connection_to
    original_create_connection_to = type(event_loop).create_connection_to
    
    try:
        type(event_loop).create_datagram_connection_to = create_datagram_connection_to
        type(event_loop).create_connection_to = create_connection_to
        
        yield
    
    finally:
        type(event_loop).create_datagram_connection_to = original_create_datagram_connection_to
        type(event_loop).create_connection_to = original_create_connection_to
