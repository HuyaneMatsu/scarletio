<h1 align="center">
    <b>
        <a href="https://github.com/HuyaneMatsu/scarletio">
            scarletio
        </a>
    </b>
</h1>

<p align="center">
    <b>
        Asynchronous blackmagic & Witchcraft
    </b>
</p>

<br>

---

## Table of contents
- [Introduction](#introduction)
- [Coroutines](#coroutines)
- [Running coroutines](#running-coroutines)
- [Tasks](#tasks)
- [Task groups](#task-groups)
- [Task cancellation](#task-cancellation)
- [Task suspension](#task-suspension)
- [Timeouts](#timeouts)
- [Running in threads](#running-in-threads)
- [Scheduling from other threads](#scheduling-from-other-threads)
- [Locks](#locks)
- [Events](#events)

---

## Introduction

Scarletio is a coroutine based concurrent Python library using modern `async / await` syntax.
Originally inspired by asyncio.

One of the core concepts of the library is that the event loops should not intercept with synchronous code execution.
When an event loop is started it will not block the control flow, instead it provides you various synchronization
tools to start new asynchronous procedures and to retrieve their results cross environment.

You can experiment with scarletio in the REPL:
```
$ python3 -m scarletio
                     _      _   _
                    | |    | | (_)
  ___  ___ __ _ _ __| | ___| |_ _  ___
 / __|/ __/ _` | '__| |/ _ \ __| |/ _ \
 \__ \ (_| (_| | |  | |  __/ |_| | (_) |
 |___/\___\__,_|_|  |_|\___|\__|_|\___/

                                  1.0.56


Scarletio interactive console 3.8.10 (default, May 26 2023, 14:05:08) [GCC 9.4.0] on linux.
Use "await" directly.
Type "help", "copyright", "credits" or "license" for more information.
In [0]: 
```

> **Note**
> a great deal of Scarletio features only works on Linux

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Coroutines

[Coroutines](https://docs.python.org/3/glossary.html#term-coroutine) are a special type of function that can be
suspended and resumed, allowing other code to run in between.
Coroutines enable developers to write asynchronous code in a more sequential and readable manner.

In traditional programming functions are called, executed, and completed before control is returned to the caller.
However, coroutines differ in that they can be suspended in the middle of their execution, allowing the program to
switch to another task.
When a coroutine is suspended, it yields control back to the event loop, allowing other code to be executed.

A coroutine function is declared by prefixing a function definition with the `async` keyword, like this:

```py3
In [0]: async def main():
   ...:     print('hello')
   ...:     await sleep(1.0)
   ...:     print('world')
   ...:
```

This functions prints out "hello", waits 1 second and then prints "world".

Inside a coroutine function, you can use the `await` keyword to wait for the result of another coroutine or an
asynchronous operation.
When an await statement is encountered, the coroutine suspends its execution until the awaited task is complete,
allowing other coroutines to run in the meantime.

Coroutines are scheduled and executed within an event loop, which is responsible for managing their execution and
switching between them.

Note that simply calling a coroutine function will not schedule it to be executed:

```py3
In [1]: main()
<coroutine object main at 0x7fbb2615d340>
```

To run the coroutine we have to `await` it:

```py3
In [2]: await main()
hello
world
```

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Running coroutines

Scarletio repl provides a native way of using `await`, but traditionally `await` can only be used inside of coroutine
functions.

```py3
from scarletio import sleep

async def main():
    print('hello')
    await sleep(1.0)
    print('world')


await main()

# Produces:
#
#  File "file.py", line 8
#    await main()
#    ^
#SyntaxError: 'await' outside function
```

We can use `scarletio.run` function to run our entry point, the "main" function.

```py3
from scarletio import run, sleep

async def main():
    print('hello')
    await sleep(1.0)
    print('world')


run(main())

# Produces:
#
# hello
# world
```

For more control over our application we want to access our event loop directly, since that is handling the scheduling
and the execution of our tasks. To get our event loop we will use the `scarletio.get_or_create_event_loop` function.

```py3
from scarletio import get_or_create_event_loop, sleep

async def main():
    print('hello')
    await sleep(1.0)
    print('world')


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# hello
# world
```

While `scarletio.run` handles loop detection, creation and stopping as required, `loop.run` will not stop the event
loop after our coroutine finishes.

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Tasks

Tasks are used to schedule coroutines concurrently. To schedule up a task we wrap our coroutine with a function
just as `loop.create_task`. It will return our task and schedule up the coroutine.

```py3
from scarletio import get_or_create_event_loop, sleep


async def say_after(to_say, after):
    await sleep(after)
    print(to_say)


async def main():
    # We schedule up `say_after`
    task = LOOP.create_task(say_after('hello', 1))
    
    # Lets wait for our task's completion.
    await task


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# hello
```

To run coroutines concurrently we just have to create more tasks.

```py3
from scarletio import get_or_create_event_loop, sleep


async def say_after(to_say, after):
    await sleep(after)
    print(to_say)


async def main():
    # We schedule up `say_after`. One finishes after 1 and the other after 2 seconds.
    task_0 = LOOP.create_task(say_after('hello', 1))
    task_1 = LOOP.create_task(say_after('world', 2))
    
    # Lets await for out tasks' completion.
    await task_0
    await task_1


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# hello
# world
```

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Task groups

Task groups allow you to manage and coordinate a collection of tasks.
They provide convenient way to work with multiple tasks concurrently and track their progress and results.

Task groups provide methods to create and add individual tasks to the group. They are particularly useful in scenarios
where you have a set of related tasks that can be executed concurrently and need to be managed collectively.
They make it easier to handle complex workflows and improve the readability of asynchronous code.

```py3
from scarletio import TaskGroup, get_or_create_event_loop, sleep


async def say_after(to_say, after):
    await sleep(after)
    print(to_say)


async def main():
    task_group = TaskGroup(LOOP)
    
    # We schedule up `say_after`.
    task_group.create_task(say_after('hello', 1))
    task_group.create_task(say_after('world', 2))
    
    # Lets await for out tasks' completion.
    await task_group.wait_all()


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# hello
# world
```

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Task cancellation

Tasks can easily and safely be cancelled. When a task is cancelled a `scarletio.CancelledError` will be raised into
task at the next opportunity.

```py3
from scarletio import TaskGroup, get_or_create_event_loop, sleep


async def say_after(to_say, after):
    await sleep(after)
    print(to_say)


async def main():
    task_group = TaskGroup(LOOP)
    
    # We schedule up `say_after`. By cancelling `hello` it will not print.
    task_group.create_task(say_after('hello', 1)).cancel()
    task_group.create_task(say_after('world', 2))
    
    # Lets await for out tasks' completion.
    await task_group.wait_all()


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# world
```

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Task suspension

Tasks can be suspended using either `sleep`, `skip_poll_cycle` or `skip_ready_cycle`.

`sleep` suspends the task for the given amount of seconds.

```py3
from time import strftime
from scarletio import get_or_create_event_loop, sleep


async def main():
    # Print out the current time every 4 seconds.
    while True:
        print(strftime('%X'))
        await sleep(4)


LOOP = get_or_create_event_loop()
try:
    LOOP.run(main())
finally:
    LOOP.stop()
```

`sleep` returns a `Future`, so they can be *cancelled* or simply used inside a task group too.

```py3
from scarletio import TaskGroup, get_or_create_event_loop, sleep


async def say_after(to_say, after):
    await sleep(after)
    print(to_say)


async def main():
    task_group = TaskGroup(LOOP)
    
    task_group.create_task(say_after('hello', 1))
    task_group.add_future(sleep(2))
    
    # Lets await for out tasks' completion.
    await task_group.wait_all()
    print('world')


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# hello
# world
```

`skip_ready_cycle` skips every scheduled and ready to run tasks. This can be used to synchronise between other tasks,
or to wait for other scheduled callbacks to finish before we continue our tasks' execution.

This is particularly useful in event driven programming when we know our event handlers will be run, but we do not
know in what order.

```py3
from scarletio import TaskGroup, get_or_create_event_loop, skip_ready_cycle


async def say_first(to_say):
    print(to_say)


async def say_second(to_say):
    await skip_ready_cycle()
    print(to_say)


async def main():
    task_group = TaskGroup(LOOP)
    
    # `say_second` will always print after `say_first` if scheduled concurrently.
    task_group.create_task(say_second('world'))
    task_group.create_task(say_first('hello'))
    
    # Lets await for out tasks' completion.
    await task_group.wait_all()


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# hello
# world
```

`skip_poll_cycle` is a more extreme version of `skip_ready_cycle`, because it schedules the task back after the next
io polling.

```py3
from scarletio import TaskGroup, get_or_create_event_loop, skip_poll_cycle, skip_ready_cycle


async def skip_10_times_then_say(to_say):
    for _ in range(10):
        await skip_ready_cycle()
    
    print(to_say)


async def skip_io_poll_then_say(to_say):
    await skip_poll_cycle()
    print(to_say)


async def main():
    task_group = TaskGroup(LOOP)
    
    task_group.create_task(skip_io_poll_then_say('world'))
    task_group.create_task(skip_10_times_then_say('hello'))
    
    # Lets await for out tasks' completion.
    await task_group.wait_all()


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# hello
# world
```

Since tasks are usually scheduled after `io` operations, Scarletio will always prefer to finish all already
scheduled and ready to run tasks before again polling from io.

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Timeouts

Timeouts can be applied to `Future`-s and `Task`-s using their `apply_timeout` method. If timeout occurs the `Task`
is cancelled and a `TimeoutError` is propagated.

```py3
from scarletio import get_or_create_event_loop, sleep


async def wait_forever():
    await sleep(3600)


async def main():
    task = LOOP.create_task(wait_forever())
    task.apply_timeout(1.0)
    
    try:
        await task
    except TimeoutError:
        print('TIMEOUT!')


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# TIMEOUT!
```

We can use `repeat_timeout` when executing a loop where timeout should be applied on each cycle.

```py3
from scarletio import get_or_create_event_loop, repeat_timeout, sleep


async def say_after(to_say, after):
    await sleep(after)
    print(to_say)


async def main():
    after = 2
    try:
        with repeat_timeout(5) as loop:
            for _ in loop: # The timeout is reapplied with every iteration.
                await say_after('hi', after)
                after += 2
    except TimeoutError:
        print('TIMEOUT!')


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()


# Produces:
#
# hi
# hi
# TIMEOUT!
```

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Running in threads

While tasks run inside an event loop, it is possible to move their execution into a separate thread or,
to be more accurate, into an executor.
It can be useful when running IO-bound functions that would otherwise block the event loop.

```py3
from threading import current_thread
from time import sleep as blocking_sleep
from scarletio import enter_executor, get_or_create_event_loop


async def main():
    print(f'before entering: {current_thread().ident}')
    async with enter_executor():
        print(f'after entering: {current_thread().ident}')
        
        blocking_sleep(2)
        
        print(f'before exiting: {current_thread().ident}')
    print(f'after exiting: {current_thread().ident}')


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces: (example)
# 
# before entering: 140664167724800
# after entering: 140664159332096
# before exiting: 140664159332096
# after exiting: 140664167724800
```

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Scheduling from other threads

We can create tasks from other threads by using the `create_task_thread_safe` method.
If we want to retrieve their result we use `task.sync_wrap().wait()`.

```py3
from scarletio import get_or_create_event_loop, sleep


async def say_after(to_say, after):
    await sleep(after)
    print(to_say)


LOOP = get_or_create_event_loop()

# Create our tasks from a different thread
task_0 = LOOP.create_task_thread_safe(say_after('hello', 1))
task_1 = LOOP.create_task_thread_safe(say_after('world', 2))

# Wait for their execution to finish.
task_0.sync_wrap().wait()
task_1.sync_wrap().wait()

LOOP.stop()
```

It is also possible to wait for tasks' results from other event loop using `await task.async_wrap(loop)`.

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Locks

Scarletio `Lock` can be used to guarantee exclusive access to a shared resource.
Should be used with `async with` statement.

The example will:
- Print `hello` after 1 second.
- Print `world` after 2 seconds.
- Print `hello world` after 4 seconds.

```py3
from scarletio import Lock, TaskGroup, get_or_create_event_loop, sleep


async def say_after(to_say, after, lock):
    async with lock:
        await sleep(after)
        print(to_say)


async def main():
    task_group = TaskGroup(LOOP)
    lock = Lock(LOOP)
    
    task_group.create_task(say_after('hello', 1, lock))
    task_group.create_task(say_after('world', 1, lock))
    task_group.create_task(say_after('hello world', 2, lock))
    
    # Lets await for out tasks' completion.
    await task_group.wait_all()


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

```

A scarletio `ScarletLock` can be used to guarantee access to a shared resource `n` amount of times.

The example will:
- Print `hello` and `world` after 1 second.
- Print `hello world` after 3 seconds.

```py3
from scarletio import ScarletLock, TaskGroup, get_or_create_event_loop, sleep


async def say_after(to_say, after, lock):
    async with lock:
        await sleep(after)
        print(to_say)


async def main():
    task_group = TaskGroup(LOOP)
    lock = ScarletLock(LOOP, 2)
    
    task_group.create_task(say_after('hello', 1, lock))
    task_group.create_task(say_after('world', 1, lock))
    task_group.create_task(say_after('hello world', 2, lock))
    
    # Lets await for out tasks' completion.
    await task_group.wait_all()


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()
```

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>

---

## Events

A scarletio `event` can be used to notify multiple tasks that some event has happened.

```py3
from scarletio import Event, TaskGroup, get_or_create_event_loop, sleep


async def set_event_after(event, after):
    await sleep(after)
    event.set()


async def say_when_set(to_say, event):
    await event
    print(to_say)


async def main():
    task_group = TaskGroup(LOOP)
    event = Event(LOOP)
    
    task_group.create_task(set_event_after(event, 2))
    task_group.create_task(say_when_set('hello', event))
    task_group.create_task(say_when_set('world', event))
    
    # Lets await for out tasks' completion.
    await task_group.wait_all()


LOOP = get_or_create_event_loop()
LOOP.run(main())
LOOP.stop()

# Produces:
#
# hello
# world
```

<div align="right">[ <a href="#table-of-contents">↑ Back to top ↑</a> ]</div>
