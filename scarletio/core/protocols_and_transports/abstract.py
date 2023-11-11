__all__ = ('AbstractBidirectionalTransportLayerBase', 'AbstractProtocolBase', 'AbstractTransportLayerBase', )

class AbstractTransportLayerBase:
    """
    Defines abstract transport layer functionality.
    """
    __slots__ = ()
    
    
    def get_extra_info(self, name, default = None):
        """
        Gets optional transport information.
        
        Parameters
        ----------
        name : `str`
            The extra information's name to get.
        default : `object`, `None`, Optional
            Default value to return if `name` could not be matched. Defaults to `None`.
        
        Returns
        -------
        info : `default`, `object`
        """
        return default
    
    
    def get_protocol(self):
        """
        Gets the transport's actual protocol.
        
        Returns
        -------
        protocol : `None`, ``ProtocolBase``
            Asynchronous protocol implementation.
        """
        return None
    
    
    def set_protocol(self, protocol):
        """
        Sets a new protocol to the transport.
        
        Parameters
        ----------
        protocol : ``ProtocolBase``
            Asynchronous protocol implementation.
        """
        pass
    
    
    def is_closing(self):
        """
        Returns whether the transport is closing.
        
        Returns
        -------
        is_closing : `bool`
        """
        return True

    
    def close(self):
        """
        Starts the shutdown process of the transport.
        
        If the transport is already closing, does nothing.
        """
        pass
    
    
    def abort(self):
        """
        Closes the transport immediately.
        
        The buffered data will be lost.
        """
        pass
    
    
    def write(self, data):
        """
        Write the given `data` to the transport.
        
        Do not blocks, but queues up the data instead to be sent as can.
        
        Parameters
        ----------
        data : `bytes-like`
            The data to send.
        
        Raises
        ------
        TypeError
            If `data` was not given as `bytes-like`.
        RuntimeError : `bool`
            If ``.write_eof`` was already called.
        """
        pass
    
    
    def writelines(self, lines):
        """
        Writes the given lines to the transport's socket.
        
        Parameters
        ----------
        lines : `iterable` of `bytes-like`
            The lines to write.
        
        Raises
        ------
        RuntimeError
            Protocol has no attached transport.
        """
        self.write(b''.join(lines))
    
    
    def write_eof(self):
        """
        Writes eof to the subprocess pipe's transport's protocol if applicable.
        
        By default ``SubprocessStreamWriter``'s transport is ``UnixWritePipeTransport``, what will call connection lost
        as well when the write buffer is empty.
        """
        pass
    
    
    def can_write_eof(self):
        """
        Return whether the transport supports ``.write_eof``.
        
        Returns
        -------
        can_write_eof : `bool`
        """
        return False
    
    
    def get_write_buffer_size(self):
        """
        Return the current size of the write buffer.
        
        Returns
        -------
        get_write_buffer_size : `int`
        """
        return 0
    
    
    def get_write_buffer_limits(self):
        """
        Returns the low and the high water of the transport.
        
        Returns
        -------
        low_water : `int`
            The ``.protocol`` is resumed writing when the buffer size goes under the low water mark. Defaults to
            `16384`.
        high_water : `int`
            The ``.protocol`` is paused writing when the buffer size passes the high water mark. Defaults to
            `65536`.
        """
        return 0, 0
    
    
    def set_write_buffer_limits(self, high = None, low = None):
        """
        Set the high- and low-water limits for write flow control.
        
        These two values control when to call the protocol's ``.pause_writing`` and ``.resume_writing`` methods. If
        specified, the low-water limit must be less than or equal to the high-water limit. Neither value can be
        negative. The defaults are implementation-specific. If only the high-water limit is given, the low-water limit
        defaults to an implementation-specific value less than or equal to the high-water limit. Setting high to zero
        forces low to zero as well, and causes ``.pause_writing`` to be called whenever the buffer becomes non-empty.
        Setting low to zero causes ``.resume_writing`` to be called only once the buffer is empty. Use of zero for
        either limit is generally sub-optimal as it reduces opportunities for doing I/O and computation concurrently.
        
        Parameters
        ----------
        high : `None`, `int` = `None`, Optional
            High limit to stop reading if reached.
        low : `None`, `int` = `None`, Optional
            Low limit to start reading if reached.
        
        Raises
        ------
        ValueError
            If `low` is lower than `0` or if `low` is higher than `high`.
        """
        pass
    
    
    def pause_reading(self):
        """
        Pauses the receiving end.
        
        No data will be passed to the respective protocol's ``.data_received`` method until ``.resume_reading`` is
        called.
        
        Returns
        -------
        reading_paused : `bool`
            Whether reading was paused.
        """
        return False
    
    
    def resume_reading(self):
        """
        Resumes the receiving end.
        
        Data received will once again be passed to the respective protocol's ``.data_received`` method.
        
        Returns
        -------
        reading_resumed : `bool`
            Whether reading was resumed.
        """
        return False


class AbstractProtocolBase:
    """
    Defines abstract protocol functionality.
    
    Structure
    ---------
    All protocol should implement the following methods:
    - ``.connection_made``
    - ``.connection_lost``
    - ``.close``
    - ``.close_transport``
    - ``.get_transport``
    - ``.get_extra_info``
    
    Read protocols should implement the following:
    - ``.set_exception``
    - ``.eof_received``
    - ``.data_received``
    
    Write protocols should implement the following:
    - ``.pause_writing``
    - ``.resume_writing``
    - ``.write``
    - ``.writelines``
    - ``.write_eof``
    - ``.can_write_eof``
    - ``.drain``
    
    Datagram protocols should implement the following:
    - ``.datagram_received``
    - ``.error_received``
    """
    __slots__ = ()
    
    def connection_made(self, transport):
        """
        Called when a connection is made.
        
        Parameters
        ----------
        transport : `object`
            Asynchronous transport implementation, what calls the protocol's ``.data_received`` when data is
            received.
        """
        pass
    
    
    def connection_lost(self, exception):
        """
        Called when the connection is lost or closed.
        
        Parameters
        ----------
        exception : `None`, `BaseException`
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        pass
    
    
    def close(self):
        """
        Closes the protocol by closing it's transport if applicable.
        """
        pass
    
    
    def close_transport(self, force = False):
        """
        Starts the shutdown process of the protocol's transport if applicable.
        
        Parameters
        ----------
        force : `bool`
            Whether the transport should be shut down immediately.
        """
        transport = self.get_transport()
        if (transport is not None):
            transport.close()
            
            if force:
                transport.abort()
    
    
    def get_transport(self):
        """
        Returns the transport layer of the protocol.
        
        Returns
        -------
        transport : `None`, ``AbstractTransportLayerBase``
        """
        pass
    
    
    def get_extra_info(self, name, default = None):
        """
        Gets optional transport information.
        
        Parameters
        ----------
        name : `str`
            The extra information's name to get.
        default : `object` = `None`, Optional
            Default value to return if `name` could not be matched. Defaults to `None`.
        
        Returns
        -------
        info : `default`, `object`
        """
        return default
    
    
    def set_exception(self, exception):
        """
        Called by ``.connection_lost`` if the connection is closed by an exception, or can be called if any method
        of the protocol raises an unexpected exception.
        
        Parameters
        ----------
        exception : `BaseException`
        """
        pass
    
    
    def eof_received(self):
        """
        Calling ``.connection_lost`` without exception causes eof.
        
        Marks the protocol as it is at eof and stops payload processing if applicable.
        
        Returns
        -------
        transport_closes : `bool`
            Returns `False` if the transport will close itself. If it returns `True`, then closing the transport is up
            to the protocol.
            
            Always returns `False`.
        """
        pass
    
    
    def data_received(self, data):
        """
        Called when some data is received.
        
        Parameters
        ----------
        data : `bytes`
            The received data.
        """
        pass
    
    
    def pause_writing(self):
        """
        Called when the transport's buffer goes over the high-water mark.
        
        ``.pause_writing`` is called when the buffer goes over the high-water mark, and eventually
        ``.resume_writing`` is called when the buffer size reaches the low-water mark.
        """
        pass
    
    
    def resume_writing(self):
        """
        Called when the transport's buffer drains below the low-water mark.
        
        See ``.pause_writing`` for details.
        """
        pass
    
    
    def write(self, data):
        """
        Writes the given data to the protocol's transport.
        
        Parameters
        ----------
        data : `bytes-like`
            The data to write.
        
        Raises
        ------
        RuntimeError
            Protocol has no attached transport.
        """
        pass
    
    
    def writelines(self, lines):
        """
        Writes the given lines to the protocol's transport.
        
        Parameters
        ----------
        lines : `iterable` of `bytes-like`
            The lines to write.
        
        Raises
        ------
        RuntimeError
            Protocol has no attached transport.
        """
        pass
    
    
    def write_eof(self):
        """
        Writes eof to the transport's protocol if applicable.
        """
        pass
    
    
    def can_write_eof(self):
        """
        Returns whether ``.write_eof`` will write eof successfully.
        
        Returns
        -------
        can_write_eof : `bool`
        """
        pass
    
    
    async def drain(self):
        """
        Blocks till the write buffer is drained.
        
        This method is a coroutine.
        
        Raises
        ------
        BaseException
            Connection lost exception if applicable.
        """
        pass
    
    
    def datagram_received(self, data, address):
        """
        Called when some datagram is received.
        
        Parameters
        ----------
        data : `bytes`
            The received data.
        address : `tuple` (`str`, `int`)
            The address from where the data was received.
        """
        pass
    
    
    def error_received(self, exception):
        """
        Called when a send or receive operation raises an `OSError`, but not `BlockingIOError`, nor `InterruptedError`.
        
        Parameters
        ----------
        exception : `OSError`
            The catched exception.
        """
        pass


class AbstractBidirectionalTransportLayerBase(AbstractTransportLayerBase, AbstractProtocolBase):
    """
    Defines abstract bidirectional transport layer functionality.
    """
    __slots__ = ()
