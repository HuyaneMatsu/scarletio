## 1.0.25  *\[2022-04-23\]*

- Add `get_last_module_frame`.

## 1.0.24 *\[2022-04-18\]*

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
