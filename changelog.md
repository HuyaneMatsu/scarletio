## 1.0.41 *\[2022-09-13\]*

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
