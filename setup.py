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
        'scarletio.core.protocols_and_transports',
        'scarletio.core.traps',
        'scarletio.http_client',
        'scarletio.tools',
        'scarletio.utils',
        'scarletio.web_common',
        'scarletio.websocket',
    ],
    url = 'https://github.com/HuyaneMatsu/scarletio',
    license = 'MIT',
    author = 'HuyaneMatsu',
    author_email = 're.ism.tm@gmail.com',
    description = 'Asynchronous blackmagic & Witchcraft',
    long_description = README,
    long_description_content_type = 'text/markdown',
    classifiers = [
        'Development Status :: 4 - Beta',
        
        'License :: OSI Approved :: MIT License',
        
        'Intended Audience :: Developers',
        
        'Operating System :: OS Independent',
        
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        #'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    include_package_data = True,
    package_data = {
    },
    python_requires = '>=3.6',
    install_requires = [
        'chardet>=2.0',
    ],
    extras_require = {
        'cpythonspeedups': [
            'cchardet>=2.0',
        ],
    },
)
