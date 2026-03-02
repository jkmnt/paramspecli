import sys
from argparse import ArgumentTypeError
from functools import wraps
from typing import Callable, NoReturn, TextIO

from .apstub import TypeConverter


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


def catch_all[T](f: TypeConverter[T]) -> TypeConverter[T]:
    """Catch type converter exceptions and present them as the cli errors"""

    @wraps(f)
    def catcher(s: str) -> T:
        try:
            return f(s)
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
