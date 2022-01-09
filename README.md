<h3 align="center">
    <font size="6">
        <b>
            <a href="https://github.com/HuyaneMatsu/scarletio">
                scarletio
            </a>
        </b>
    </font>
</h3>

<b>
    Asynchronous blackmagic & Witchcraft
</b>

<h1></h1>

Scarletio is a coroutine based concurrent Python library using modern `async / await` syntax. It abstracts away
threading behind event loops providing concurrent API since the start.

One of the core concept of the library, that event loops should not intercept with synchronous code execution. When
an event loop is started it will not block the control flow. Synchronizations like starting new asynchronous
procedures and retrieving their result cross environment allows you to snuggle synchronous with asynchronous models
well.
