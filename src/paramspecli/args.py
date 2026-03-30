from typing import Any, Iterable, Literal, overload

from .apstub import TypeConverter
from .cli import Markup
from .fake import Argument


# 1.
# {'type': 'None', 'nargs': 'None'}
@overload
def argument(
    metavar: str,
    *,
    #
    type: None = None,
    nargs: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
) -> Argument[str, str]: ...


# 2.
# {'type': 'None', 'nargs': 'int | Literal["*", "+"]'}
@overload
def argument(
    metavar: str,
    *,
    #
    type: None = None,
    nargs: int | Literal["*", "+"],
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
) -> Argument[list[str], list[str]]: ...


# 3.
# {'type': 'None', 'nargs': 'Literal["?"]', 'default': 'None'}
@overload
def argument(
    metavar: str,
    *,
    #
    type: None = None,
    nargs: Literal["?"],
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
) -> Argument[str, None]: ...


# 4.
# {'type': 'None', 'nargs': 'Literal["?"]', 'default': 'D'}
@overload
def argument[D](
    metavar: str,
    *,
    #
    type: None = None,
    nargs: Literal["?"],
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
) -> Argument[str, D]: ...


# 5.
# {'type': 'TypeConverter[T]', 'nargs': 'None'}
@overload
def argument[T](
    metavar: str,
    *,
    #
    type: TypeConverter[T],
    nargs: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
) -> Argument[T, T]: ...


# 6.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]'}
@overload
def argument[T](
    metavar: str,
    *,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
) -> Argument[list[T], list[T]]: ...


# 7.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"', 'default': 'None'}
@overload
def argument[T](
    metavar: str,
    *,
    #
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
) -> Argument[T, None]: ...


# 8.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"', 'default': 'str'}
@overload
def argument[T, D](
    metavar: str,
    *,
    #
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: str,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
) -> Argument[T, T]: ...


# 8.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"', 'default': 'D'}
@overload
def argument[T, D](
    metavar: str,
    *,
    #
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
) -> Argument[T, D]: ...


def argument(
    metavar: str,
    *,
    #
    type: TypeConverter[Any] | None = None,
    nargs: int | Literal["*", "+", "?"] | None = None,
    default: Any | None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
) -> Argument[Any, Any]:
    """Positional argument. Always required, unless made optional via `nargs="?"`."""

    if isinstance(nargs, int) and nargs <= 0:
        raise ValueError("Arguments could not have nargs == 0")

    return Argument(metavar, help=help, conv=type, choices=choices, nargs=nargs, default=default)
