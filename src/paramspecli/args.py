from typing import Any, Iterable, Literal, overload

from .apstub import TypeConverter
from .fake import Argument


##
@overload
def argument(
    metavar: str,
    *,
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
) -> Argument[str, str]: ...


## nargs
@overload
def argument(
    metavar: str,
    *,
    nargs: int | Literal["*", "+"],
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
) -> Argument[list[str], list[str]]: ...


## optional
@overload
def argument(
    metavar: str,
    *,
    nargs: Literal["?"],
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
) -> Argument[str, None]: ...


## optional, default: D
@overload
def argument[D](
    metavar: str,
    *,
    nargs: Literal["?"],
    default: D,
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
) -> Argument[str, D]: ...


##  type: T
@overload
def argument[T](
    metavar: str,
    *,
    type: TypeConverter[T],
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
) -> Argument[T, T]: ...


##  type: T, nargs
@overload
def argument[T](
    metavar: str,
    *,
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
) -> Argument[list[T], list[T]]: ...


## type: T, optional
@overload
def argument[T](
    metavar: str,
    *,
    type: TypeConverter[T],
    nargs: Literal["?"],
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
) -> Argument[T, None]: ...


## type: T, optional, default: str | D
# default is parsed if string
@overload
def argument[T, D](
    metavar: str,
    *,
    type: TypeConverter[T],
    nargs: Literal["?"],
    help: str | Literal[False] | None = None,
    default: str | D,
    choices: Iterable[T] | None = None,
) -> Argument[T, T | D]: ...


def argument(
    metavar: str,
    *,
    type: TypeConverter[Any] | None = None,
    help: str | Literal[False] | None = None,
    nargs: int | Literal["*", "+", "?"] | None = None,
    default: Any | None = None,
    choices: Iterable[Any] | None = None,
) -> Argument[Any, Any]:
    """Positional argument. Always required, unless made optional via `nargs="?"`."""
    return Argument(metavar, help=help, conv=type, choices=choices, nargs=nargs, default=default)
