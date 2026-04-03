# Streaming

### From http & to http

Streaming from http to http is not hard since the client http supports payload streaming as output,
and async generator as input.


Example for printing an http response's stream.

```py
from scarletio import get_event_loop
from scarletio.http_client import HTTPClient


http = HTTPClient(get_event_loop())


async with http.get('get_url') as response:
    payload_stream = response.payload_stream
    if (payload_stream is not None):
        async for chunk in payload_stream:
            print(chunk)
```

Example for streaming to an http request:

```py
from scarletio import get_event_loop
from scarletio.http_client import HTTPClient


async def stream_data():
    yield b'hello\n'
    yield b'there\n'


http = HTTPClient(get_event_loop())


await http.post('post_url', data = stream_data())
```

Example for chaining response stream into a request:

```py
from scarletio import get_event_loop
from scarletio.http_client import HTTPClient


async def stream_data_from_get_request(http, url):
    response = await http.get(url)
    payload_stream = response.payload_stream
    if (payload_stream is not None):
        async for chunk in payload_stream:
            yield chunk


http = HTTPClient(get_event_loop())


await http.post('post_url', data = stream_data_from_get_request(http, 'get_url'))
```

### Reusable streams

Http requests are commonly retried, either by you, or on redirect.
In these cases an already started coroutine generator would fail since it cannot be restarted.
To solve this you can use the `ResourceStreamFunction` wrapper that starts the wrapped coroutine generator function
each time it is tried to be async iterated.

```py
from scarletio import get_event_loop
from scarletio.http_client import HTTPClient
from scarletio.streaming import ResourceStreamFunction


@ResourceStreamFunction
async def create_get_request_stream_resource(http, url):
    response = await http.get(url)
    payload_stream = response.payload_stream
    if (payload_stream is not None):
        async for chunk in payload_stream:
            yield chunk


http = HTTPClient(get_event_loop())


for retry in range(5):
    async with http.post('post_url', data = create_get_request_stream_resource(http, 'get_url')) as response:
        
        # Repeat on internal server error up to 4 more times
        if response.status < 500:
            break
```

### Streaming form-data

`form-data`-s can be used to send an http request that is built from multiple parts.
These are usually multiple files / attachments, but can be anything else.

Each "field" in a formdata has a "name" and its "value" (and other various things), where the "value" can be a stream.
A form-data is reusable if all of its "values" are reusable.

```py
from scarletio import get_event_loop
from scarletio.http_client import HTTPClient
from scarletio.streaming import ResourceStreamFunction
from scarletio.web_common import FormData


@ResourceStreamFunction
async def create_get_request_stream_resource(http, url):
    response = await http.get(url)
    payload_stream = response.payload_stream
    if (payload_stream is not None):
        async for chunk in payload_stream:
            yield chunk


http = HTTPClient(get_event_loop())


form = FormData()
form.add_field(
    f'files[0]',
    create_get_request_stream_resource(http, 'get_url_0'),
    file_name = 'sister.txt',
    content_type = 'application/octet-stream',
)
form.add_field(
    f'files[1]',
    create_get_request_stream_resource(http, 'get_url_1'),
    file_name = 'love.txt',
    content_type = 'application/octet-stream',
)

for retry in range(5):
    async with http.post('post_url', data = form) as response:
        
        # Repeat on internal server error up to 4 more times
        if response.status < 500:
            break
```

### Streaming zips

Sometimes you want to stream multiple files as one, for these cases zip streaming is an acceptable solution.
Scarletio provides support for a single time stream with the `stream_zip` coroutine generator function,
and reusable streaming using `stream_zip`'s wrapped version `create_zip_stream_resource`.

```py
from scarletio import get_event_loop
from scarletio.http_client import HTTPClient
from scarletio.streaming import ResourceStreamFunction, ZipStreamFile, create_zip_stream_resource


@ResourceStreamFunction
async def create_get_request_stream_resource(http, url):
    response = await http.get(url)
    payload_stream = response.payload_stream
    if (payload_stream is not None):
        async for chunk in payload_stream:
            yield chunk


http = HTTPClient(get_event_loop())

data = create_zip_stream_resource([
    ZipStreamFile(
        'sister.txt',
        create_get_request_stream_resource(http, 'get_url_0'),
    ),
    ZipStreamFile(
        'love.txt',
        create_get_request_stream_resource(http, 'get_url_1'),
    ),
])

for retry in range(5):
    async with http.post('post_url', data = data) as response:
        
        # Repeat on internal server error up to 4 more times
        if response.status < 500:
            break
```

##### Zip name deduplication

The duplicate names in a zip archive are deduplicated using a `path (index).extension` format.
This logic can be modified by using the `name_deduplicator` keyword parameter.

Passing it as `None` completely disables name deduplication.

```py
zip_stream = create_zip_stream_resource(files, name_deduplicator = None)
```

The default name deduplicator can also use different configuration.
Here is an example modifying it from `path (index).extension` to `path~index.extension` by providing a different regex
and name reconstructor.

```py
from re import compile as re_compile
from scarletio.streaming import name_deduplicator_default

NAME_REGEX = re_compile('((?:.*/)?.*?)(?:~(\\d+))?(?:\\.(.*?))?')

def name_reconstructor(path, index, extension):
    name_parts = [path]
    
    if index:
        name_parts.append('~')
        name_parts.append(str(index))
    
    if (extension is not None):
        name_parts.append('.')
        name_parts.append(extension)
    
    return ''.join(name_parts)


zip_stream = create_zip_stream_resource(
    files,
    name_deduplicator = name_deduplicator_default(NAME_REGEX, name_reconstructor),
)

```

Completely custom name deduplicator is also viable.
Here is a deduplicator that postfixes every file (even non-duplicates) in a `path_index.extension` format.

```py
from itertools import count
from re import compile as re_compile


NAME_REGEX = re_compile('((?:.*/)?.*?)(?:\\.(.*?))?')


def name_reconstructor(path, index, extension):
    name_parts = [path, '_', str(index).rjust(4, '0')]
    
    if (extension is not None):
        name_parts.append('.')
        name_parts.append(extension)
    
    return ''.join(name_parts)


def name_deduplicator_postfixed():
    name = yield
    
    for index in count():
        match = NAME_REGEX.fullmatch(name)
        if match is None:
            path = name
            extension = None
        else:
            path, extension = match.groups()
        
        name = yield name_reconstructor(path, index, extension)


zip_stream = create_zip_stream_resource(
    files,
    name_deduplicator = name_deduplicator_postfixed(),
)
```
