__all__ = ('HttpReadProtocol', 'HttpReadWriteProtocol',)

from base64 import b64decode as base64_decode
from binascii import a2b_qp as qp_decode
from functools import partial as partial_func
from random import getrandbits
from struct import Struct

from ..core import ReadProtocolBase, ReadWriteProtocolBase
from ..utils import IgnoreCaseMultiValueDictionary, copy_docs

from .compressors import COMPRESSION_ERRORS, get_decompressor_for
from .exceptions import PayloadError, WebSocketProtocolError
from .headers import CONTENT_ENCODING, CONTENT_LENGTH, CONTENT_TRANSFER_ENCODING, CONTENT_TYPE, METHOD_CONNECT
from .helpers import HttpVersion11, parse_http_headers, parse_http_request, parse_http_response
from .http_message import RawRequestMessage, RawResponseMessage
from .mime_type import MimeType
from .web_socket_frame import WebSocketFrame, apply_web_socket_mask


PAYLOAD_ERROR_EOF_AT_HTTP_HEADER = 'EOF received meanwhile reading http headers.'


UNPACK_LENGTH_2 = Struct('!H').unpack_from
UNPACK_LENGTH_3 = Struct('!Q').unpack_from

PACK_LENGTH_1 = Struct('!BB').pack
PACK_LENGTH_2 = Struct('!BBH').pack
PACK_LENGTH_3 = Struct('!BBQ').pack


class HttpReadProtocol(ReadProtocolBase):
    """
    Asynchronous read protocol implementation. Stuffed full of http read methods.
    
    Attributes
    ----------
    _at_eof : `bool`
        Whether the protocol received end of file.
    
    _chunks : `Deque<bytes>`
        Right feed, left pop queue, used to store the received data chunks.
    
    _exception : `None | BaseException`
        Exception set by ``.set_exception``, when an unexpected exception occur meanwhile reading from socket.
    
    _loop : ``EventThread``
        The event loop to what the protocol is bound to.
    
    _offset : `int`
        Byte offset, of the used up data of the most-left chunk.
    
    _paused : `bool`
        Whether the protocol's respective transport's reading is paused. Defaults to `False`.
        
        Also note, that not every transport supports pausing.
    
    _payload_reader : `None | GeneratorType`
        Payload reader generator, what gets the control back, when data, eof or any exception is received.
    
    _payload_stream : `None | PayloadStream`
        Payload stream of the protocol.
    
    _transport : `None | AbstractTransportLayerBase`
        Asynchronous transport implementation. Is set meanwhile the protocol is alive.
    """
    __slots__ = ()
    
    
    def should_close(self):
        """
        Returns the protocol should be closed.
        
        Returns
        -------
        should_close : `bool`
        """
        if (self._payload_stream is not None):
            return True
        
        if (self._exception is not None):
            return True
        
        if (not self._at_eof) and (self._offset or self._chunks):
            return True
        
        return False
    
    
    async def read_http_response(self):
        """
        Reads http response.
        
        This method is a coroutine.
        
        Returns
        -------
        response_message : ``RawResponseMessage``
        
        Raises
        ------
        PayloadError
            Invalid data received.
        """
        try:
            data = await self.read_until(b'\r\n\r\n')
        except ConnectionError as exception:
            cause = exception.__cause__
            if (cause is not None) and isinstance(cause, EOFError):
                raise PayloadError(PAYLOAD_ERROR_EOF_AT_HTTP_HEADER) from exception
            
            raise
        
        return parse_http_response(data)
    
    
    async def read_http_request(self):
        """
        Reads http request.
        
        This method is a coroutine.
        
        Returns
        -------
        request_message : ``RawResponseMessage``
        
        Raises
        ------
        EOFError
            Connection lost before enough data was received.
        PayloadError
            Invalid data received.
        """
        try:
            data = await self.read_until(b'\r\n\r\n')
        except ConnectionError as exception:
            cause = exception.__cause__
            if (cause is not None) and isinstance(cause, EOFError):
                raise PayloadError(PAYLOAD_ERROR_EOF_AT_HTTP_HEADER) from exception
            
            raise
        
        return parse_http_request(data)
    
    
    async def _read_single_multipart(self, boundary, is_first):
        """
        Reads a single multipart.
        
        This method is a coroutine.
        
        Parameters
        ----------
        boundary : `bytes`
            A boundary that marks the start and the end of the multipart.
        
        is_first : `bool`
            Whether this is the first multipart that we read.
        
        Returns
        -------
        is_more : `bool`
            Whether the payload contains more multipart field.
        
        headers : `None`, ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`)
            Received response headers.
        
        chunk : `None | bytes`
            The field content.
        
        Raises
        ------
        EOFError
            Connection lost before enough data was received.
        PayloadError
            Invalid data received.
        """
        if is_first:
            await self.read_until(b'--' + boundary)
            
            try:
                maybe_end_0 = await self.read_exactly(2)
            except EOFError:
                # End of payload? Ok i guess.
                return False, None, None
            else:
                if maybe_end_0 == b'\r\n':
                    pass
                elif maybe_end_0 == b'--':
                    # End of payload?
                    try:
                        maybe_end_1 = await self.read_exactly(2)
                    except EOFError:
                        return False, None, None
                    else:
                        if maybe_end_1 == b'\r\n':
                            return False, None, None
                        else:
                            raise PayloadError(
                                f'Multipart boundary not ended with b\'--\' + b\'\r\n\', got '
                                f'b\'--\'+{maybe_end_1!r}.'
                            )
                else:
                    raise PayloadError(
                        f'Multipart boundary not ended either with b\'--\' or b\'\r\n\', got '
                        f'{maybe_end_0!r}.'
                    )
        
        data = await self.read_until(b'\r\n\r\n')
        headers = parse_http_headers(data, 0)
        
        length = headers.get(CONTENT_LENGTH, None)
        if length is None:
            part = await self.read_until(b'\r\n--' + boundary)
        else:
            length = int(length)
            part = await self._read_exactly_as_one(length)
            try:
                maybe_boundary = await self.read_exactly(len(boundary) + 4)
            except EOFError:
                return False, None, part
            
            if maybe_boundary != b'\r\n--' + boundary:
                raise PayloadError(
                    f'Multipart payload not ended with boundary, expected: b\'\r\n\' + b\'--\' + '
                    f'{boundary!r}, got {maybe_boundary!r}.'
                )
            
            
        try:
            maybe_end_0 = await self.read_exactly(2)
        except EOFError:
            return False, headers, part
        
        if maybe_end_0 == b'\r\n':
            return True, headers, part
        
        if maybe_end_0 == b'--':
            try:
                maybe_end_1 = await self.read_exactly(2)
            except EOFError:
                return False, headers, part
            
            if maybe_end_1 == b'\r\n':
                return False, headers, part
            
            raise PayloadError(
                f'Multipart boundary not ended with b\'--\'+b\'\r\n\', got '
                f'b\'--\'+{maybe_end_1!r}.'
            )
        
        raise PayloadError(
            f'Multipart boundary not ended either with  b\'--\' or b\'\r\n\', got '
            f'{maybe_end_0!r}.'
        )
    
    
    async def read_multipart(self, headers):
        """
        Reads multipart data from the protocol.
        
        This method is a coroutine generator.
        
        Parameters
        ----------
        headers : ``IgnoreCaseMultiValueDictionary``
            The response's or the request's headers.
        
        Yields
        ------
        headers : `IgnoreCaseMultiValueDictionary`
            The multipart's headers.
        data : `bytes`, `bytes-like`
            The multipart's data.
        
        Raises
        ------
        EOFError
            Connection lost before enough data was received.
        PayloadError
            Invalid data received.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        ContentEncodingError
            - `'content_encoding'` was given as `'br'` meanwhile brotli or brotlipy are not installed.
            - `'content_encoding'` is not an from the expected values.
        StopAsyncIteration
            The payload contains no more fields.
        """
        content_type = headers[CONTENT_TYPE]
        mime = MimeType(content_type)
        boundary = mime.parameters['boundary']
        
        is_first = True
        while True:
            is_more, headers, data = await self._read_single_multipart(boundary, is_first)
            if (data is not None):
                try:
                    transfer_encoding = headers[CONTENT_TRANSFER_ENCODING]
                except KeyError:
                    pass
                else:
                    transfer_encoding = transfer_encoding.casefold()
                    if transfer_encoding == 'base64':
                        data = base64_decode(data)
                    elif transfer_encoding == 'quoted-printable':
                        data = qp_decode(data)
                    elif transfer_encoding in ('binary', '8bit', '7bit'):
                        pass
                    else:
                        raise PayloadError(f'Unknown transfer encoding: {transfer_encoding!r}.')
                
                try:
                    content_encoding = headers[CONTENT_ENCODING]
                except KeyError:
                    pass
                else:
                    content_encoding = content_encoding.casefold()
                    decompressor = get_decompressor_for(content_encoding)
                    if (decompressor is not None):
                        try:
                            data = decompressor.decompress(data)
                        except COMPRESSION_ERRORS as exception:
                            raise PayloadError('Cannot decompress data.') from exception
                
                yield headers, data
            
            if not is_more:
                return
            
            is_first = False
            continue
    
    
    async def read_web_socket_frame(self, client_side, max_size):
        """
        Reads a web socket frame.
        
        This method is a coroutine.
        
        Returns
        -------
        frame : ``WebSocketFrame``
            The read web socket frame.
        
        Raises
        ------
        EofError
            Connection lost before a full frame was received.
        PayloadError
            Payload length over max size limit.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        head_0, head_1 = await self.read_exactly(2)
        
        if ((head_1 & 0b10000000) >> 7) == client_side:
            raise WebSocketProtocolError('Incorrect masking.')
        
        length = head_1 & 0b01111111
        
        if length == 126:
            data = await self.read_exactly(2)
            length, = UNPACK_LENGTH_2(data)
        elif length == 127:
            data = await self.read_exactly(8)
            length, = UNPACK_LENGTH_3(data)
        
        if (max_size is not None) and length > max_size:
            raise PayloadError(f'Payload length exceeds size limit ({length} > {max_size} bytes).')
        
        # Read the data.
        if client_side:
            data = await self.read_exactly(length)
        else:
            mask = await self.read_exactly(4)
            data = await self.read_exactly(length)
            data = apply_web_socket_mask(mask, data)
        
        return WebSocketFrame._from_fields(head_0, data)
    
    
    def get_payload_reader_task(self, message):
        """
        Gets payload reader task for the given raw http message.
        
        Parameters
        ----------
        message : ``RawMessage``
            Raw http message. Can be either request or response.
        
        Returns
        -------
        payload_reader_task : `None`, `GeneratorType`
            Payload reader task if applicable.
        """
        length = message.headers.get(CONTENT_LENGTH, None)
        if (length is not None):
            if length.isdigit():
                length = int(length)
            else:
                raise PayloadError(f'{CONTENT_LENGTH} must be a non negative int, got: {length!r}.')
        
        if (not message.upgraded):
            if message.status == 204:
                return None
            
            if message.chunked:
                decompressor = get_decompressor_for(message.encoding)
                if decompressor is None:
                    return self._read_chunked
                else:
                    return partial_func(self._read_chunked_encoded, decompressor)
            
            if (length is not None) and (length > 0):
                decompressor = get_decompressor_for(message.encoding)
                if decompressor is None:
                    return partial_func(self._read_exactly, length, False)
                else:
                    return partial_func(self._read_exactly_encoded, length, decompressor)
        
        if isinstance(message, RawRequestMessage) and (message.method == METHOD_CONNECT):
            message.upgraded = True
            return self._read_until_eof
        
        if isinstance(message, RawResponseMessage) and message.status >= 199 and (length is None):
            if message.status == 204:
                return None
            
            if message.chunked:
                decompressor = get_decompressor_for(message.encoding)
                if decompressor is None:
                    return self._read_chunked
                else:
                    return partial_func(self._read_chunked_encoded, decompressor)
            
            return self._read_until_eof
        
        return None
    
    
    async def _read_chunked_by_chunk(self):
        """
        Reads a chunked http message by chunk and yields it back. Used by other payload readers.
        
        This method is a coroutine generator.
        
        Yields
        -------
        chunk : `bytes | memoryview`
        
        Raises
        ------
        EofError
            Connection lost before `n` bytes were received.
        PayloadError
            - Chunk size is not hexadecimal.
            - Chunk not ends with CRLF.
        """
        while True:
            line = await self._read_until_as_one(b'\r\n')
            # strip chunk extension
            index = line.find(b';')
            if index != -1:
                line = line[:index]
            
            try:
                length = int(line, 16)
            except ValueError:
                raise PayloadError(
                    f'Not hexadecimal chunk size: {line!r}.'
                ) from None
            
            if length == 0:
                end = await self._read_exactly_as_one(2)
                if end != b'\r\n':
                    raise PayloadError(
                        f'Received chunk does not end with b\'\\r\\n\', instead with: {end}.'
                    )
                break
            
            async for chunk in self._read_exactly_by_chunk(length):
                yield chunk
            
            end = await self._read_exactly_as_one(2)
            if end != b'\r\n':
                raise PayloadError(
                    f'Received chunk does not end with b\'\\r\\n\', instead with: {end}.'
                )
    
    
    async def _read_chunked(self, payload_stream):
        """
        Payload reader task, that reads a chunked http message, till it ends.
        
        This method is a coroutine.
        
        Parameters
        ----------
        payload_stream : ``PayloadStream``
            Payload buffer to read into.
        
        Raises
        ------
        EofError
            Connection lost before `n` bytes were received.
        PayloadError
            - Chunk size is not hexadecimal.
            - Chunk not ends with CRLF.
        """
        async for chunk in self._read_chunked_by_chunk():
            payload_stream.add_received_chunk(chunk)
    
    
    async def _read_exactly_encoded(self, length, decompressor, payload_stream):
        """
        Payload reader task, that reads exactly `n` bytes from the protocol, then decompresses it with the given
        decompress object.
        
        This method is a coroutine.
        
        Parameters
        ----------
        length : `int`
            The amount of bytes to read.
        
        decompressor : `ZLIB_DECOMPRESSOR`, `BROTLI_DECOMPRESSOR`
            Decompressor used to decompress the data after receiving it.
        
        payload_stream : ``PayloadStream``
            Payload buffer to read into.
        
        Returns
        -------
        collected : `bytes`
        
        Raises
        ------
        EofError
            Connection lost before `n` bytes were received.
        PayloadError
            Cannot decompress a chunk.
        """
        async for chunk in self._read_exactly_by_chunk(length):
            try:
                chunk = decompressor.decompress(chunk)
            except COMPRESSION_ERRORS:
                raise PayloadError('Cannot decompress chunk.') from None
            
            payload_stream.add_received_chunk(chunk)
        
        
        # Flush decompressor at the end in case it is required.
        try:
            chunk = decompressor.flush()
        except COMPRESSION_ERRORS:
            raise PayloadError('Cannot decompress chunk.') from None
        
        if chunk:
            payload_stream.add_received_chunk(chunk)
    
    
    async def _read_chunked_encoded(self, decompressor, payload_stream):
        """
        Payload reader task, that reads a chunked http message, till it ends. After receiving a "chunk", decompresses
        it.
        
        This method is a coroutine.
        
        Parameters
        ----------
        decompressor : `ZLIB_DECOMPRESSOR`, `BROTLI_DECOMPRESSOR`
            Decompressor used to decompress the data after receiving it.
        
        payload_stream : ``PayloadStream``
            Payload buffer to read into.
            
        Returns
        -------
        collected : `bytes`
        
        Raises
        ------
        EofError
            Connection lost before `n` bytes were received.
        PayloadError
            - Chunk size is not hexadecimal.
            - Chunk not ends with CRLF.
            - Cannot decompress a chunk.
        """
        async for chunk in self._read_chunked_by_chunk():
            try:
                chunk = decompressor.decompress(chunk)
            except COMPRESSION_ERRORS:
                raise PayloadError('Cannot decompress chunk.') from None
            
            payload_stream.add_received_chunk(chunk)
        
        
        # Flush decompressor at the end in case it is required.
        try:
            chunk = decompressor.flush()
        except COMPRESSION_ERRORS:
            raise PayloadError('Cannot decompressor chunk.') from None
        
        if chunk:
            payload_stream.add_received_chunk(chunk)
    
    
    def isekai_into(self, other_class):
        """
        Copies the protocol's attributes to an other one.
        
        Can be used to change a protocol's type.
        
        Parameters
        ----------
        other_class : `type`
            The other protocol asynchronous protocol type to isekai self into.
        
        Returns
        -------
        new : `other_class
        """
        new = object.__new__(other_class)
        
        new._loop = self._loop
        new._transport = self._transport
        new._exception = self._exception
        new._chunks = self._chunks
        new._offset = self._offset
        new._at_eof = self._at_eof
        new._payload_reader = self._payload_reader
        new._payload_stream = self._payload_stream
        new._paused = self._paused
        
        return new
    

class HttpReadWriteProtocol(ReadWriteProtocolBase, HttpReadProtocol):
    """
    Asynchronous read-write protocol implementation. Stuffed full of http read methods.
    
    Attributes
    ----------
    _at_eof : `bool`
        Whether the protocol received end of file.
    _chunks : `deque` of `bytes`
        Right feed, left pop queue, used to store the received data chunks.
    _exception : `None`, `BaseException`
        Exception set by ``.set_exception``, when an unexpected exception occur meanwhile reading from socket.
    _loop : ``EventThread``
        The event loop to what the protocol is bound to.
    _offset : `int`
        Byte offset, of the used up data of the most-left chunk.
    _paused : `bool`
        Whether the protocol's respective transport's reading is paused. Defaults to `False`.
        
        Also note, that not every transport supports pausing.
    _payload_reader : `None`, `GeneratorType`
        Payload reader generator, what gets the control back, when data, eof or any exception is received.
    _payload_stream : `None` of ``Future``
        Payload waiter of the protocol, what's result is set, when the ``.payload_reader`` generator returns.
        
        If cancelled or marked by done or any other methods, the payload reader will not be cancelled.
    _transport : `None`, `object`
        Asynchronous transport implementation. Is set meanwhile the protocol is alive.
    _drain_waiter : `None`, ``Future``
        A future, what is used to block the writing task, till it's writen data is drained.
    """
    __slots__ = ()
    
    def write_http_request(self, method, path, headers, version = HttpVersion11):
        """
        Writes an http request to the protocol's transport.
        
        Parameters
        ----------
        method : `str`
            The request's method.
        path : `str`
            The request's path.
        headers : ``IgnoreCaseMultiValueDictionary``
            Request headers.
        version : ``HttpVersion`` = `HttpVersion11`, Optional
            Http version of the request. Defaults to `HttpVersion11`.
        
        Raises
        ------
        RuntimeError
            Protocol has no attached transport.
        """
        transport = self._transport
        if transport is None:
            raise RuntimeError(f'Protocol has no attached transport; self = {self!r}.')
        
        result = [f'{method} {path} HTTP/{version.major}.{version.major}\r\n']
        extend = result.extend
        for k, v in headers.items():
            extend((k, ': ', v, '\r\n'))
        
        result.append('\r\n')
        transport.write(''.join(result).encode())
    
    
    def write_http_response(self, status, headers, version = HttpVersion11, body = None):
        """
        Writes an http response to the protocol's transport.
        
        Parameters
        ----------
        status : `http.HTTPStatus`
            The response's status.
        headers : ``IgnoreCaseMultiValueDictionary``
            Response headers.
        version : ``HttpVersion`` = `HttpVersion11`, Optional
            Http version of the response. Defaults to `HttpVersion11`.
        body : `None`, `bytes-like` = `None`, Optional
            Http response body.
        
        Raises
        ------
        RuntimeError
            Protocol has no attached transport.
        """
        transport = self._transport
        if transport is None:
            raise RuntimeError(f'Protocol has no attached transport; self = {self!r}.')
        
        result = [
            'HTTP/',
            str(version.major),
            '.',
            str(version.minor),
            ' ',
            str(status.value),
            ' ',
            str(status.phrase),
            '\r\n',
        ]
        
        for header_key, header_value in headers.items():
            result.extend((header_key, ': ', header_value, '\r\n'))
        
        result.append('\r\n')
        
        transport.write(''.join(result).encode())
        if (body is not None) and body:
            transport.write(body)
    
    
    def write_web_socket_frame(self, frame, client_side):
        """
        Writes a web socket frame to the protocol.
        
        Parameters
        ----------
        frame : ``WebSocketFrame``
            The web socket frame to write.
        client_side : `bool`
            Whether the respective web socket is client or server side.
        
        Raises
        ------
        RuntimeError
            Protocol has no attached transport.
        """
        transport = self._transport
        if transport is None:
            raise RuntimeError(f'Protocol has no attached transport; self = {self!r}.')
        
        # Prepare the header.
        head_0 = frame.head_0
        head_1 = client_side << 7
        
        length = len(frame.data)
        if length < 126:
            header = PACK_LENGTH_1(head_0, head_1 | length)
        elif length < 65536:
            header = PACK_LENGTH_2(head_0, head_1 | 126, length)
        else:
            header = PACK_LENGTH_3(head_0, head_1 | 127, length)
        transport.write(header)
        
        # prepare the data.
        if client_side:
            mask = getrandbits(32).to_bytes(4, 'big')
            transport.write(mask)
            data = apply_web_socket_mask(mask, frame.data,)
        else:
            data = frame.data
        
        transport.write(data)

    
    @copy_docs(HttpReadProtocol.isekai_into)
    def isekai_into(self, other_class):
        new = HttpReadProtocol.isekai_into(self, other_class)
        
        new._drain_waiter = self._drain_waiter
        
        return new
