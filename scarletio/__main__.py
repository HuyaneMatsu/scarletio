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


PACKAGE = __import__(PACKAGE_NAME)
__import__(f'{PACKAGE_NAME}.tools')
__import__(f'{PACKAGE_NAME}.main')

collect_module_variables = PACKAGE.tools.collect_module_variables
run_asynchronous_interactive_console = \
    PACKAGE.tools.asynchronous_interactive_console.run_asynchronous_interactive_console
debug_key = PACKAGE.main.debug_key
get_short_executable = PACKAGE.get_short_executable


def __main__():
    """
    Runs an asynchronous interactive console.
    
    > You need python3.8 or higher to use `await`!
    
    > If `debug-key` or `dk` is passed as a command, it pops up a key debugger instead.
    """
    parameters = sys.argv.copy()
    
    if parameters and ((parameters[0] == __file__) or (parameters[0] != get_short_executable())):
        del parameters[0]
    
    if parameters:
        used_command_name = parameters[0].strip().casefold().replace('_', '-')
    else:
        used_command_name = 'interpreter'
    
    if used_command_name in ('debug-key', 'dk'):
        debug_key()
    
    elif used_command_name in ('interpreter', 'i'):
        run_asynchronous_interactive_console(collect_module_variables(PACKAGE))
    
    else:
        sys.stdout.write(
            'Available commands:\n'
            '- interpreter\n'
            '- debug-character\n'
        )


if __name__ == '__main__':
    __main__()
