__all__ = ('get_address_info_async', 'get_name_info_async')

from errno import ECONNREFUSED as ERROR_CODE_CONNECTION_REFUSED
from functools import partial as partial_func
from itertools import count
from socket import (
    AF_INET as SOCKET_FAMILY_IP_V4, AF_INET6 as SOCKET_FAMILY_IP_V6, AF_UNSPEC as SOCKET_FAMILY_UNSPECIFIED,
    AI_ADDRCONFIG as ADDRESS_INFO_ADDRESS_CONFIGURATION, AI_CANONNAME as ADDRESS_INFO_CANONICAL_NAME,
    AI_NUMERICHOST as ADDRESS_INFO_NUMERIC_HOST, AI_V4MAPPED as ADDRESS_INFO_IP_V4_MAPPED,
    EAI_FAIL as ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE, EAI_FAMILY as ERROR_CODE_ADDRESS_INFO_FAMILY,
    EAI_NONAME as ERROR_CODE_ADDRESS_INFO_NO_NAME, EAI_SERVICE as ERROR_CODE_ADDRESS_INFO_SERVICE,
    EAI_SOCKTYPE as ERROR_CODE_ADDRESS_INFO_SOCKET_TYPE, NI_DGRAM as NAME_INFO_DATAGRAM,
    NI_NAMEREQD as NAME_INFO_RAISE_ERROR_IF_NAME_CANNOT_BE_DETERMINED, NI_NUMERICHOST as NAME_INFO_NUMERIC_HOST,
    NI_NUMERICSERV as NAME_INFO_NUMERIC_SERVICE, SOCK_DGRAM as SOCKET_TYPE_DATAGRAM, SOCK_RAW as SOCKET_TYPE_RAW,
    SOCK_STREAM as SOCKET_TYPE_STREAM, SOL_IP as SOCKET_OPTION_LEVEL_IP, SOL_TCP as SOCKET_OPTION_LEVEL_TCP,
    SOL_UDP as SOCKET_OPTION_LEVEL_UDP, gaierror as GetAddressInfoError, getservbyname as get_protocol_for_service_name,
    getservbyport as get_service_by_protocol, if_nametoindex as get_network_interface_index
)
from ssl import create_default_context as create_default_ssl_context

from ..core import DatagramAddressedReadProtocol, ReadProtocolBase, ReadWriteProtocolBase, Task
from ..utils import export

from .building_and_parsing import (
    build_query_data, parse_domain_name_pointer_data, parse_ip_v4_data, parse_ip_v6_data, parse_result_data
)
from .constants import (
    CLASS_CODE_INTERNET, IP_TYPE_IP_V4, IP_TYPE_IP_V6, NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO,
    NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES, QUERY_TRANSPORT_TYPE_AUTO, QUERY_TRANSPORT_TYPE_TCP,
    QUERY_TRANSPORT_TYPE_TLS, QUERY_TRANSPORT_TYPE_UDP, RESOURCE_RECORD_TYPE_DOMAIN_NAME_POINTER,
    RESOURCE_RECORD_TYPE_IP_V4_ADDRESS, RESOURCE_RECORD_TYPE_IP_V6_ADDRESS
)
from .helpers import (
    build_name_from_labels, iter_intermediate_intermediate_addresses_ordered, iter_labels_with_searches,
    parse_ip_v4_string, parse_ip_v6_string, parse_labels_from_name, parse_reversed_labels_from_address,
    produce_ip_string, produce_ip_v4_string, produce_ip_v6_string
)
from .query import Query
from .question import Question
from .resolve_configuration import RESOLVE_CONFIGURATION_DEFAULT


COUNTER = iter(count(0))


# Separately defined, so it is patchable while testing.
def _get_next_id():
    """
    Returns a new transaction identifier.
    
    Returns
    -------
    transaction_id : `int`
    """
    return (next(COUNTER) & 0xffff)


async def async_iter_execute_query_async(event_loop, query, resolve_configuration, ssl_context):
    """
    Iterates over query execution results.
    
    This function is an iterable coroutine generator.
    
    Parameters
    ----------
    event_loop : ``EventThread``
        The event loop to use.
    
    query : ``Query``
        The query to execute.
    
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration to query as.
    
    ssl_context : ``None | SSLContext`
        SSL context to use when using secure connection.
    
    Yields
    ------
    result : ``Result``
    
    Raises
    ------
    OsError
    GetAddressInfoError
    """
    name_server_configurations = resolve_configuration.name_server_configurations
    if (name_server_configurations is None):
        name_server_configurations = resolve_configuration.name_server_configurations_fallback
        if (name_server_configurations is None):
            raise GetAddressInfoError(
                ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
                'No name server to query from.',
            )
    
    transaction_id = query.transaction_id
    if not resolve_configuration.option_rotate:
        transaction_id = 0
    
    # Please don't do this.
    questions = query.questions
    if questions is None:
        return
    
    name_server_skipped_due_to_secure_connection_not_being_available = 0
    preference_query_transport_type = resolve_configuration.preference_query_transport_type
    
    # Limit retry count to the length of name server configurations.
    # It makes no sense to try the same name server twice.
    for index in range(
        transaction_id,
        transaction_id + min(resolve_configuration.option_attempts, len(name_server_configurations))
    ):
        name_server_configuration = name_server_configurations[index % len(name_server_configurations)]
        supports_multiple_questions_in_queries = name_server_configuration.supports_multiple_questions_in_queries
        secure_connection_support_level = name_server_configuration.secure_connection_support_level
        
        # Select the preferred executor for the specified name server
        if preference_query_transport_type == QUERY_TRANSPORT_TYPE_AUTO:
            if secure_connection_support_level == NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO:
                query_executor = _execute_query_tcp
            
            elif secure_connection_support_level == NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_YES:
                query_executor = _execute_query_tls
            
            else:
                query_executor = _execute_query_tls_with_tcp_fallback
        
        elif preference_query_transport_type == QUERY_TRANSPORT_TYPE_UDP:
            query_executor = _execute_query_udp
        
        elif preference_query_transport_type == QUERY_TRANSPORT_TYPE_TCP:
            query_executor = _execute_query_tcp
        
        elif preference_query_transport_type == QUERY_TRANSPORT_TYPE_TLS:
            if secure_connection_support_level == NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO:
                name_server_skipped_due_to_secure_connection_not_being_available += len(questions)
                continue
            
            # If it defines maybe, we still enforce tls, and check the response at that time.
            query_executor = _execute_query_tls
            
        else:
            raise GetAddressInfoError(
                ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
                f'No defined query behaviour for preference_query_transport_type = {preference_query_transport_type!r}.',
            )
        
        if supports_multiple_questions_in_queries or (len(questions) == 1):
            task = Task(
                event_loop,
                query_executor(event_loop, name_server_configuration, query, resolve_configuration, ssl_context),
            )
            task.apply_timeout(resolve_configuration.option_timeout)
            try:
                result = await task
            except TimeoutError:
                continue
            
            except OSError as exception:
                # If we force secure request and we failed to make the connection, increment skipped count.
                if (
                    (preference_query_transport_type != QUERY_TRANSPORT_TYPE_TLS) or
                    (exception.errno != ERROR_CODE_CONNECTION_REFUSED)
                ):
                    raise
                
                name_server_skipped_due_to_secure_connection_not_being_available += len(questions)
                continue
            
            if (result is None):
                continue
            
            yield result
            return
        
        any_query_passed = False
        for question in questions:
            task = Task(
                event_loop,
                query_executor(
                    event_loop,
                    name_server_configuration,
                    Query(
                        _get_next_id(),
                        query.recursion_desired,
                        query.data_verification_desired,
                        (question,),
                        query.additional_resource_records,
                    ),
                    resolve_configuration,
                    ssl_context,
                ),
            )
            task.apply_timeout(resolve_configuration.option_timeout)
            try:
                result = await task
            except TimeoutError:
                continue
            
            except OSError as exception:
                # If we force secure request and we failed to make the connection, increment skipped count.
                if (
                    (preference_query_transport_type != QUERY_TRANSPORT_TYPE_TLS) or
                    (exception.errno != ERROR_CODE_CONNECTION_REFUSED)
                ):
                    raise
                
                name_server_skipped_due_to_secure_connection_not_being_available += 1
                continue
            
            if (result is None):
                continue
                
            any_query_passed = True
            yield result
            continue
        
        if any_query_passed:
            return
        
        continue
    
    if (
        name_server_skipped_due_to_secure_connection_not_being_available ==
        (len(name_server_configurations) * len(questions))
    ):
        error_message = (
            'Permanent failure in name resolution; '
            'Transport type TLS has been specified, but non of the name servers support it.'
        )
    else:
        error_message = 'Temporary failure in name resolution.'
    
    raise GetAddressInfoError(
        ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
        error_message,
    )


async def _execute_query_udp(event_loop, name_server_configuration, query, resolve_configuration, ssl_context):
    """
    Executes a query through User Datagram Protocol.
    
    This function is a coroutine.
    
    Parameters
    ----------
    event_loop : ``EventLoop``
        Event loop to use.
    
    name_server_configuration : ``NameServerConfiguration``
        Name server configuration describing the connection.
    
    query : ``Query``
        Query to execute.
    
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration to query as.
    
    ssl_context : ``None | SSLContext`
        SSL context to use when using secure connection.
    
    Returns
    -------
    result : ``None | Result``
    
    Raises
    ------
    OsError
    GetAddressInfoError
    """
    protocol = None
    try:
        address = (
            ''.join([*produce_ip_string(name_server_configuration.ip_type, name_server_configuration.ip_value)]),
            53,
        )
        protocol = await event_loop.create_datagram_connection_to(
            partial_func(DatagramAddressedReadProtocol, event_loop, partial_func(ReadProtocolBase, event_loop)),
            None,
            address,
            socket_flags = ADDRESS_INFO_NUMERIC_HOST,
        )
        data = build_query_data(query, resolve_configuration)
        protocol._transport.send_to(data)
        await protocol.drain()
        secondary_protocol = await protocol.wait_for_receive(address, resolve_configuration.option_timeout)
        if (secondary_protocol is None):
            return
        
        data = await secondary_protocol.read_once()
        
        result, response_parsing_error = parse_result_data(data)
        if resolve_configuration.preference_raise_upon_response_parsing_error and (response_parsing_error is not None):
            try:
                raise response_parsing_error
            finally:
                response_parsing_error = None
        
        return result
    
    finally:
        if (protocol is not None):
            protocol.close()


async def _execute_query_tcp(event_loop, name_server_configuration, query, resolve_configuration, ssl_context):
    """
    Executes a query through Transmission Control Protocol.
    
    This function is a coroutine.
    
    Parameters
    ----------
    event_loop : ``EventLoop``
        Event loop to use.
    
    name_server_configuration : ``NameServerConfiguration``
        Name server configuration describing the connection.
    
    query : ``Query``
        Query to execute.
    
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration to query as.
    
    ssl_context : ``None | SSLContext`
        SSL context to use when using secure connection.
    
    Returns
    -------
    result : ``None | Result``
    
    Raises
    ------
    OsError
    GetAddressInfoError
    """
    protocol = None
    try:
        protocol = await event_loop.create_connection_to(
            partial_func(ReadWriteProtocolBase, event_loop),
            ''.join([*produce_ip_string(name_server_configuration.ip_type, name_server_configuration.ip_value)]),
            53,
            socket_flags = ADDRESS_INFO_NUMERIC_HOST,
        )
        
        query_data = build_query_data(query, resolve_configuration)
        protocol.write(len(query_data).to_bytes(2, 'big'))
        protocol.write(query_data)
        query_data = None
        await protocol.drain()
        
        data_length_raw = await protocol.read(2)
        data_length = int.from_bytes(data_length_raw, 'big')
        data = await protocol.read(data_length)
        
        result, response_parsing_error = parse_result_data(data)
        if resolve_configuration.preference_raise_upon_response_parsing_error and (response_parsing_error is not None):
            try:
                raise response_parsing_error
            finally:
                response_parsing_error = None
        
        return result
    
    finally:
        if (protocol is not None):
            protocol.close()


async def _execute_query_tls(event_loop, name_server_configuration, query, resolve_configuration, ssl_context):
    """
    Executes a query through Transport Layer Security over Transmission Control Protocol.
    
    This function is a coroutine.
    
    Parameters
    ----------
    event_loop : ``EventLoop``
        Event loop to use.
    
    name_server_configuration : ``NameServerConfiguration``
        Name server configuration describing the connection.
    
    query : ``Query``
        Query to execute.
    
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration to query as.
    
    ssl_context : ``None | SSLContext`
        SSL context to use when using secure connection.
    
    Returns
    -------
    result : ``None | Result``
    
    Raises
    ------
    OsError
    GetAddressInfoError
    """
    protocol = None
    try:
        if ssl_context is None:
            ssl_context = create_default_ssl_context()
        
        protocol = await event_loop.create_connection_to(
            partial_func(ReadWriteProtocolBase, event_loop),
            ''.join([*produce_ip_string(name_server_configuration.ip_type, name_server_configuration.ip_value)]),
            853,
            socket_flags = ADDRESS_INFO_NUMERIC_HOST,
            ssl_context = ssl_context,
        )
        
        query_data = build_query_data(query, resolve_configuration)
        protocol.write(len(query_data).to_bytes(2, 'big'))
        protocol.write(query_data)
        query_data = None
        await protocol.drain()
        
        data_length_raw = await protocol.read(2)
        data_length = int.from_bytes(data_length_raw, 'big')
        data = await protocol.read(data_length)
        result, response_parsing_error = parse_result_data(data)
        if resolve_configuration.preference_raise_upon_response_parsing_error and (response_parsing_error is not None):
            try:
                raise response_parsing_error
            finally:
                response_parsing_error = None
        
        return result
    
    finally:
        if (protocol is not None):
            protocol.close()


async def _execute_query_tls_with_tcp_fallback(
    event_loop, name_server_configuration, query, resolve_configuration, ssl_context
):
    """
    Executes a query first through Transport Layer Security over Transmission Control Protocol and if it fails due to
    not being supported, executes it through just Transmission Control Protocol.
    
    This function is a coroutine.
    
    Parameters
    ----------
    event_loop : ``EventLoop``
        Event loop to use.
    
    name_server_configuration : ``NameServerConfiguration``
        Name server configuration describing the connection.
    
    query : ``Query``
        Query to execute.
    
    resolve_configuration : ``ResolveConfiguration``
        Resolve configuration to query as.
    
    ssl_context : ``None | SSLContext`
        SSL context to use when using secure connection.
    
    Returns
    -------
    result : ``None | Result``
    
    Raises
    ------
    OsError
    GetAddressInfoError
    """
    try:
        return await _execute_query_tls(
            event_loop, name_server_configuration, query, resolve_configuration, ssl_context
        )
    except OSError as exception:
        if exception.errno != ERROR_CODE_CONNECTION_REFUSED:
            raise
        
        name_server_configuration.secure_connection_support_level = (
            NAME_SERVER_CONFIGURATION_SECURE_CONNECTION_SUPPORT_LEVEL_NO
        )
    
    return await _execute_query_tcp(event_loop, name_server_configuration, query, resolve_configuration, ssl_context)


@export
async def get_address_info_async(
    event_loop,
    host_name,
    port,
    socket_family = SOCKET_FAMILY_UNSPECIFIED,
    socket_type = 0,
    socket_protocol = 0,
    socket_flags = 0,
    *,
    resolve_configuration = None,
    ssl_context = None,
):
    """
    Gets address info for the given host name.
    
    This function is a coroutine.
    
    Parameters
    ----------
    event_loop : ``EventThread``
        Event loop to use.
    
    host_name : `None | str`
        Host name to query for.
    
    port : `None | int | str`
        Port to query for.
    
    socket_family : `int` = `SOCKET_FAMILY_UNSPECIFIED`, Optional
        Socket family to query for.
    
    socket_type : `int` = `0`, Optional
        Socket type to query for.
    
    socket_protocol : `int` = `0`, Optional
        Socket protocol to query for.
    
    socket_flags : `int` = `0`, Optional
        Socket flags to query as.
    
    resolve_configuration : ``None | ResolveConfiguration``, Optional (Keyword only)
        Resolve configuration to query as.
    
    ssl_context : ``None | SSLContext`, Optional (Keyword only)
        SSL context to use when using secure connection.
    
    Returns
    -------
    output : `list<(int, int, int, str, (str, int) | (str, int, int, int))>`
    
    Raises
    ------
    OsError
    GetAddressInfoError
    """
    # Set configuration if required.
    if resolve_configuration is None:
        resolve_configuration = RESOLVE_CONFIGURATION_DEFAULT
    
    # Validate host_name & port combo.
    if (host_name is None) and (port is None):
        raise GetAddressInfoError(
            ERROR_CODE_ADDRESS_INFO_NO_NAME,
            'Name and service not known.',
        )
    
    # Validate port
    if port is None:
        port = 0
    elif isinstance(port, int):
        pass
    elif isinstance(port, str):
        port = get_protocol_for_service_name(port)
    else:
        raise GetAddressInfoError(
            ERROR_CODE_ADDRESS_INFO_SERVICE,
            f'Port can be either `None`, `int` or `str`, got type(port) = {type(port).__name__}; port = {port!r}.',
        )
    
    # Validate family
    if socket_family == SOCKET_FAMILY_UNSPECIFIED:
        if resolve_configuration.option_no_ip_v6_lookups:
            socket_families = (SOCKET_FAMILY_IP_V4,)
        else:
            # Python's own returns ip v6 addresses before ip v4. To replicate this, we set to execute the up v6 first.
            socket_families = (SOCKET_FAMILY_IP_V6, SOCKET_FAMILY_IP_V4)
    elif (socket_family == SOCKET_FAMILY_IP_V4) or (socket_family == SOCKET_FAMILY_IP_V6):
        socket_families = (socket_family,)
    else:
        raise GetAddressInfoError(
            ERROR_CODE_ADDRESS_INFO_FAMILY,
            f'Socket family not supported; socket_family = {socket_family!r}.',
        )
    
    # Validate socket type
    if socket_type == 0:
        if port:
            socket_types = (SOCKET_TYPE_DATAGRAM, SOCKET_TYPE_STREAM)
            socket_protocols = (SOCKET_OPTION_LEVEL_UDP, SOCKET_OPTION_LEVEL_TCP)
        else:
            socket_types = (SOCKET_TYPE_DATAGRAM, SOCKET_TYPE_STREAM, SOCKET_TYPE_RAW)
            socket_protocols = (SOCKET_OPTION_LEVEL_UDP, SOCKET_OPTION_LEVEL_TCP, SOCKET_OPTION_LEVEL_IP)
    
    elif (socket_type == SOCKET_TYPE_DATAGRAM) or (socket_type == SOCKET_TYPE_STREAM):
        socket_types = (socket_type,)
        if socket_type == SOCKET_TYPE_DATAGRAM:
            socket_protocols = (SOCKET_OPTION_LEVEL_UDP,)
        else:
            socket_protocols = (SOCKET_OPTION_LEVEL_TCP,)
    else:
        raise GetAddressInfoError(
            ERROR_CODE_ADDRESS_INFO_SOCKET_TYPE,
            f'Socket type not supported; socket_type = {socket_type!r}.',
        )
    
    # Validate socket protocol
    if socket_protocol:
        # I have no idea whether this is the correct validation.
        for index in range(len(socket_protocols)):
            if socket_protocols[index] == socket_protocol:
                break
        
        else:
            raise GetAddressInfoError(
                ERROR_CODE_ADDRESS_INFO_SERVICE,
                (
                    f'Protocol not supported for socket type; socket_type = {socket_type!r}; '
                    f'socket_protocol = {socket_protocol!r}.'
                ),
            )
        
        if len(socket_protocols) != 1:
            socket_types = (socket_types[index],)
            socket_protocols = (socket_protocols[index],)
    
    # This scenario is not implemented
    if (socket_flags & ADDRESS_INFO_ADDRESS_CONFIGURATION) or (socket_flags & ADDRESS_INFO_IP_V4_MAPPED):
        raise GetAddressInfoError(
            ERROR_CODE_ADDRESS_INFO_RESOLUTION_FAILURE,
            (
                f'Non recoverable failure in name resolution; Unsupported socket flags given: '
                f'{ADDRESS_INFO_ADDRESS_CONFIGURATION!r} / {ADDRESS_INFO_IP_V4_MAPPED!r}; '
                f'socket_flags = {socket_flags!r}.'
            ),
        )
    
    intermediate_addresses = []
    
    while True:
        # If host is empty, fill with local host.
        if host_name is None:
            for socket_family in socket_families:
                if socket_family == SOCKET_FAMILY_IP_V4:
                    ip_type = IP_TYPE_IP_V4
                    ip_value = (127 << 24) | 1
                else:
                    ip_type = IP_TYPE_IP_V6
                    ip_value = 1
                
                intermediate_addresses.append((ip_type, ip_value, None, 0))
            
            break
        
        
        # If the given `host_name` is an ip, we parse it.
        for socket_family in socket_families:
            if socket_family == SOCKET_FAMILY_IP_V4:
                matched, ip_value = parse_ip_v4_string(host_name)
                if not matched:
                    continue
                
                ip_type = IP_TYPE_IP_V4
                network_interface_index = 0
            
            else:
                matched, ip_value, percentage_index = parse_ip_v6_string(host_name)
                if not matched:
                    continue
                
                ip_type = IP_TYPE_IP_V6
                if percentage_index == -1:
                    scope = None
                
                else:
                    if percentage_index == len(host_name) - 1:
                        scope = None
                    else:
                        scope = host_name[percentage_index + 1 :]
                
                if scope is None:
                    network_interface_index = 0
                elif scope.isdigit():
                    network_interface_index = int(scope)
                else:
                    network_interface_index = get_network_interface_index(scope)
                
            intermediate_addresses.append((ip_type, ip_value, None, network_interface_index))
            
        
        # `ADDRESS_INFO_NUMERIC_HOST` requires the given `host_name` to be an ip, so we force return if that happens.
        # Else we only return if we matched any output.
        if (socket_flags & ADDRESS_INFO_NUMERIC_HOST) or intermediate_addresses:
            break
        
        # Note:
        # Wanted to implement extended dns keep-alive, so added`Query.additional_resource_records`,
        # But seems like the local linux service and google's servers ignore it as well.
        # If you can find a server that does not ignore it and should be added, you know where to find me.
        # 
        # (
        #     ResourceRecord(
        #         None,
        #         RESOURCE_RECORD_TYPE_OPT,
        #         1232,
        #         0,
        #         OPTION_TYPE_KEEP_ALIVE.to_bytes(2, 'big') + b'\00\00',
        #     ),
        # ),
        
        for labels in iter_labels_with_searches(resolve_configuration, parse_labels_from_name(host_name)):
            async for result in async_iter_execute_query_async(
                event_loop,
                Query(
                    _get_next_id(),
                    True,
                    True,
                    (*(
                        Question(
                            labels,
                            (
                                RESOURCE_RECORD_TYPE_IP_V4_ADDRESS
                                if socket_family == SOCKET_FAMILY_IP_V4 else
                                RESOURCE_RECORD_TYPE_IP_V6_ADDRESS),
                            CLASS_CODE_INTERNET,
                        )
                        for socket_family in socket_families
                    ),),
                    None,
                ),
                resolve_configuration,
                ssl_context,
            ):
                answers = result.answers
                if (answers is None):
                    continue
                
                for resource_record in answers:
                    if socket_flags & ADDRESS_INFO_CANONICAL_NAME:
                        canonical_name = build_name_from_labels(resource_record.labels)
                    else:
                        canonical_name = None
                    
                    resource_record_type = resource_record.resource_record_type
                    data = resource_record.data
                    if resource_record_type == RESOURCE_RECORD_TYPE_IP_V4_ADDRESS:
                        ip_value = parse_ip_v4_data(data)
                        if ip_value is None:
                            continue
                        
                        ip_type = IP_TYPE_IP_V4
                        socket_family = SOCKET_FAMILY_IP_V4
                    
                    elif resource_record_type == RESOURCE_RECORD_TYPE_IP_V6_ADDRESS:
                        ip_value = parse_ip_v6_data(data)
                        if ip_value is None:
                            continue
                        
                        ip_type = IP_TYPE_IP_V6
                        socket_family = SOCKET_FAMILY_IP_V6
                    
                    else:
                        continue
                    
                    if (socket_family not in socket_families):
                        continue
                    
                    intermediate_addresses.append((ip_type, ip_value, canonical_name, 0))
                    continue
            
            if intermediate_addresses:
                break
            
        break
    
    if not intermediate_addresses:
        raise GetAddressInfoError(
            ERROR_CODE_ADDRESS_INFO_NO_NAME,
            'Name and service not known.',
        )
    
    output = []
    for ip_type, ip_value, canonical_name, network_interface_index in iter_intermediate_intermediate_addresses_ordered(
        resolve_configuration, intermediate_addresses
    ):
        if ip_type == IP_TYPE_IP_V4:
            socket_family = SOCKET_FAMILY_IP_V4
            address_tuple = (''.join([*produce_ip_v4_string(ip_value)]), port)
        else:
            socket_family = SOCKET_FAMILY_IP_V6
            address_tuple = (''.join([*produce_ip_v6_string(ip_value)]), port, 0, network_interface_index)
        
        if (canonical_name is None):
            canonical_name = ''
        
        for socket_type, socket_protocol in zip(socket_types, socket_protocols):
            output.append((socket_family, socket_type, socket_protocol, canonical_name, address_tuple))
    
    return output


@export
async def get_name_info_async(
    event_loop,
    socket_address,
    socket_flags = 0,
    *,
    resolve_configuration = None,
    ssl_context = None,
):
    """
    Gets name info for the given host name and port pair.
    (For ip v6, should also have additional flow info and scope fields.)
    
    This function is a coroutine.
    
    Parameters
    ----------
    event_loop : ``EventThread``
        Event loop to use.
    
    socket_address : `(str, int) | (str, int, int, int)`
        Socket address to query for.
    
    socket_flags : `int` = `0`, Optional
        Socket flags to query as.
    
    resolve_configuration : ``None | ResolveConfiguration``, Optional (Keyword only)
        Resolve configuration to query as.
    
    ssl_context : ``None | SSLContext`, Optional (Keyword only)
        SSL context to use when using secure connection.
    
    Returns
    -------
    output : `(str, str)`
    
    Raises
    ------
    OsError
    GetAddressInfoError
    """
    # Set configuration if required.
    if resolve_configuration is None:
        resolve_configuration = RESOLVE_CONFIGURATION_DEFAULT
    
    # Unpack socket_address
    socket_address_length = len(socket_address)
    if socket_address_length == 2:
        has_scope = False
        socket_family = SOCKET_FAMILY_IP_V4
        
    elif socket_address_length == 4:
        has_scope = True
        scope = socket_address[3]
        socket_family = SOCKET_FAMILY_IP_V6
    
    else:
        raise GetAddressInfoError(
            ERROR_CODE_ADDRESS_INFO_SERVICE,
            (
                f'`socket_address` length can be 2 or 4, got {socket_address_length!r}; '
                f'socket_address = {socket_address!r}.'
            ),
        )
    
    host_name = socket_address[0]
    port = socket_address[1]
    
    address_info = await get_address_info_async(
        event_loop,
        host_name,
        port,
        socket_family,
        SOCKET_TYPE_STREAM,
        SOCKET_OPTION_LEVEL_TCP,
        0,
        resolve_configuration = resolve_configuration,
        ssl_context = ssl_context,
    )
    
    if len(address_info) > 1:
        raise GetAddressInfoError(
            ERROR_CODE_ADDRESS_INFO_NO_NAME,
            '`get_address_info` resolved to multiple addresses.',
        )
    
    address = address_info[0][4][0]
    
    while True:
        if not (socket_flags & NAME_INFO_NUMERIC_HOST):
            async for result in async_iter_execute_query_async(
                event_loop,
                Query(
                    _get_next_id(),
                    True,
                    True,
                    (
                        Question(
                            parse_reversed_labels_from_address(address),
                            RESOURCE_RECORD_TYPE_DOMAIN_NAME_POINTER,
                            CLASS_CODE_INTERNET,
                        ),
                    ),
                    None,
                ),
                resolve_configuration,
                ssl_context,
            ):
                answers = result.answers
                if (answers is not None):
                    break
            else:
                if (socket_flags & NAME_INFO_RAISE_ERROR_IF_NAME_CANNOT_BE_DETERMINED):
                    raise GetAddressInfoError(
                        ERROR_CODE_ADDRESS_INFO_NO_NAME,
                        'Name and service not known.',
                    )
                
                answers = None
            
            if (answers is not None):
                maybe_host_name = parse_domain_name_pointer_data(answers[0].data)
                if (maybe_host_name is not None):
                    host_name = maybe_host_name
                break
        
        host_name = address
        if has_scope:
            host_name = f'{host_name}%{scope!s}'
        break
    
    if socket_flags & NAME_INFO_NUMERIC_SERVICE:
        service = str(port)
    else:
        if socket_flags & NAME_INFO_DATAGRAM:
            protocol_name = 'udp'
        else:
            protocol_name = 'tcp'
        
        try:
            service = get_service_by_protocol(port, protocol_name)
        except OSError as exception:
            raise GetAddressInfoError(
                ERROR_CODE_ADDRESS_INFO_NO_NAME,
                exception.args[0],
            ).with_traceback(exception.__traceback__)
    
    return host_name, service
