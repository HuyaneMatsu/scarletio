__all__ = ('AsyncProcess',)

import sys
from socket import socketpair as create_socket_pair
from subprocess import PIPE, Popen, TimeoutExpired

from ..protocols_and_transports import ReadProtocolBase
from ..traps import Future, Task, TaskGroup, skip_poll_cycle

from .subprocess_protocols import SubprocessReadPipeProtocol, SubprocessWritePipeProtocol
from .subprocess_writer import SubprocessWriter


IS_AIX = sys.platform.startswith('aix')
LIMIT = 1 << 16
MAX_READ_SIZE = 262144

PROCESS_EXIT_DELAY_LIMIT = 10


class AsyncProcess:
    """
    Asynchronous process implementation.
    
    Attributes
    ----------
    _alive_file_descriptors : `list` if `int`
        A list of alive file descriptor's respective internal identifier.
        
        Can have the following elements:
        
        +-------------------+-------+
        | Respective name   | Value |
        +===================+=======+
        | stdin             | `0`   |
        +-------------------+-------+
        | stdout            | `1`   |
        +-------------------+-------+
        | stderr            | `2`   |
        +-------------------+-------+
    
    _connection_lost : `bool`
        Whether all the pipes of the ``AsyncProcess`` lost connection.
    _drain_waiter : `None`, ``Future``
        A future, what is used to block the writing task, till it's writen data is drained.
    _exit_waiters : `None`, `set of ``Future``
        Waiter futures which wait for the subprocess to shutdown.
    _extra : `dict` of (`str`, `object`) items
        Optional transport information.
    _loop : ``EventThread``
        the respective event loop of the async subprocess to what is bound to.
    _paused : `bool`
        Whether the subprocess is paused writing because it hit's the high water mark.
    _pending_calls : `None`, `list` of (`callable`, `tuple` of `object`)
        Meanwhile the subprocess connection is established, this attribute is set as a list to put connection lost
        and related calls it to with their parameters.
    _subprocess_stderr_protocol : `None`, ``SubprocessReadPipeProtocol``
        Protocol of the stderr pipe if applicable.
    _subprocess_stdin_protocol : `None`, ``SubprocessWritePipeProtocol``
        Protocol of the stdin pipe if applicable.
    _subprocess_stdout_protocol : `None`, ``SubprocessReadPipeProtocol``
        Protocol of the stdout pipe if applicable.
    _closed : `bool`
        Whether subprocess is closed.
    process : `subprocess.Process`
        The internal blocking subprocess object.
    process_id : `int`
        The subprocess identifier.
    return_code : `None`, `int`
        The returned exit code of the subprocess. Set as `None` if not yet applicable.
    stderr : ``ReadProtocolBase``
        Asynchronous stderr implementation.
    stdin : ``SubprocessWriter``
        Asynchronous stdin implementation.
    stdout : ``ReadProtocolBase``
        Asynchronous stdout implementation.
    """
    __slots__ = (
        '_alive_file_descriptors', '_closed', '_connection_lost', '_drain_waiter', '_exit_waiters', '_extra', '_loop',
        '_paused', '_pending_calls', '_subprocess_stderr_protocol', '_subprocess_stdin_protocol',
        '_subprocess_stdout_protocol', 'process', 'process_id', 'return_code', 'stderr', 'stdin', 'stdout'
    )
    
    async def __new__(
        cls, loop, process_parameters, shell, stdin, stdout, stderr, buffer_size, extra, process_open_kwargs
    ):
        """
        Creates a new ``AsyncProcess``.
        
        This method is a coroutine.
        
        Parameters
        ----------
        loop : ``EventThread``
            The event loop to what the async process is bound to.
        process_parameters : `tuple` of `object`
            Process parameters to open the subprocess with.
        shell : `bool
            Whether the specified command will be executed through the shell.
        stdin : `file-like`, `subprocess.PIPE`.
            Standard input for the created shell. Defaults to `subprocess.PIPE`.
        stdout : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`
            Standard output for the created shell.
        stderr : `file-like`, `subprocess.PIPE`, `subprocess.DEVNULL`, `subprocess.STDOUT`
            Standard error for the created shell.
        buffer_size : `int`
            Will be supplied as the corresponding parameter to the open() function when creating the
            stdin/stdout/stderr pipe file objects:
            
            Expected values:
            
            +---------------+-----------+-----------------------------------------------------------------------+
            | Name          | Value     | Description                                                           |
            +===============+===========+=======================================================================+
            | unbuffered    | `0`       | Read and write are one system call and can return short.              |
            +---------------+-----------+-----------------------------------------------------------------------+
            | line buffered | `1`       | Only usable if `universal_newlines = True`, for example in text mode. |
            +---------------+-----------+-----------------------------------------------------------------------+
            | buffer size   | `> 1`     | Use a buffer of approximately to that value.                          |
            +---------------+-----------+-----------------------------------------------------------------------+
            | default       | `< 0`     | use the system default: `io.DEFAULT_BUFFER_SIZE`.                     |
            +---------------+-----------+-----------------------------------------------------------------------+
            
        extra : `None`, `dict` of (`str`, `object`) items
            Optional transport information.
        process_open_kwargs : `dict` of (`str`, `object`) items
            Additional parameters to open the process with.
        
        Raises
        ------
        TypeError
            If `process_open_kwargs` contains unexpected key.
        """
        if stdin == PIPE:
            # Use a socket pair for stdin, since not all platforms support selecting read events on the write end of a
            # socket (which we use in order to detect closing of the other end).  Notably this is needed on AIX, and
            # works just fine on other platforms.
            stdin_r, stdin_w = create_socket_pair()
        else:
            stdin_r = stdin
            stdin_w = None
        
        process = None
        
        try:
            process = Popen(
                process_parameters,
                shell = shell,
                stdin = stdin_r,
                stdout = stdout,
                stderr = stderr,
                universal_newlines = False,
                bufsize = buffer_size,
                **process_open_kwargs,
            )
            
            if (stdin_w is not None):
                stdin_r.close()
                process.stdin = open(stdin_w.detach(), 'wb', buffering = buffer_size)
                stdin_w = None
        except:
            if (process is not None) and (process.poll() is None):
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            
            raise
        finally:
            if (stdin_w is not None):
                stdin_r.close()
                stdin_w.close()
        
        if extra is None:
            extra = {}
        
        extra['subprocess'] = process
        
        self = object.__new__(cls)
        self._extra = extra
        self._closed = False
        self._loop = loop
        self.process = process
        self.process_id = process.pid
        self.return_code = None
        self._exit_waiters = None
        self._pending_calls = []
        self._subprocess_stdin_protocol = None
        self._subprocess_stdout_protocol = None
        self._subprocess_stderr_protocol = None
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self._paused = False
        self._drain_waiter = None
        self._connection_lost = False
        self._alive_file_descriptors = []
        
        try:
            stdin = process.stdin
            if (stdin is not None):
                subprocess_stdin_protocol = SubprocessWritePipeProtocol(self, 0)
                await loop.connect_write_pipe(subprocess_stdin_protocol, stdin)
                self._subprocess_stdin_protocol = subprocess_stdin_protocol
                stdin_transport = subprocess_stdin_protocol.get_transport()
                if (stdin_transport is not None):
                    self.stdin = SubprocessWriter(loop, stdin_transport, self)
            
            stdout = process.stdout
            if (stdout is not None):
                subprocess_stdout_protocol = SubprocessReadPipeProtocol(self, 1)
                await loop.connect_read_pipe(subprocess_stdout_protocol, stdout)
                self._subprocess_stdout_protocol = subprocess_stdout_protocol
                stdout_transport = subprocess_stdout_protocol.get_transport()
                if (stdout_transport is not None):
                    self.stdout = stdout_protocol = ReadProtocolBase(loop)
                    stdout_protocol.connection_made(stdout_transport)
                    self._alive_file_descriptors.append(1)
            
            stderr = process.stderr
            if (stderr is not None):
                subprocess_stderr_protocol = SubprocessReadPipeProtocol(self, 2)
                await loop.connect_read_pipe(subprocess_stderr_protocol, stderr)
                self._subprocess_stderr_protocol = subprocess_stderr_protocol
                stderr_transport = subprocess_stderr_protocol.get_transport()
                if (stderr_transport is not None):
                    self.stderr = ReadProtocolBase(loop)
                    self.stderr.connection_made(stderr_transport)
                    self._alive_file_descriptors.append(2)
            
            for pending_call, args in self._pending_calls:
                pending_call(self, *args)
            
            self._pending_calls = None
        except:
            self.close()
            await self.wait()
            raise
        
        return self
    
    def __repr__(self):
        """Returns the async process's representation."""
        repr_parts = [
            '<',
            self.__class__.__name__,
        ]
        
        if self._closed:
            repr_parts.append(' closed')
            field_added = True
        else:
            field_added = False
        
        stdin = self.stdin
        if (stdin is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' stdin = ')
            repr_parts.append(repr(stdin))
        
        stdout = self.stdout
        if (stdout is not None):
            if field_added:
                repr_parts.append(',')
            else:
                field_added = True
            
            repr_parts.append(' stdout = ')
            repr_parts.append(repr(stdout))
        
        stderr = self.stderr
        if (stderr is not None):
            if field_added:
                repr_parts.append(',')
            
            repr_parts.append(' stderr = ')
            repr_parts.append(repr(stderr))
        
        repr_parts.append('>')
        return ''.join(repr_parts)
    
    
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
        return self._extra.get(name, default)
    
    
    def is_closing(self):
        """
        Returns whether the async process is closing.
        
        Returns
        -------
        is_closing : `bool`
        """
        return self._closed
    
    
    def close(self):
        """
        Starts the shutdown process of the async process.
        """
        if self._closed:
            return
        
        self._closed = True
        
        pipe_stdin = self._subprocess_stdin_protocol
        if (pipe_stdin is not None):
            pipe_stdin.close_transport()
        
        pipe_stdout = self._subprocess_stdout_protocol
        if (pipe_stdout is not None):
            pipe_stdout.close_transport()
        
        pipe_stderr = self._subprocess_stderr_protocol
        if (pipe_stderr is not None):
            pipe_stderr.close_transport()
        
        process = self.process
        if (process is not None):
            if (self.return_code is None) and (process.poll() is None):
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
        
        Task(self._loop, self._process_exited())
    
    __del__ = close
    
    def send_signal(self, signal):
        """
        Sends the signal to the child process.
        
        Parameters
        ----------
        signal : `int`
            The signal to send.
        
        Raises
        ------
        ProcessLookupError
            The underlying process is already dead.
        """
        process = self.process
        if process is None:
            raise ProcessLookupError()
        
        process.send_signal(signal)
    
    
    def terminate(self):
        """
        Stops the child process.
        
        Raises
        ------
        ProcessLookupError
            The underlying process is already dead.
        """
        process = self.process
        if process is None:
            raise ProcessLookupError()
        
        process.terminate()
    
    
    async def kill(self):
        """
        Kills the child process.
        
        This method is a coroutine.
        """
        process = self.process
        if process is None:
            return
        
        process.kill()
        
        self.close()
        
        await skip_poll_cycle(self._loop)
    
    
    def _pipe_connection_lost(self, file_descriptor, exception):
        """
        Called when a file descriptor of the subprocess lost connection.
        
        Calls ``._do_pipe_connection_lost`` or adds it as a callback if the process is still connecting.
        
        Parameters
        ----------
        file_descriptor : `int`
            File descriptor identifier.
            
            It's value can be any of the following:
            
            +-------------------+-------+
            | Respective name   | Value |
            +===================+=======+
            | stdin             | `0`   |
            +-------------------+-------+
            | stdout            | `1`   |
            +-------------------+-------+
            | stderr            | `2`   |
            +-------------------+-------+
        
        exception : `None`, `BaseException`
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        pending_calls = self._pending_calls
        if (pending_calls is None):
            self._do_pipe_connection_lost(file_descriptor, exception)
        else:
            pending_calls.append((self.__class__._do_pipe_connection_lost, (file_descriptor, exception)))
        
        self._try_finish()
    
    
    def _do_pipe_connection_lost(self, file_descriptor, exception):
        """
        Called by ``._pipe_connection_lost`` to call the pipe's connection lost method.
        
        Parameters
        ----------
        file_descriptor : `int`
            File descriptor identifier.
            
            It's value can be any of the following:
            
            +-------------------+-------+
            | Respective name   | Value |
            +===================+=======+
            | stdin             | `0`   |
            +-------------------+-------+
            | stdout            | `1`   |
            +-------------------+-------+
            | stderr            | `2`   |
            +-------------------+-------+
        
        exception : `None`, `BaseException`
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        if file_descriptor == 0:
            pipe = self.stdin
            if (pipe is not None):
                pipe.close()
            
            self._do_connection_lost(exception)
            return
        
        if file_descriptor == 1:
            reader = self.stdout
        elif file_descriptor == 2:
            reader = self.stderr
        else:
            reader = None
        
        if (reader is not None):
            reader.connection_lost(exception)
        
        try:
            self._alive_file_descriptors.remove(file_descriptor)
        except ValueError:
            pass
        
        self._maybe_process_exited()
    
    
    def _pipe_data_received(self, file_descriptor, data):
        """
        Called when one of the subprocess's pipe receives any data.
        
        Calls ``._do_pipe_data_received`` or adds it as a callback if the process is still connecting.
        
        Parameters
        ----------
        file_descriptor : `int`
            File descriptor identifier.
            
            It's value can be any of the following:
            
            +-------------------+-------+
            | Respective name   | Value |
            +===================+=======+
            | stdin             | `0`   |
            +-------------------+-------+
            | stdout            | `1`   |
            +-------------------+-------+
            | stderr            | `2`   |
            +-------------------+-------+
        
        data : `bytes`
            The received data.
        """
        pending_calls = self._pending_calls
        if (pending_calls is None):
            self._do_pipe_data_received(file_descriptor, data)
        else:
            pending_calls.append((self.__class__._do_pipe_data_received, (file_descriptor, data)))
    
    
    def _do_pipe_data_received(self, file_descriptor, data):
        """
        Called by ``._pipe_data_received`` to call the respective protocol' data received method.
        
        Parameters
        ----------
        file_descriptor : `int`
            File descriptor identifier.
            
            It's value can be any of the following:
            
            +-------------------+-------+
            | Respective name   | Value |
            +===================+=======+
            | stdin             | `0`   |
            +-------------------+-------+
            | stdout            | `1`   |
            +-------------------+-------+
            | stderr            | `2`   |
            +-------------------+-------+
        
        data : `bytes`
            The received data.
        """
        if file_descriptor == 1:
            reader = self.stdout
        elif file_descriptor == 2:
            reader = self.stderr
        else:
            return
        
        if (reader is not None):
            reader.data_received(data)
    
    
    async def _process_exited(self):
        """
        Task created by ``.close``to wait till the sub-process is closed and to set
        
        This method is a coroutine.
        """
        try:
            return_code = self.process.poll()
            if return_code is None:
                return_code = await self._loop.run_in_executor(self.process.wait)
            
            self.return_code = return_code
            
            self._try_finish()
            
            # wake up futures waiting for wait()
            exit_waiters = self._exit_waiters
            if (exit_waiters is not None):
                for waiter in self._exit_waiters:
                    if not waiter.is_cancelled():
                        waiter.set_result(return_code)
            
            self._exit_waiters = None
        finally:
            self.process = None
    
    
    def _maybe_process_exited(self):
        """
        Called when a sub-process pipe is closed. When all all pipe is closed, calls ``.close``.
        """
        if self._alive_file_descriptors:
            return
        
        self.close()
    
    
    async def wait(self, timeout = None):
        """
        Wait for child process to terminate.
        
        This method is a coroutine.
        
        Parameters
        ----------
        timeout : `None`, `float`
            The maximal amount of time to wait for the process to close in seconds.

        Returns
        -------
        return_code : `int`
            The return code of the subprocess.
        
        Raises
        ------
        TimeoutExpired
            If the process was not closed before timeout.
        """
        return_code = self.return_code
        if (return_code is not None):
            return return_code
        
        waiter = Future(self._loop)
        
        exit_waiters = self._exit_waiters
        if exit_waiters is None:
            self._exit_waiters = exit_waiters = set()
        
        exit_waiters.add(waiter)
        if (timeout is not None):
            waiter.apply_timeout(timeout)
        
        try:
            return await waiter
        except TimeoutError:
            exit_waiters.discard(waiter)
            
            process = self.process
            if process is None:
                args = None
            else:
                args = process.args
            
            raise TimeoutExpired(args, timeout) from None
    
    
    def _try_finish(self):
        """
        If the sub-process finished closing, calls ``._do_connection_lost``. If the process is still connecting, adds
        it as a callback instead.
        """
        if self.return_code is None:
            return
        
        stdin_protocol = self._subprocess_stdin_protocol
        if (stdin_protocol is None) or stdin_protocol._disconnected:
            return
        
        stdout_protocol = self._subprocess_stdout_protocol
        if (stdout_protocol is None) or stdout_protocol._disconnected:
            return
        
        stderr_protocol = self._subprocess_stderr_protocol
        if (stderr_protocol is None) or stderr_protocol._disconnected:
            return
        
        pending_calls = self._pending_calls
        if (pending_calls is None):
            self._do_connection_lost(None)
        else:
            pending_calls.append((self.__class__._do_connection_lost, (self, None,)))
    
    
    async def _feed_stdin(self, input_value):
        """
        Feeds the given data to ``.stdin``, waits till it drains and closes it.
        
        Used by ``.communicate``.
        
        This method is a coroutine.
        
        Parameters
        ----------
        input_value : `None`, `bytes-like`
            Optional data to be sent to the sub-process.
        """
        stdin = self.stdin
        if stdin is None:
            return
        
        if (input_value is not None):
            stdin.write(input_value)
        
        try:
            await stdin.drain()
        except (BrokenPipeError, ConnectionResetError):
            # communicate() ignores BrokenPipeError and ConnectionResetError
            pass
        
        stdin.close()
    
    
    async def _read_close_stdout_stream(self):
        """
        Reads every data from ``.stdout``. When reading is done, closes it.
        
        Used by ``.communicate``.
        
        This method is a coroutine.
        
        Returns
        -------
        result :`None`, `bytes`
        """
        stream = self.stdout
        if stream is None:
            return None
        
        transport = self._subprocess_stdout_protocol.get_transport()
        result = await stream.read()
        transport.close()
        return result
    
    
    async def _read_close_stderr_stream(self):
        """
        Reads every data from ``.stderr``. When reading is done, closes it.
        
        Used by ``.communicate``.
        
        This method is a coroutine.
        
        Returns
        -------
        result : `None`, `bytes`
        """
        stream = self.stderr
        if stream is None:
            return None
        
        transport = self._subprocess_stderr_protocol.get_transport()
        result = await stream.read()
        transport.close()
        return result
    
    
    async def communicate(self, input_value = None, timeout = None):
        """
        Sends data to stdin and reads data from stdout and stderr.
        
        Returns when the process is closed or raises when timeout occurs.
        
        This method is a coroutine.
        
        Parameters
        ----------
        input_value : `None`, `bytes-like` = `None` , Optional
            Optional data to be sent to the sub-process.
        timeout : `None`, `float` = `None`, Optional
            The maximal amount of time to wait for the process to close in seconds.
        
        Returns
        -------
        stdout : `None`, `bytes`
            The read data from stdout.
        stderr : `None`, `bytes`
            The read data from stderr.
        
        Raises
        ------
        TimeoutError
            If the process was not closed before timeout.
        """
        tasks = []
        
        loop = self._loop
        if input_value is None:
            stdin_task = None
        else:
            stdin_task = Task(loop, self._feed_stdin(input_value))
            tasks.append(stdin_task)
        
        if self.stdout is None:
            stdout_task = None
        else:
            stdout_task = Task(loop, self._read_close_stdout_stream())
            tasks.append(stdout_task)
        
        if self.stderr is None:
            stderr_task = None
        else:
            stderr_task = Task(loop, self._read_close_stderr_stream())
            tasks.append(stderr_task)
        
        if tasks:
            task_group = TaskGroup(loop, tasks)
            
            future = task_group.wait_all()
            if (timeout is not None):
                future.apply_timeout(timeout)
            
            try:
                await future
            except TimeoutError:
                # timeout occurred, cancel the read tasks and raise TimeoutExpired.
                task_group.cancel_pending()
                
                process = self.process
                if process is None:
                    args = None
                else:
                    args = process.args
                
                raise TimeoutExpired(args, timeout) from None
            
            except:
                task_group.cancel_all()
                raise
            
            if (stdin_task is not None):
                stdin_task.get_result()
            
            if (stdout_task is None):
                stdout = None
            else:
                stdout = stdout_task.get_result()
            
            if (stderr_task is None):
                stderr = None
            else:
                stderr = stderr_task.get_result()
        else:
            stdout = None
            stderr = None
        
        await self.wait()
        
        return stdout, stderr
    
    
    def poll(self):
        """
        Returns the subprocess' return code if terminated.
        
        Returns
        -------
        return_code : `None`, `int`
        """
        return self.return_code
    
    
    def pause_writing(self):
        """
        Called when the write transport's buffer goes over the high-water mark.
        
        ``.pause_writing`` is called when the write buffer goes over the high-water mark, and eventually
        ``.resume_writing`` is called when the write buffer size reaches the low-water mark.
        """
        self._paused = True
    
    
    def resume_writing(self):
        """
        Called when the transport's write buffer drains below the low-water mark.
        
        See ``.pause_writing`` for details.
        """
        self._paused = False
        
        drain_waiter = self._drain_waiter
        if drain_waiter is None:
            return
        
        self._drain_waiter = None
        drain_waiter.set_result_if_pending(None)
    
    
    def _do_connection_lost(self, exception):
        """
        Sets ``._connection_lost`` as `True` and set ``._drain_waiter`` result or exception as well.
        
        Parameters
        ----------
        exception : `None`, `BaseException`
            Defines whether the connection is closed, or an exception was received.
            
            If the connection was closed, then `exception` is given as `None`. This can happen at the case, when eof is
            received as well.
        """
        self._connection_lost = True
        # Wake up the writer if currently paused.
        if not self._paused:
            return
        
        drain_waiter = self._drain_waiter
        if drain_waiter is None:
            return
        
        self._drain_waiter = None
        if exception is None:
            drain_waiter.set_result_if_pending(None)
        else:
            drain_waiter.set_exception_if_pending(exception)
    
    
    async def _drain_helper(self):
        """
        Called when the transport buffer after writing goes over the high limit mark to wait till it is drained.
        
        This method is a coroutine.
        """
        if self._connection_lost:
            raise ConnectionResetError('Connection lost')
        
        if not self._paused:
            return
        
        self._drain_waiter = drain_waiter = Future(self)
        await drain_waiter
