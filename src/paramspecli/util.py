import sys
from argparse import ArgumentTypeError
from functools import wraps
from typing import Callable, NoReturn, TextIO

from .exc import ParseAgain


def echo(*strings: str, nl: bool = True, stream: TextIO | None = None) -> None:
    """Should be used instead of the print() to make intention clear"""
    out = stream or sys.stdout
    for s in strings:
        out.write(s)
        if nl:
            out.write("\n")
    out.flush()


def exit(status: int = 0, message: str | tuple[str, ...] | None = None) -> NoReturn:
    """Print error message and exit"""
    if message:
        if isinstance(message, str):
            message = (message,)
        echo(*message, stream=sys.stderr)
    sys.exit(status)


def catch_all[**P, T](f: Callable[P, T]) -> Callable[P, T]:
    """Catch callable exceptions and present them as the cli errors"""

    @wraps(f)
    def catcher(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return f(*args, **kwargs)
        except ParseAgain as e:
            raise e
        except ArgumentTypeError as e:
            raise e
        except Exception as e:
            raise ArgumentTypeError(str(e)) from e

    return catcher


def resolve_later[**P](resolve: Callable[[], Callable[P, None]]) -> Callable[P, None]:
    """Allows the handler to be resolved at the call time"""

    @wraps(resolve)
    def wrap(*args: P.args, **kwargs: P.kwargs) -> None:
        resolve()(*args, **kwargs)

    return wrap
