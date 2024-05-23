This is the styleguide followed by scarletio.

The rules of this style guide are not written in stone, as scarletio evolves this style guide changes as well.

Some old code might not follow it, but that's the beauty of it. Improve, adapt, overcome.

This style guide is here to make the project's formatting consistent and readable.

## Indentation

4 Spaces.

### Continuation lines

Continuation lines should align wrapped elements by exactly 1 indentation starting in the next line.
The closing bracket should be on the same level as the expression's start.

```py
# Wrong:
# Aligned with opening delimiter.
foo = long_function_name(vairbale_0, vairbale_1,
                         vairbale_2, vairbale_3)

# Hell no:
def long_function_name(
        vairbale_0, vairbale_1, vairbale_2,
        vairbale_3):
    print(vairbale_0)

# Are you joking?:
# Hanging indents should add a level.
foo = long_function_name(
    vairbale_0, vairbale_1,
    vairbale_2, vairbale_3)

# Feeling funny?:
foo = long_function_name(vairbale_0, vairbale_1,
    vairbale_2, vairbale_3)

# lolk:
def long_function_name(
    vairbale_0, vairbale_1, vairbale_2,
    vairbale_3):
    print(vairbale_0)
```

```py
# Correct:
def long_function_name(
    vairbale_0,
    vairbale_1,
    vairbale_2,
    vairbale_3,
):
    print(vairbale_0)


# Correct:
def long_function_name(
    vairbale_0, vairbale_1, vairbale_2, vairbale_3
):
    print(vairbale_0)


# Correct:
foo = long_function_name(
    vairbale_0,
    vairbale_1,
    vairbale_2,
    vairbale_3,
)

# Correct:
foo = long_function_name(
    vairbale_0, vairbale_1, vairbale_2, vairbale_3
)
```

### Tabs or spaces?

If you ask this again I might cry.

### Maximum line length

120, except if physically not possible (then more is allowed).

### Should a line break before or after an operation?

After.

```py
# ????:
income = (weight
          + pancake
          + (cakes - snacks)
          - cola
          - kfc)
```

```py
# Correct:
income = (
    weight +
    pancake +
    (cakes - snacks) -
    cola -
    kfc
)
```

> Before is allowed too, just follow the other rules for the love of Koishi.

## Blank lines

2 lines between function definition. Can be 3 if it includes type definition(s).

A function defined inside of a type is same based as a function defined outside of a type.
This might be hard for some people, but stay strong, this means there is no difference between the two.

A file should always end with an empty line.

## Source file encoding

UTF-8.

# Imports

Imports should be on the least required lines as humanly possible. When someone opens a file they do not want to see
half page of license and then an another half page of imports. They are looking for that bug vomit under that.

```py
# Wrong:
import os
import sys

# Wronger:
from subprocess import PIPE
from subprocess import Popen
```

```py
# Correct:
import os, sys

# Correcter:
from subprocess import PIPE, Popen
```

Imports should be at the top of the file after file documentation & `__all__` definition.
If the file is dealing with imports (like try catch) then this is not required. Do as you can.

Imports should be sorted alphabetically. Also based on resolution too:

- Standard library.
- 3rd party library
- Local application absolute.
- Local application relative (from most `....` to least.)

Relative imports are based. Absolute imports are cheems doggos.

```py
# Wrong:
import my_package.sibling
from my_package import sibling
from my_package.sibling import example
```

```py
# Correct:
from .sibling import example
```

When an import line passes the recommended line length it should be broke into multiple lines as following:

```py
from ...utils.trace import (
    _render_syntax_error_representation_into, fixup_syntax_error_line_from_buffer, get_exception_representation,
    is_syntax_error
)
```

If imported variables cause local name clashes consider renaming the variables either in the source file or just use
that `as` keyword in the imports.

Star imports should be only used in `__init__.py` files or when collecting all variables from a module(s) intentionally.

## Module level dunder names

For evaluable variables (like `__all__`) after documentation and before imports.
For more complex values (like `__getattr__` or when `__all__` is built) after imports.

## String quotes

Single quote. When using triple quoted strings use double quotes (so we have 6x quoted strings, lol).

## Whitespace

Avoid spaces after bracket opening and before bracket closing:

```py
# Wrong:
cook( pig[ 1 ], { eggs: 2 } )
```

```py
# Correct:
cook(pig[1], {eggs: 2})
```

Between trailing command and closing brackets is optional.

Before block starting `:` do not put extra whitespace.

```py
# Wrong:
if x == 4 :
    print(x, y)
```

```py
# Correct:
if x == 4:
    print(x, y)
```

When dealing with slices put whitespace if it is required to make it readable. (This goes based on feelings.)

```py
# Wrong
pig[some_long_variable+1:some_long_vriable_too*2-4]
```

```py
# Correct:
pig[some_long_variable + 1 : some_long_vriable_too * 2 - 4]
```

Do not put space before brackets if it follows a variable name.

```py
# Wrong:
cook (1)
my_dict ['key'] = my_list [index]
```

```py
# Correct:
cook(1)
my_dict['key'] = my_list[index]

# Correct even tho invalid syntax:
# my_something{value = 2}
```

More than one space around an assignment (or other) operator to align it with another is absolutely allowed.
Can be used to assert dominance on plebs who use automatic code formatters.

```py
# Correct:
x = 1
y = 2
some_stuff = 3

# Hell yeah:
x          = 1
y          = 2
some_stuff = 3
```

Always put space before and after operations like `=`, `==`, `>=`, `&`, `+`, etc.
Except when dealing with line continuations and the line ends with an operation obviously.

```py
# Wrong:
x = x*2 - 1
hypot2 = x*x + y*y
c = (a+b) * (a-b)
i=i+1
submitted +=1
```

```py
# Correct
i = i + 1
submitted += 1
x = x * 2 - 1
hypot2 = x * x + y * y
c = (a + b) * (a - b)
```

Assigning a default value to a parameter, is same as assign a value to a variable.
Use the same formatting as for `=` right above.

```py
# Stultus:
def complex(real, imag=0.0):
    return magic(r=real, i=imag)
```

```py
# Correct:
def complex(real, imag = 0.0):
    return magic(r = real, i = imag)
```

## Comments

Put white space after `#` if it is followed by text.

### Inline Comments

Avoid them. They are scary.

## Documentation Strings

Use double triple quote. If the docstring extends on multiple lines, do not never ever put docstring on the first line
please.

```py
# Whats worng with you:
"""I like chips.

Shrimp fry.
"""
```

```py
# Correct:
"""I like chips."""

# Correct:
"""
I like chips.

Shrimp fry.
"""
```

## Naming Conventions

Either Capital words, lower case with underscore or upper case with underscore. No other option.

```py
# Wrong:
lowercase
UPPERCASE
mixedCase
Capitalized_Words_With_Underscores
```

```py
# Correct:
b (single lowercase letter)
B (single uppercase letter)
lower_case_with_underscores
UPPER_CASE_WITH_UNDERSCORES
CapitalizedWords
```

If an imported module uses wrong naming conversion it is recommended to rename the variables as possible.

### Highlighting brackets

Using extra brackets to highlight logic is recommend if a statement contains `not` keyword.
At the case of complex statements it should be always used to help the reader see which statement is part of what.

```py
# Wrong:
if variable_0 is not None and not isinstance(variable_0, int):
    pass
```

```py
# Correct:
if (variable_0 is not None) and (not isinstance(variable_0, int)):
    pass
```

## Programming recommendations

Always scope down `try` `except`-s to the code that can actually drop the error.

```py
# Wrong:
try:
    return handle_value(collection[key])
except KeyError:
    return key_not_found(key)
```

```py
# Correct:
try:
    value = collection[key]
except KeyError:
    return key_not_found(key)
else:
    return handle_value(value)
```

When comparing `None` always use `is` statements.

```py
# Wrong:
if a == None:
    pass
```

```py
# Correct:
if a is None:
    pass
```

When comparing with `True` of `False` **never** use `is` statement.

```py
# Wrong:
if a is True:
    pass
```

```py
# Correct:
if a == True:
    pass

# Better:
if a:
    pass
```

When checking that something is (or not) `None` always check for it explicitly.

```py
# Wrong:
if a:
    pass
```

```py
# Correct:
if (a is not None):
    pass
```

Do not pack & unpack if you do not need to.

```py
# Wrong:
a, b = 1, 2
```

```py
# Correct:
a = 1
b = 2
```

Do not use `;` if you do not need to.

```py
# Wrong
a = 1; b = 2;
```

```py
# Correct:
a = 1
b = 2
```

Do not use `__init__` when an exception can occur in it. When `__init__` is called the object is already constructed,
so as an example the `__del__` method will most likely raise an `AttributeError`. Use `__new__` at these cases.

```py
# Wrong
def __init__(self, a):
    if a > 5:
        raise ValueError()

    self.a = a
```

```py
# Correct
def __new__(cls, a):
    if a > 5:
        raise ValueError()

    self = object.__new__(cls)
    self.a = a
    return self
```

Stdlib is at best case mid. Do not feel ashamed to reimplement functionality. I would delete it if I could.
