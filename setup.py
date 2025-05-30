import pathlib, re
from ast import literal_eval
from setuptools import setup


HERE = pathlib.Path(__file__).parent

# Lookup version
version_search_pattern = re.compile('^__version__[ ]*=[ ]*((?:\'[^\']+\')|(?:\"[^\"]+\"))[ ]*$', re.M)
parsed = version_search_pattern.search((HERE / 'scarletio' / '__init__.py').read_text())
if parsed is None:
    raise RuntimeError('No version found in `__init__.py`.')

version = literal_eval(parsed.group(1))

# Lookup readme
README = (HERE / 'README.md').read_text('utf-8')

setup(
    name = 'scarletio',
    version = version,
    packages = [
        'scarletio',
        'scarletio.core',
        'scarletio.ext',
        'scarletio.ext.asyncio',
        'scarletio.core.event_loop',
        'scarletio.core.subprocess',
        'scarletio.core.top_level',
        'scarletio.core.protocols_and_transports',
        'scarletio.core.traps',
        'scarletio.http_client',
        'scarletio.main',
        'scarletio.main.key_debug',
        'scarletio.tools',
        'scarletio.tools.asynchronous_interactive_console',
        'scarletio.tools.asynchronous_interactive_console.editors',
        'scarletio.utils',
        'scarletio.utils.highlight',
        'scarletio.utils.highlight.formatter_detail',
        'scarletio.utils.trace',
        'scarletio.utils.trace.exception_proxy',
        'scarletio.utils.trace.exception_representation',
        'scarletio.utils.trace.exception_representation.suggestion',
        'scarletio.utils.trace.expression_parsing',
        'scarletio.utils.trace.frame_proxy',
        'scarletio.utils.type_proxies',
        'scarletio.web_common',
        'scarletio.web_common.url',
        'scarletio.web_socket',
        'scarletio.streaming',
        'scarletio.streaming.resource_streaming',
        'scarletio.streaming.zip_streaming',
    ],
    url = 'https://github.com/HuyaneMatsu/scarletio',
    license = 'DBAD',
    author = 'HuyaneMatsu',
    author_email = 're.ism.tm@gmail.com',
    description = 'Asynchronous blackmagic & Witchcraft',
    long_description = README,
    long_description_content_type = 'text/markdown',
    classifiers = [
        'Development Status :: 4 - Beta',
        
        'Intended Audience :: Developers',
        
        'Operating System :: OS Independent',
        
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data = False,
    package_data = {},
    python_requires = '>=3.6',
    install_requires = [
        'chardet>=2.0',
    ],
    extras_require = {
        'cpythonspeedups': [
            'cchardet>=2.0',
        ],
    },
    entry_points = {
        'console_scripts': [
            'scarletio = scarletio.__main__:__main__'
        ],
    },
)
