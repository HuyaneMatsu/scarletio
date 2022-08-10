import sys
from os import getcwd as get_current_work_directory
from os.path import (
    dirname as get_directory_name, expanduser as get_user_home_directory, join as join_paths,
    normpath as normalize_path, realpath as get_real_path
)


try:
    from . import __package__ as PACKAGE_NAME
except ImportError:
    PACKAGE_NAME = sys.path[0]
    
    sys.path.append(
        normalize_path(
            join_paths(
                get_directory_name(
                    get_real_path(
                        join_paths(
                            get_current_work_directory(),
                            get_user_home_directory(__file__),
                        )
                    )
                ),
                '..',
            )
        )
    )


PACKAGE = __import__(f'{PACKAGE_NAME}.tools.asynchronous_interactive_console')

collect_package_local_variables = PACKAGE.tools.collect_package_local_variables
run_asynchronous_interactive_console = \
    PACKAGE.tools.asynchronous_interactive_console.run_asynchronous_interactive_console



def __main__():
    """
    Runs an asynchronous interactive console.
    
    > You need python3.8 or higher to use `await`!
    """
    run_asynchronous_interactive_console(collect_package_local_variables(PACKAGE))


if __name__ == '__main__':
    __main__()
