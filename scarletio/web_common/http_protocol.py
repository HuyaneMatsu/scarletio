__all__ = ('HttpReadProtocol', 'HttpReadWriteProtocol',)

from base64 import b64decode as base64_decode
from binascii import a2b_qp as qp_decode
from random import getrandbits
from re import compile as re_compile
from struct import Struct

from ..core import ReadProtocolBase, ReadWriteProtocolBase
from ..utils import IgnoreCaseMultiValueDictionary, copy_docs

from .compressors import COMPRESSION_ERRORS, get_decompressor_for
from .exceptions import PayloadError, WebSocketProtocolError
from .headers import CONTENT_ENCODING, CONTENT_LENGTH, CONTENT_TRANSFER_ENCODING, CONTENT_TYPE, METHOD_CONNECT
from .helpers import HttpVersion
from .helpers import HttpVersion11
from .http_message import RawRequestMessage, RawResponseMessage
from .mime_type import MimeType
from .websocket_frame import WebSocketFrame, apply_websocket_mask


HTTP_STATUS_RP = re_compile(b'HTTP/(\\d+)\\.(\\d+) (\\d\\d\\d)(?: (.*?))?\r\n')
HTTP_REQUEST_RP = re_compile(b'([^ ]+) ([^ ]+) HTTP/(\\d+)\\.(\\d+)\r\n')

HTTP_STATUS_LINE_RP = re_compile(b'HTTP/(\\d+)\\.(\\d+) (\\d\\d\\d)(?: (.*?))?')
HTTP_REQUEST_LINE_RP = re_compile(b'([^ ]+) ([^ ]+) HTTP/(\\d+)\\.(\\d+)')

MAX_LINE_LENGTH = 8190


CONNECTION_ERROR_EOF_NO_HTTP_HEADER = (
    'Stream closed before any data was received. (Might be caused by bad connection on your side, like the other side '
    'might have closed the stream before receiving the full payload.)'
)

PAYLOAD_ERROR_EOF_AT_HTTP_HEADER = (
    'EOF received meanwhile reading http headers.'
)


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
    _payload_waiter : `None` of ``Future``
        Payload waiter of the protocol, what's result is set, when the ``.payload_reader`` generator returns.
        
        If cancelled or marked by done or any other methods, the payload reader will not be cancelled.
    _transport : `None`, `object`
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
        if (self._payload_waiter is not None):
            return True
        
        if (self._exception is not None):
            return True
        
        if (not self._at_eof) and (self._offset or self._chunks):
            return True
        
        return False
    
    
    def _read_until_CRLF(self):
        """
        Payload reader task helper, what returns a received line until `CRLF` (`\\r\\n`). Note, that `CRLF` is not
        including the returned value, tho they are added to the read offset.
        
        This method is a generator.
        
        Returns
        -------
        collected : `bytes`
        
        Raises
        ------
        EOFError
            Connection lost before a line could be read.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        exception = self._exception
        if (exception is not None):
            raise exception
        
        chunks = self._chunks
        
        if chunks:
            chunk = chunks[0]
        else:
            if self._at_eof:
                raise EOFError(b'')
            
            chunk = yield from self._wait_for_data()
        
        # Do first search outside, because we operate with offset
        offset = self._offset
        
        position = chunk.find(b'\r\n', offset)
        
        if position != -1:
            # We found!
            # Because the result must be bytes, we slice it
            collected = chunk[offset:position]
            # Add 2 to position to compensate CRLF
            position += 2
            
            # If the chunk is exhausted, remove it
            if len(chunk) == position:
                del chunks[0]
                self._offset = 0
            # Else, offset it, fast slicing!
            else:
                self._offset = position
            
            return collected
        
        # If first did not succeed, lets go normally.
        collected = []
        n = MAX_LINE_LENGTH - len(chunk)
        # If there is offset, apply it
        if offset:
            collected.append(memoryview(chunk)[offset:])
            n += offset
        else:
            collected.append(chunk)
        del chunks[0]
        
        while True:
            # case 2: found between 2?
            if chunk[-1] == b'\r'[0]:
                if chunks:
                    chunk = chunks[0]
                else:
                    if self._at_eof:
                        chunks.clear()
                        self._offset = 0
                        raise EOFError(b''.join(collected))
                    
                    chunk = yield from self._wait_for_data()
                
                if chunk[0] == b'\n'[0]:
                    # If size is 1, we delete it
                    if len(chunk) == 1:
                        del chunks[0]
                        self._offset = 0
                    # If more, fast slice it!
                    else:
                        self._offset = 1
                    
                    # cast memory view, so we do not need to create a new immutable
                    collected[-1] = memoryview(collected[-1])[:-1]
                    
                    return b''.join(collected)
                
            else:
                # case 3: not found, go for next chunk
                if chunks:
                    chunk = chunks[0]
                else:
                    if self._at_eof:
                        chunks.clear()
                        self._offset = 0
                        raise EOFError(b''.join(collected))
                    
                    chunk = yield from self._wait_for_data()
            
            # no offset search
            position = chunk.find(b'\r\n')
            
            # case 1: found in middle
            if position != -1:
                # cast memoryview
                collected.append(memoryview(chunk)[:position])
                
                # Add 2 position to compensate CRLF
                position += 2
                # If the chunk is fully exhausted remove it
                if len(chunk) == position:
                    del chunks[0]
                    self._offset = 0
                # Fast slice the rest of the chunk with offset
                else:
                    self._offset = position
                
                return b''.join(collected)
            
            # collected the data
            collected.append(chunk)
            del chunks[0]
            n -= len(chunk)
            if n < 0:
                raise PayloadError(
                    f'Header line exceeds max line length: {MAX_LINE_LENGTH!r} by {-n!r} and CRLF still not found.'
                )
            
            continue


    def _read_multipart(self, boundary, is_first):
        """
        Payload reader task, which reads an http response's status line and headers.
        
        This method is a generator.
        
        Returns
        -------
        is_more : `bool`
            Whether the payload contains more multipart field.
        headers : `None`, ``IgnoreCaseMultiValueDictionary`` of (`str`, `str`)
            Received response headers.
        chunk : `None`, `bytes`, `bytearray`
            The field content.
        
        Raises
        ------
        EOFError
            Connection lost before enough data was received.
        PayloadError
            Invalid data received.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        if is_first:
            yield from self._read_until(b'--' + boundary)
            try:
                maybe_end_1 = yield from self._read_exactly(2)
            except EOFError:
                # End of payload? Ok i guess.
                return False, None, None
            else:
                if maybe_end_1 == b'\r\n':
                    pass
                elif maybe_end_1 == b'--':
                    # End of payload?
                    try:
                        maybe_end_2 = yield from self._read_exactly(2)
                    except EOFError:
                        return False, None, None
                    else:
                        if maybe_end_2 == b'\r\n':
                            return False, None, None
                        else:
                            raise PayloadError(
                                f'Multipart boundary not ended with b\'--\' + b\'\r\n\', got '
                                f'b\'--\'+{maybe_end_2!r}.'
                            )
                else:
                    raise PayloadError(
                        f'Multipart boundary not ended either with b\'--\' or b\'\r\n\', got '
                        f'{maybe_end_1!r}.'
                    )
        
        chunk, offset = yield from self._read_http_helper()
        headers = yield from self._read_http_headers(chunk, offset)
        
        length = headers.get(CONTENT_LENGTH, None)
        if length is None:
            part = yield from self._read_until(b'\r\n--' + boundary)
        else:
            length = int(length)
            part = yield from self._read_exactly(length)
            try:
                maybe_boundary = yield from self._read_exactly(len(boundary) + 4)
            except EOFError:
                return False, None, part
            
            if maybe_boundary != b'\r\n--' + boundary:
                raise PayloadError(
                    f'Multipart payload not ended with boundary, expected: b\'\r\n\' + b\'--\' + '
                    f'{boundary!r}, got {maybe_boundary!r}.'
                )
            
            
        try:
            maybe_end_1 = yield from self._read_exactly(2)
        except EOFError:
            return False, headers, part
        
        if maybe_end_1 == b'\r\n':
            return True, headers, part
        
        if maybe_end_1 == b'--':
            try:
                maybe_end_2 = yield from self._read_exactly(2)
            except EOFError:
                return False, headers, part
            
            if maybe_end_2 == b'\r\n':
                return False, headers, part
            
            raise PayloadError(
                f'Multipart boundary not ended with b\'--\'+b\'\r\n\', got '
                f'b\'--\'+{maybe_end_2!r}.'
            )
        
        raise PayloadError(
            f'Multipart boundary not ended either with  b\'--\' or b\'\r\n\', got '
            f'{maybe_end_1!r}.'
        )
    
    
    async def read_multipart(self, headers):
        """
        Reads multipart data from the protocol
        
        This method is an asynchronous generator.
        
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
            is_more, headers, data = await self.set_payload_reader(self._read_multipart(boundary, is_first))
            if data is not None:
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
                        except COMPRESSION_ERRORS:
                            raise PayloadError('Cannot decompress data.') from None
                
                yield headers, data
            
            if not is_more:
                return
            
            is_first = False
            continue
    
    def _read_http_helper(self):
        """
        Payload reader task helper. Returns if any chunk is already received, or waits for a new one.
        
        This method is a generator.
        
        Returns
        -------
        chunk : `bytes`
            A received chunk of data.
        offset : `int`
            The offset, till the chunk was already used up.
        
        Raises
        ------
        EOFError
            Connection lost before a chunk was received.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        chunks = self._chunks
        if chunks:
            chunk = chunks[0]
            offset = self._offset
        else:
            if self._at_eof:
                raise EOFError(b'')
            
            chunk = yield from self._wait_for_data()
            offset = 0
        
        return chunk, offset
    
    def _read_http_response(self):
        """
        Payload reader task, which reads an http response's status line and headers.
        
        This method is a generator.
        
        Returns
        -------
        response_message : ``RawResponseMessage``
        
        Raises
        ------
        ConnectionError
            Connection lost before enough data was received.
        PayloadError
            Invalid data received.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        try:
            try:
                chunk, offset = yield from self._read_http_helper()
            except EOFError as err:
                args = err.args
                if (args is None) or (not args) or (not args[0]):
                    raise ConnectionError(CONNECTION_ERROR_EOF_NO_HTTP_HEADER)
                
                raise
            
            parsed = HTTP_STATUS_RP.match(chunk, offset)
            if parsed is None:
                # stupid fallback
                line = yield from self._read_until_CRLF()
                parsed = HTTP_STATUS_LINE_RP.fullmatch(line)
                if parsed is None:
                    raise PayloadError(f'Invalid status line: {line!r}.')
                
                chunk, offset = yield from self._read_http_helper()
            else:
                offset = parsed.end()
                
            major, minor, status, reason = parsed.groups()
            
            headers = yield from self._read_http_headers(chunk, offset)
            return RawResponseMessage(HttpVersion(int(major), int(minor)), int(status), reason, headers)
        except EOFError as err:
            raise PayloadError(PAYLOAD_ERROR_EOF_AT_HTTP_HEADER) from err
    
    def _read_http_request(self):
        """
        Payload reader task, which reads an http request's status line and headers.
        
        This method is a generator.
        
        Returns
        -------
        request_message : ``RawRequestMessage``
        
        Raises
        ------
        ConnectionError
            Connection lost before enough data was received.
        PayloadError
            Invalid data received.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        try:
            try:
                chunk, offset = yield from self._read_http_helper()
            except EOFError as err:
                args = err.args
                if (args is None) or (not args) or (not args[0]):
                    raise ConnectionError(CONNECTION_ERROR_EOF_NO_HTTP_HEADER)
                
                raise
            
            parsed = HTTP_REQUEST_RP.match(chunk, offset)
            if parsed is None:
                # stupid fallback
                line = yield from self._read_until_CRLF()
                parsed = HTTP_REQUEST_LINE_RP.fullmatch(line)
                if parsed is None:
                    raise PayloadError(f'invalid request line: {line!r}.')
                
                chunk, offset = yield from self._read_http_helper()
            else:
                offset = parsed.end()
            
            method, path, major, minor = parsed.groups()
            
            headers = yield from self._read_http_headers(chunk, offset)
            path = path.decode('ascii', 'surrogateescape')
            return RawRequestMessage(HttpVersion(int(major), int(minor)), method.upper().decode(), path, headers)
        except EOFError as err:
            raise PayloadError(PAYLOAD_ERROR_EOF_AT_HTTP_HEADER) from err
    
    
    def _read_http_headers(self, chunk, offset):
        """
        Payload reader task helper, which reads an http headers.
        
        This method is a generator.
        
        Parameters
        ----------
        chunk : `bytes`
            The actual chunk from what we are reading.
        offset : `int`
            The offset, till the actual chunk is exhausted.
        
        Returns
        -------
        headers : ``IgnoreCaseMultiValueDictionary``
        
        Raises
        ------
        EOfError
            Connection lost before headers were closed.
        PayloadError
            Invalid data received.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        headers = IgnoreCaseMultiValueDictionary()
        chunks = self._chunks
        
        end = chunk.find(b'\r\n', offset)
        # At this case something is in the istr line, but is it a header?
        if end > offset:
            middle = chunk.find(b':', offset, end)
            if middle <= offset:
                raise PayloadError(f'Invalid header line: {chunk[offset:end]!r}.')
            
            name = chunk[offset:middle].lstrip()
            value = chunk[middle + 1:end].strip()
            offset = end + 2
        
        # Found \r\n instantly, we done!
        # The case, when there is nothing inside of the headers.
        elif end == offset:
            # If we are at the end of a chunk, remove it and save the offset.
            offset += 2
            if offset == len(chunk):
                del chunks[0]
                offset = 0
            
            self._offset = offset
            return headers
        # End is -1, so the header line ends at the incoming chunk, maybe?
        else:
            # we are at the end?
            if len(chunk) == offset:
                del chunks[0]
                offset = 0
            
            # Store offset
            self._offset = offset
            # try getting a full line
            line = yield from self._read_until_CRLF()
            # no headers at all? OK, I guess
            if not line:
                # because ._read_until_CRLF updates the chunk and the offset state for us, not needed to store it.
                return headers
            
            middle = line.find(b':')
            if middle <= 0:
                # Nothing to do, no more case
                raise PayloadError(f'Invalid header line: {line!r}.')
            
            name = line[:middle]
            value = line[middle + 1:]
            
            # Jump on this part at the end if not done, we will need this for checking continuous lines.
            if chunks:
                chunk = chunks[0]
                offset = self._offset
            else:
                if self._at_eof:
                    raise EOFError(b'')
                
                chunk = yield from self._wait_for_data()
                offset = 0
        
        name = name.decode('utf-8', 'surrogateescape')
        
        while True:
            if chunk[offset] in (b'\t'[0], b' '[0]):
                # continuous
                value = [value]
                while True:
                    end = chunk.find(b'\r\n', offset)
                    # most likely case if we find \r\n
                    if end > offset:
                        value.append(chunk[offset:end].strip())
                        # add \r\n shift
                        offset = end + 2
                        
                        # if we are at the en of the chunk, we need again a new one for continuous check
                        if offset == len(chunk):
                            del chunks[0]
                            if chunks:
                                chunk = chunks[0]
                            else:
                                if self._at_eof:
                                    raise EOFError(b'')
                                
                                chunk = yield from self._wait_for_data()
                            
                            offset = 0
                        
                        # If next line is continuous as well, continue loop
                        if chunk[offset] in (b'\t'[0], b' '[0]):
                            continue
                        
                        # Not continuous, join lines and break
                        value = b' '.join(value)
                        break
                    
                    # We cannot be at the end now, because we just checked continuous above >.> at least 1 char
                    
                    # We did not find \r\n
                    # Store offset and get a full line
                    self._offset = offset
                    line = yield from self._read_until_CRLF()
                    
                    # We cannot get empty line, because we just checked continuous above <.< at least 1 char
                    
                    # Tho it can be an empty line. At that case we don't want to add it to the values, because
                    # we join them with b' '.
                    line = line.strip()
                    if line:
                        value.append(line)
                    
                    # Update chunk data after _read_until_CRLF, because we want to check continuous.
                    if chunks:
                        chunk = chunks[0]
                        offset = self._offset
                    else:
                        if self._at_eof:
                            raise EOFError(b'')
                        
                        chunk = yield from self._wait_for_data()
                        offset = 0
                    
                    # If continuous, continue
                    if chunk[offset] in (b'\t'[0], b' '[0]):
                        continue
                    
                    # Not continuous, leave loop
                    value = b' '.join(value)
                    break
            
            # Store, nice!
            headers[name] = value.decode('utf-8', 'surrogateescape')
            
            # Find end again
            end = chunk.find(b'\r\n', offset)
            # If we found and we aren't at the end yet.
            if end > offset:
                middle = chunk.find(b':', offset, end)
                # New header line always must have b':', leave if not found, or if it is at the start.
                if middle <= offset:
                    raise PayloadError(f'Invalid header line: {chunk[offset:end]!r}.')
                
                name = chunk[offset:middle].lstrip().decode('utf-8', 'surrogateescape')
                value = chunk[middle + 1:end].strip()
                
                # Add 2 to the offset, to apply \r\n
                offset = end + 2
                # if we are at the end of the chunk, remove it and reset the offset
                if offset == len(chunk):
                    del chunks[0]
                    
                    if chunks:
                        chunk = chunks[0]
                    else:
                        if self._at_eof:
                            raise EOFError(b'')
                        
                        chunk = yield from self._wait_for_data()
                    
                    offset = 0
                continue
            
            # Next case, if we are at the end.
            if end == offset:
                # Update offset to include \r\n
                offset += 2
                # If we are at the of the chunk, remove it
                if offset == len(chunk):
                    del chunks[0]
                    offset = 0
                # Store new offset and return headers
                self._offset = offset
                return headers
            
            # Last case, no \r\n found.
            # If we are at the end of a chunk, ofc none was found.
            if len(chunk) == offset:
                # Go on the next chunk and try again.
                del chunks[0]
                if chunks:
                    chunk = chunks[0]
                else:
                    if self._at_eof:
                        raise EOFError(b'')
                    
                    chunk = yield from self._wait_for_data()
                
                offset = 0
                
                # No need to apply offset, because it is a completely new chunk.
                end = chunk.find(b'\r\n')
                # Best case scenario, if we found \r\n.
                if end > offset:
                    middle = chunk.find(b':', 0, end)
                    # middle must be found and cannot be first character either.
                    if middle <= 0:
                        raise PayloadError(f'Invalid header line: {chunk[offset:end]!r}.')
                    
                    name = chunk[:middle].lstrip().decode('utf-8', 'surrogateescape')
                    value = chunk[middle + 1:end].strip()
                    
                    #Apply offset and update chunk data if needed.
                    offset = end + 2
                    if offset == len(chunk):
                        del chunks[0]
                        if chunks:
                            chunk = chunks[0]
                        else:
                            if self._at_eof:
                                raise EOFError(b'')
                        
                            chunk = yield from self._wait_for_data()
                        
                        offset = 0
                    
                    continue
                
                # Second case, when we are at the end.
                elif end == offset:
                    # Increase offset by 2 to include \r\n
                    offset += 2
                    # If we are at the end remove the chunk and store offset, return
                    if offset == len(chunk):
                        del chunks[0]
                        offset = 0
                    
                    self._offset = offset
                    return headers
                
                # Last case, not at end an no line break at the current chunk
                else:
                    # Save offset and get a new line
                    self._offset = offset
                    line = yield from self._read_until_CRLF()
                    if not line:
                        # If the line is empty, we can leave.
                        # Offset and chunk state is updated by the _read_until_CRLF method already.
                        return headers
                    
                    # Find middle
                    middle = line.find(b':')
                    # if middle is not found or the first character is the middle, we have a bad line
                    if middle <= 0:
                        raise PayloadError(f'Invalid header line: {line!r}.')
                    
                    name = line[:middle].lstrip().decode('utf-8', 'surrogateescape')
                    value = line[middle + 1:].strip()
                    
                    # Update the current chunk and offset state
                    if chunks:
                        chunk = chunks[0]
                        offset = self._offset
                    else:
                        if self._at_eof:
                            raise EOFError(b'')
                        
                        chunk = yield from self._wait_for_data()
                        offset = 0
                    
                    continue
            # We are not at the end case
            else:
                # Store offset and read a line
                self._offset = offset
                line = yield from self._read_until_CRLF()
                # If the line is empty we leave.
                # Offset and chunk state is updated by the _read_until_CRLF method already.
                if not line:
                    return headers
                
                # Find the middle
                middle = line.find(b':')
                # If the middle was not found, or it is the first character, bad line
                if middle <= 0:
                    raise PayloadError(f'Invalid header line: {line!r}.')
                
                name = line[:middle].lstrip().decode('utf-8', 'surrogateescape')
                value = line[middle + 1:].strip()
                
                # Update the current chunk and offset state
                if chunks:
                    chunk = chunks[0]
                    offset = self._offset
                else:
                    if self._at_eof:
                        raise EOFError(b'')
                    
                    chunk = yield from self._wait_for_data()
                    offset = 0
                
                continue
            continue
    
    def _read_websocket_frame(self, is_client, max_size):
        """
        Payload reader task, which reads a websocket frame.
        
        This method is a generator.
        
        Returns
        -------
        frame : ``WebSocketFrame``
            The read websocket frame.
        
        Raises
        ------
        EofError
            Connection lost before a full frame was received.
        PayloadError
            Payload length over max size limit.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        head_1, head_2 = yield from self._read_exactly(2)
        
        if ((head_2 & 0b10000000) >> 7) == is_client:
            raise WebSocketProtocolError('Incorrect masking.')
        
        length = head_2 & 0b01111111
        
        if length == 126:
            data = yield from self._read_exactly(2)
            length, = UNPACK_LENGTH_2(data)
        elif length == 127:
            data = yield from self._read_exactly(8)
            length, = UNPACK_LENGTH_3(data)
        
        if (max_size is not None) and length > max_size:
            raise PayloadError(f'Payload length exceeds size limit ({length} > {max_size} bytes).')
        
        # Read the data.
        if is_client:
            data = yield from self._read_exactly(length)
        else:
            mask = yield from self._read_exactly(4)
            data = yield from self._read_exactly(length)
            data = apply_websocket_mask(mask,data)
        
        return WebSocketFrame._from_fields(data, head_1)
    
    
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
                    return self._read_chunked()
                else:
                    return self._read_chunked_encoded(decompressor)
            
            if (length is not None) and (length > 0):
                decompressor = get_decompressor_for(message.encoding)
                if decompressor is None:
                    return self._read_exactly(length)
                else:
                    return self._read_exactly_encoded(length, decompressor)
        
        if isinstance(message, RawRequestMessage) and (message.method == METHOD_CONNECT):
            message.upgraded = True
            return self._read_until_eof()
        
        if isinstance(message, RawResponseMessage) and message.status >= 199 and (length is None):
            if message.status == 204:
                return None
            
            if message.chunked:
                decompressor = get_decompressor_for(message.encoding)
                if decompressor is None:
                    return self._read_chunked()
                else:
                    return self._read_chunked_encoded(decompressor)
            
            return self._read_until_eof()
        
        return None
    
    
    def _read_chunked(self):
        """
        Payload reader task, what reads a chunked http message, till it ends.
        
        This method is a generator.
        
        Returns
        -------
        collected : `bytes`
        
        Raises
        ------
        ConnectionError
            Connection lost before enough data was received.
        PayloadError
            - Chunk size is not hexadecimal.
            - Chunk not ends with CRLF.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        collected = []
        while True:
            chunk_length = yield from self._read_until_CRLF()
            # strip chunk extension
            index = chunk_length.find(b';')
            if index != -1:
                chunk_length = chunk_length[:index]
            
            try:
                chunk_length = int(chunk_length, 16)
            except ValueError:
                raise PayloadError(
                    f'Not hexadecimal chunk size: {chunk_length!r}.'
                ) from None
            
            if chunk_length == 0:
                end = yield from self._read_exactly(2)
                if end != b'\r\n':
                    raise PayloadError(
                        f'Received chunk does not end with b\'\\r\\n\', instead with: {end}.'
                    )
                break
            
            chunk = yield from self._read_exactly(chunk_length)
            end = yield from self._read_exactly(2)
            if end != b'\r\n':
                raise PayloadError(
                    f'Received chunk does not end with b\'\\r\\n\', instead with: {end}.'
                )
            
            collected.append(chunk)
        
        return b''.join(collected)
    
    
    def _read_exactly_encoded(self, length, decompressor):
        """
        Payload reader task, what reads exactly `n` bytes from the protocol, then decompresses it with the given
        decompress object.
        
        This method is a generator.
        
        Parameters
        ----------
        length : `int`
            The amount of bytes to read.
        decompressor : `ZLIB_DECOMPRESSOR`, `BROTLI_DECOMPRESSOR`
            Decompressor used to decompress the data after receiving it.
        
        Returns
        -------
        collected : `bytes`
        
        Raises
        ------
        ValueError
            If `n` is given as a negative integer.
        EofError
            Connection lost before `n` bytes were received.
        PayloadError
            Cannot decompress a chunk.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        chunk = yield from self._read_exactly(length)
        try:
            return decompressor.decompress(chunk)
        except COMPRESSION_ERRORS:
            raise PayloadError('Cannot decompress chunk') from None
    
    
    def _read_chunked_encoded(self, decompressor):
        """
        Payload reader task, what reads a chunked http message, till it ends. After receiving a "chunk", decompresses
        it.
        
        This method is a generator.
        
        Parameters
        ----------
        decompressor : `zlib.decompressor`, `brotli.Decompressor`, `BROTLI_COMPRESSOR`
            Decompressor used to decompress the data after receiving it.
            
        Returns
        -------
        collected : `bytes`
        
        Raises
        ------
        ConnectionError
            Connection lost before enough data was received.
        PayloadError
            - Chunk size is not hexadecimal.
            - Chunk not ends with CRLF.
            - Cannot decompress a chunk.
        CancelledError
            If the reader task is cancelled not by receiving eof.
        """
        collected = []
        while True:
            chunk_length = yield from self._read_until_CRLF()
            # strip chunk extension
            index = chunk_length.find(b';')
            if index != -1:
                chunk_length = chunk_length[:index]
            
            try:
                chunk_length = int(chunk_length,16)
            except ValueError:
                raise PayloadError(
                    f'Not hexadecimal chunk size: {chunk_length!r}.'
                ) from None
            
            if chunk_length == 0:
                end = yield from self._read_exactly(2)
                if end != b'\r\n':
                    raise PayloadError(
                        f'Received chunk does not end with b\'\\r\\n\', instead with: {end}.'
                    )
                break
            
            chunk = yield from self._read_exactly(chunk_length)
            end = yield from self._read_exactly(2)
            if end != b'\r\n':
                raise PayloadError(
                    f'Received chunk does not end with b\'\\r\\n\', instead with: {end}.'
                )
            
            try:
                chunk = decompressor.decompress(chunk)
            except COMPRESSION_ERRORS:
                raise PayloadError('Cannot decompress chunk.') from None
            
            collected.append(chunk)
        
        return b''.join(collected)
    
    
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
        new._payload_waiter = self._payload_waiter
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
    _payload_waiter : `None` of ``Future``
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
            raise RuntimeError(f'Protocol has no attached transport; self={self!r}.')
        
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
    
    
    def write_websocket_frame(self, frame, is_client):
        """
        Writes a websocket frame to the protocol.
        
        Parameters
        ----------
        frame : ``WebSocketFrame``
            The websocket frame to write.
        is_client : `bool`
            Whether the respective websocket is client or server side.
        
        Raises
        ------
        RuntimeError
            Protocol has no attached transport.
        """
        transport = self._transport
        if transport is None:
            raise RuntimeError(f'Protocol has no attached transport; self = {self!r}.')
        
        # Prepare the header.
        head_1 = frame.head_1
        head_2 = is_client << 7
        
        length = len(frame.data)
        if length < 126:
            header = PACK_LENGTH_1(head_1, head_2 | length)
        elif length < 65536:
            header = PACK_LENGTH_2(head_1, head_2 | 126, length)
        else:
            header = PACK_LENGTH_3(head_1, head_2 | 127, length)
        transport.write(header)
        
        # prepare the data.
        if is_client:
            mask = getrandbits(32).to_bytes(4, 'big')
            transport.write(mask)
            data = apply_websocket_mask(mask, frame.data,)
        else:
            data = frame.data
        
        transport.write(data)

    
    @copy_docs(HttpReadProtocol.isekai_into)
    def isekai_into(self, other_class):
        new = HttpReadProtocol.isekai_into(self, other_class)
        
        new._drain_waiter = self._drain_waiter
        
        return new
