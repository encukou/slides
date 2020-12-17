"""This is a giant hack for visual separation in live coding

After importing hr, `hr._____` (with any number of underscores)
will print a horizontal line to the terminal, with line number at the right.
"""

import shutil
import inspect


def hr(msg=''):
    """Print a horizontal line across the terminal

    "msg" is added to the very right of the line.
    """
    cols, lines = shutil.get_terminal_size()
    print(f'{msg:—>{cols}}')


def __getattr__(name):
    # hack
    f = inspect.currentframe()
    if all(c == '_' for c in name):
        return hr(f'ř.{f.f_back.f_lineno}')
    raise AttributeError(name)

