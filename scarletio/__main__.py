from . import __package__ as PACKAGE_NAME
from .tools.asynchronous_interactive_console import (
    collect_package_local_variables, run_asynchronous_interactive_console
)


PACKAGE = __import__(PACKAGE_NAME)


def __main__():
    """
    Runs an asynchronous interactive console.
    
    > You need python3.8 or higher to use `await`!
    """
    run_asynchronous_interactive_console(collect_package_local_variables(PACKAGE))


if __name__ == '__main__':
    __main__()
