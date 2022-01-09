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

----

Scarletio is a coroutine based concurrent Python library using modern `async / await` syntax. It abstracts away
threading behind event loops providing concurrent API since the start.

One of the core concept of the library, that event loops should not intercept with synchronous code execution. When
an event loop is started it will not block the control flow. Synchronizations like starting new asynchronous
procedures and retrieving their result cross environment allows you to snuggle synchronous with asynchronous models
well.
