# 1.0.68 *\[2024-03-18\]*

#### Improvements

- Add `FormData.__bool__`.
- `FormData.fields` is now a list of `FormDataField`.
- Add `FormData.add_json`.
- `FormData.__eq__` now has better support for `json` with the addition of `.add_json`.

# 1.0.67 *\[2024-03-14\]*

#### Improvements

- Add `CauseGroup.__eq__`.
- Add `CauseGroup.__new__`.
- Add `FormData.__eq__`.
- No `content length` / `tarnsfer encoding` headers are sent when we are not sending anything.
    Having these headers caused Discord's websocket to never read want we send to it (since yesterday night).

#### Bug fixes

- `WebSocketCommonProtocol.close_connection` did not handle `GeneratorExit` correctly.

#### Renames, Deprecation & Removals

- Rename `FormData` to `Formdata`. Old version is still a valid import for now.
- Deprecate `filename` parameter of `FormData.add_field` in favor of `file_name`.

# 1.0.66 *\[2024-02-28\]*

#### Bug fixes

- Fix some syntax errors failing to render (From 1.0.65).

# 1.0.65 *\[2024-02-03\]*

#### Improvements

- `WebSocketCommonProtocol` no longer swallows `CancelledError` at a few cases.
- `EditorAdvanced` now repeats write io polling if poll returns prematurely.
- Add new highlight tokens for trace rendering.
- Move `AttributeError` content generation from raise time to render time.
- Highlight `AttributeError` representation in rendering.
- Rich render rich builtin `AttributeError`-s too.

# 1.0.64 *\[2023-12-31\]*

#### Improvements

- Expressions are now also parsed backwards to better include where the exception occurred.
- If exception occurred in a multi-line expression add `around` word into the location.
- Frame filters now receive `1` parameter the frame or a virtual frame instead of 4 as before. Warning is dropped if
    `4` is given.
- Add tests to `utils.trace` and rewrite its internals. Top level imports are still the same, but internal imports
    changed. Wanted to also add new features but took too long.
- Yeet `linecache` import, implement smart line and file caching ourself instead.

# 1.0.63 *\[2023-11-11\]*

#### Improvements

- Improve content disposition header format.

#### Bug fixes

- `URL` now handles inheritance correctly.
- `asyncio.gather` did not silence all wrapped tasks' exception if multiple exception occurred or is going to occur.
- `EditorAdvanced` did not allow typing `~`. Caused by incorrect handing of the `delete` key which also contained `~`.

# 1.0.62 *\[2023-08-21\]*

#### Improvements

- `Future.__repr__` now will show a new `cancellation_exception` option field if cancelled with a custom exception.
- Add cli entry point.

#### Bug fixes

- Interactive console got stuck when `StopIteration` was raised into it.
- `Task.__repr__` showed bare `CancelledError()`.
- In `Future.__repr__` `result~raise` state had priority over `cancelled`.

# 1.0.61 *\[2023-08-19\]*

#### Improvements

- `Future`-s now can have multiple states.
- Add `Future.silence` to silence cleanup warnings. This replaces the old `.__silence__` method.
- Add `Future.is_silenced`.
- Add `InvalidStateError.__eq__`.
- Add `InvalidStateError.__hash__`.
- Add keyword parameter support to `InvalidStateError.__new__`.
- Add `Future.is_cancelling`.
- Disable `Task.set_exception` and `.set_exception_if_pending`. Add `Future.cancel_with` instead.
- Add `FutureWrapperSync.cancel_with`.
- Add `FutureWrapperSync.is_cancelling`.
- Add `FutureWrapperAsync.cancel_with`.
- Add `FutureWrapperAsync.is_cancelling`.
- Add `FutureWrapperBase`.
- `FutureWrapperAsync.wait` now waits till the future is cancelled when propagating cancellation.
- `FutureWrapperSync.wait` now waits till the future is cancelled when propagating cancellation.
- `FutureWrapperAsync.wait_till_completion` now waits till the future is cancelled when propagating cancellation.
- `FutureWrapperSync.wait_till_completion` now waits till the future is cancelled when propagating cancellation.
- `Future.get_exception` no longer raises `CancelledError`. Instead returns it.
- `TimeoutError` caused by `Task.apply_timeout` now will include the cancellation exception as cause.
- Add `Future.get_cancellation_exception`.
- `FutureWrapperAsync.wait` now includes cancellation exception in the traceback.
- `FutureWrapperSync.wait` now includes cancellation exception in the traceback.
- `FutureWrapperAsync.wait_till_completion` now includes cancellation exception in the traceback.
- `FutureWrapperSync.wait_till_completion` now includes cancellation exception in the traceback.
- Add `AutoCompleter` for interactive console editors to use.
- `EditorAdvanced` supports auto completion.
- Add `FutureBaseWrapper.get_cancellation_exception`.

#### Bug fixes

- `FutureAsyncWrapper` re-implemented slots, allocating more memory as required (This is actually a python bug).
- Timeout dropped `TimeoutError` into the cancelled task instead of `CancelledError`.

#### Renames, Deprecation & Removals

- Deprecate `FutureAsyncWrapper.__call__`. It resets the future which should not happen.
- Remove `Gatherer`.
- Remove `ResultGatheringFuture`.
- Remove `WaitContinuously`.
- Remove `WaitTillAll`.
- Remove `WaitTillExc`.
- Remove `WaitTillFirst`.
- Remove `FutureSyncWrapper.__call__`.
- Remove `FutureAsyncWrapper.__call__`.
- Rename `EventThread.call_later` to `.call_after`.
- Rename `EventThread.call_later_weak` to `.call_after_weak`.
- Deprecate `EventThread.call_later`.
- Deprecate `EventThread.call_later_weak`.
- Rename `FutureSyncWrapper` to `FutureWrapperSync`.
- Rename `FutureAsyncWrapper` to `FutureWrapperAsync`.
- Deprecate `FutureSyncWrapper`.
- Deprecate `FutureAsyncWrapper`.

## 1.0.60 *\[2023-08-10\]*

#### Improvements

##### ext.asyncio
- Implement `Condition`.

## 1.0.59 *\[2023-07-28\]*

#### Bug fixes

- It could happen that the interactive console did not have builtins(?).

## 1.0.58 *\[2023-07-28\]*

#### Improvements

##### ext.asyncio
- `current_task` return improved with `weakref`, `eq`, `is`, `hash` to fix errors coming from anyio.

## 1.0.57 *\[2023-07-28\]*

#### Bug fixes

- When using `raise ... from None` exception context is no longer shown.

## 1.0.56 *\[2023-06-13\]*

#### Improvements

- Add `ExecutorThread.get_stack`.
- Add `ExecutorThread.print_stack`.
- Add `ExecutorThread.current_function`.
- Add `ExecutorThread.__repr__`.
- Add `get_or_create_event_loop`.

#### Bug fixes

- `repeat_timeout` no longer marks the task as done with exception.

#### Renames, Deprecation & Removals

- Reverse `Task` parameters from `(coroutine, loop)` to `(loop, coroutine)`, so it matched other constructors in order.
- Deprecate `Future.result`.
- Deprecate `Future.exception`.
- Set due date to `Future.pending`'s deprecation.
- Set due date to `Future.done`'s deprecation.
- Set due date to `Future.cancelled`'s deprecation.

## 1.0.55 *\[2023-03-24\]*

#### Improvements

- Add `EventThread.socket_receive_into`.
- Add `Reference` type.
- Add `CoroutineFunctionTypeProxy`.
- Add `CoroutineTypeProxy`.

#### Bug fixes

- Fix `WebSocketServer.close` dropped `AttributeError`. (from `1.0.54` probably)
- Fix race condition in `EventThread.socket_connect` and in other `.socket_...` methods.
- Tasks waiting on a `TaskGroup`'s waiter could be garbage collected prematurely.

## 1.0.54 *\[2023-03-02\]*

#### Improvements

- Add `TaskGroup.iter_futures`.
- Add `Handle.iter_positional_parameters`.
- Add `Future.iter_callbacks`.
- `EventThread.get_tasks` now handles `TaskGroup`-s as intended.
- Stop using features that were deprecated at ˙1.0.51˙.
- Add `TaskGroup.wait_exception_or_cancellation`.
- Add `TaskGroup.wait_exception_or_cancellation_and_pop`.

##### ext.asyncio
- Update `gather`, `complete_as`, `wait` to match asyncio's behavior more.

## 1.0.53 *\[2023-02-05\]*

#### Improvements

- Add `FutureSyncWrapper.wait_for_completion`.

#### Bug fixes

- `enter_executor` dropped `AttributeError` (Gilgamesh#8939) (From `1.0.51`).

## 1.0.52 *\[2023-02-03\]*

#### Bug fixes

- `CompoundMetaType` did not respect property-like custom descriptors as intended.

## 1.0.51 *\[2023-01-22\]*

#### Improvements

- Add `TaskGroup`.
- Add `Future.apply_timeout` replacing `future_or_timeout` function.

#### Bug fixes

- `Future.__repr__` did not render correctly if the future result was not yet retrieved.

#### Renames, Deprecation & Removals

- Deprecate `Gatherer`.
- Deprecate `ResultGatheringFuture`.
- Deprecate `WaitContinuously`.
- Deprecate `WaitTillAll`.
- Deprecate `WaitTillExc`.
- Deprecate `WaitTillFirst`.
- Deprecate `future_or_timeout`.
- Deprecate `Future.clear` in favor of keeping future life cycle flow.

## 1.0.50 *\[2023-01-14\]*

#### Improvements

- `Future.wait_for_completion` will not propagate future exception. (It was never intended.)
- Task stepping speed improved.

## 1.0.49 *\[2022-12-12\]*

#### Bug fixes

- Interactive console crashed when pressing `home` at index `0`.

## 1.0.48 *\[2022-12-07\]*

#### Bug fixes

### ext.asyncio

- `run` was using an incorrect way of detecting created event loops.

## 1.0.47 *\[2022-11-21\]*

#### Bug fixes

- `collect_module_variables` could raise when module variables are broken.

## 1.0.46 *\[2022-11-21\]*

#### Improvements

- Add `get_frame_module`.
- `collect_module_variables` now handles non-packages as well.

#### Renames, Deprecation & Removals

- Rename `collect_package_local_variables` to `collect_module_variables`.
- Deprecate `collect_package_local_variables`.

## 1.0.45 *\[2022-11-13\]*

#### Improvements

- Support `HOME` key in the interactive console.
- Support `END` key in the interactive console.

## 1.0.44 *\[2022-11-11\]*

#### Improvements

- Add `include_with_callback`.
- Add `RichAttributeErrorBaseType` now handles the case correctly when the object indeed has the attribute.

## 1.0.43 *\[2022-10-25\]*

#### Bug fixes

- Html highlighter formatter will now prefer linebreak token conversion over other tokens.

## 1.0.42 *\[2022-09-28\]*

- Add `CauseGroup`.

#### Bug fixes

- Fix: When long data is read by the editor to redirect, it is chunked to multiple parts. If the chunk is at the
    middle of a line, it will break the output.
- Fix a case when editor redirection failed at partially duped unicodes.

## 1.0.41 *\[2022-09-21\]*

#### Bug fixes

- Highlighter now removes empty strings from "lines". Keeping them could cause incorrect line break amount.

## 1.0.40 *\[2022-09-13\]*

#### Bug fixes

- Highlighting returned incorrect output on line-ending back-slash characters. (Gilgamesh#8939)
- Editor could skip new-line prefix when the line was empty. (Showed up by fixing previous bug.)
- Highlighter built multi-line format strings with too much internal linebreaks.
- Highlighting returned incorrect output on escaped non-closed format strings.

## 1.0.39 *\[2022-09-08\]*

#### Bug fixes

- `ExceptionWriterContextManager._create_location_message_from_tracing` dropped `TypeError`. (Gilgamesh#8939)
- Highlighter could not render linebreaks after specific tokens.

## 1.0.38 *\[2022-09-08\]*

#### Bug fixes

- The editor cursor after moving back to 0th position showed up visually at 1st.
- 0 length string highlights were broken. (Gilgamesh#8939)

## 1.0.37 *\[2022-09-07\]*

#### Bug fixes

- Editor line breaking was not working as expected. (Gilgamesh#8939)
- Editor `in [n]` command had lower priority than compiling.
- Edit prefix length was incorrectly calculated.

## 1.0.36 *\[2022-09-03\]*

#### Improvements

- Add `ExceptionWriterContextmanager` with `catching` shortcut.
- Make `write_exception_sync` directly importable.
- Add more traceback highlight options. (This also means some changed)
- `before` and `after` parameters when writing a traceback are now also highlighted.
- `Future.__repr__` now wont contain the full exception representation if too long.
- Update `format_coroutine` function to produce shorter representation.
- Replace default exception hooks.

## 1.0.35 *\[2022-08-26\]*

#### Improvements

- `EditorAdvanced` now ignores the pasted console prefixes.
- Highlighter now handles not only the default console prefix.

## 1.0.34 *\[2022-08-23\]*

#### Improvements

- Add `Executor.get_used_executor_count`.
- Add `Executor.get_free_executor_count`.
- Add `Executor.get_total_executor_count`.
- `Executor` now auto adjusts it's executor count.
- Fix a slow loop in `EventThread.runner` caused by ignoring continuously queued callbacks.
- Fix a slow loop in `EventThread.run_in_executor` caused by not adjusting kept executor count.

#### Renames, Deprecation & Removals

- Deprecate `keep_executor_count` parameter everywhere.
- Deprecate `Executor.used_executor_count`. Please use `.get_used_executor_count()` instead.
- Deprecate `Executor.free_executor_count`. Please use `.get_free_executor_count()` instead.

## 1.0.33 *\[2022-08-18\]*

#### Improvements

- Handle io race condition when invoking `EditorAdvanced` within interactive console.
- Improve `repr(Task)` with updating `format_coroutine` function.
- Add `Future.get_result` and `Future.get_exception` and to related types as well in favor of moving away from
    `.result` and `.exception`, as they not intuitive.

## 1.0.32 *\[2022-08-13\]*

#### Improvements

- Add code highlighting support.
- Add `highlighter` parameter for `render_frames_into`, `render_exception` into.
- Repeated exception frames are now grouped.
- Add `render_frames_into_async`.
- Add `render_exception_into_async`.
- Add `write_exception_async`.
- Add `write_exception_maybe_async`.
- `Task.get_stack` now supports async generator correctly.
- Add `write_exception_async`.
- Add `set_default_trace_writer_highlighter`.
- Add `set_trace_writer_highlighter`.
- Add `get_default_trace_writer_highlighter`.
- Render syntax errors correctly.
- Handle syntax errors correctly in console.
- Highlight consoles too!

#### Bug fixes

- `EventThread._accept_connection_task` now handles task cancellation correctly.
- `WebSocketServerProtocol.lifetime_handler` now handles task cancellation correctly.
- `WebSocketServerProtocol.handshake` now handles task cancellation correctly.
- `WebSocketCommonProtocol.transfer_data` now handles task cancellation correctly.
- `to_coroutine` dropped error on `python3.11`.

### ext.asyncio

- `EventThread.call_exception_handler` wanted to render exception traceback when there was no exception.

#### Renames, Deprecation & Removals

- Deprecate `EventThread.render_exception_async`, use `write_exception_async` instead.
- Deprecate `EventThread.render_exception_maybe_async`, use `write_exception_maybe_async` instead.

## 1.0.31 *\[2022-07-24\]*

#### Improvements

- Frame accesses are now normalized with a proxy type.
- `format_coroutine` now handles coroutine generators as expected.
- `format_coroutine` now handles running states as expected.
- Multiline expressions now show up correctly in tracebacks.

## 1.0.30 *\[2022-07-19\]*

#### Improvements

- `AsynchronousInteractiveConsole` wont show internal frames anymore when an exception traceback is shown.

## 1.0.29 *\[2022-07-02\]*

#### Improvements

- Add `is_generator_function`.
- Add `is_generator`.

#### Bug fixes

- Compound built types had a few internal attributes badly assigned.
- `is_coroutine` could return incorrect value.
- `is_awaitable` could return incorrect value.

## 1.0.28 *\[2022-06-27\]*

#### Improvements

- Add `CallableAnalyzer.__mod__`.
- Add `CallableAnalyzer.__eq__`.
- Add `Parameter.__eq__`.
- Add `CallableAnalyzer.iter_non_reserved_parameters`.
- Add `Compound`.
- Add `CompoundTypeMetaType`.
- Add `Theory`.

#### Bug fixes

- Fix infinite recursion in `_HandleCancellerBase.__repr__` caused by circular reference.

## 1.0.27 *\[2022-05-17\]*

#### Improvements

- `to_json` now accepts enums.

## 1.0.26 *\[2022-04-24\]*

#### Bug fixes

- `SyncQueue.copy` raised `AttributeError`. (WizzyGeek#2356)

## 1.0.25  *\[2022-04-23\]*

#### Improvements

- Add `get_last_module_frame`.

## 1.0.24 *\[2022-04-18\]*

#### Improvements

- Add `stop_on_interruption` parameter to `run_asynchronous_interactive_console`.
- Add `stop_on_interruption` parameter to `AsynchronousInteractiveConsole`.

## 1.0.23 *\[2022-04-07\]*

#### Improvements

- Ignore raising `RichAttributeErrorBaseType.__getattr__` frames when rending exception traceback.

#### Bug fixes

- `FutureSyncWrapper._future` can be nulled, meaning it's loop could also be nulled.

## 1.0.22 *\[2022-03-31\]*

#### Bug fixes

- Importing just `.websocket` didn't resolve `.http_client` causing `NotImplementedError` runtime. (Sube#0880)
- `include` could fail when including a not yet resolved reference to a non-module file.

## 1.0.21 *\[2022-03-26\]*

#### Bug fixes

- `create_event_loop` didn't set event loop correctly (typo).

## 1.0.20 *\[2022-03-15\]*

#### Bug fixes

- Not yet started event loops were undetectable by `get_event_loop` causing `RuntimeError`. Set them at
`create_event_loop` if applicable.

## 1.0.19 *\[2022-03-08\]*

#### Bug fixes

##### ext.asyncio

- Add missing `EventThread.remove_signal_handler`. (Forest#2913)
- Add missing `EventThread.shutdown_asyncgens`. (Forest#2913)

## 1.0.18 *\[2022-02-28\]*

#### Improvements

- Add missing `_HandleCancellerBase.__repr__`.
- Add `filter` parameter to `render_exception_into`.
- Add `filter` parameter to `render_frames_into`.
- Add `line_number` parameter to `should_ignore_frame` (deprecate 3 parameter version).
- Add `filter` parameter to `should_ignore_frame`.

## 1.0.17 *\[2022-02-15\]*

#### Improvements
- Add missing `RawMessage.__new__`.
- Add missing `RawMessage.__repr__`.
- Add missing `RawResponseMessage.__repr__`.
- Add missing `RawRequestMessage.__repr__`.
- Stop trying to read `head` request response's body.

## 1.0.16 *\[2022-02-12\]*

#### Bug fixes

- Http version 1.0 connections could be closed too early.

## 1.0.15 *\[2022-02-12\]*

#### Bug fixes

- Http version 1.0 connections were not closed by default.

## 1.0.14 *\[2022-02-11\]*

#### Bug fixes

- `Timeout.__enter__` could raise `AttributeError` (typo). (winwinwinwin#0001)

## 1.0.13 *\[2022-02-10\]*

#### Improvements

- Add `CallableAnalyzer.get_parameter`.
- Add `CallableAnalyzer.has_parameter`.
- Add `set_event_loop`.
- State the future's state's name in `InvalidStateError.__repr__`.

## 1.0.12 *\[2022-02-09\]*

#### Improvements

- Add `ext.asyncio`.

## 1.0.11 *\[2022-02-08\]*

#### Improvements

- Add `__main__` file to scarletio. It starts an interactive console.
- `sleep` now calls `get_event_loop` instead of `current_thread`. Ths change improves event loop resolution.
- Add `scarletio.tools.asynchronous_interactive_console` for brave people.
- Add `get_current_task`.
- Add `get_tasks`.
- Add `loop` parameter to `create_future`.
- Add `loop` parameter to `create_task`.
- Add `run_coroutine`. (Name by `asleep-cult`).
- Add `skip_poll_cycle`.

## 1.0.10 *\[2022-01-29\]*

#### Bug fixes

- `HttpReadProtocol.get_payload_reader_task` should return `None` if status is 204.

## 1.0.9 *\[2022-01-25\]*

- Add `is_iterable`.
- Add `WeakSet`.
- Add `Future.wait_for_completion`.
- Add missing `WeakMap.update`.
- Add `is_hashable`.
- Add `MultiValueDictionary.popitem`.

#### Bug fixes

- `WeakMap.__getitem__` returned incorrect value.
- `WeakItemDictionary.copy` didn't set all attributes.
- `WeakKeyDictionary.copy` didn't set all attributes.
- `WeakValueDictionary.copy` didn't set all attributes.
- `_MultiValueDictionaryItemIterator.__contains__` returned incorrect value.
- `MultiValueDictionary.__init__` could add the same item multiple times.
- `IgnoreCaseMultiValueDictionary.__init__` could add the same item multiple times.

## 1.0.8 *\[2022-01-04\]*

#### Bug fixes

- `EventThread.get_tasks` could drop `AttributeError`.
- Fix a `TypeError` in `quote`.

## 1.0.7 *\[2021-12-26\]*

#### Bug fixes

- `RichAttributeErrorBaseType.__getattr__` now will not drop recursion error when python calls
    `getattr(instance, '__dict__')` from `object.__dir__(instance)`.

## 1.0.6 *\[2021-12-10\]*

#### Improvements

- Add `EventThread.get_tasks`

## 1.0.5 *\[2021-12-07\]*

#### Bug fixes

- `RichAttributeErrorBaseType.__getattr__` now will not drop recursion error at some edge cases.

## 1.0.4 *\[2021-12-07\]*

#### Improvements

- Add `CallableAnalyzer.get_non_reserved_keyword_only_parameters`.

## 1.0.3 *\[2021-12-05\]*

#### Improvements

- `RichAttributeErrorBaseType.__getattr__` will not cache, if the object has dynamic `__getattr__`.

#### Bug fixes

- Fix a `NameError` on windows only.
