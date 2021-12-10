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
