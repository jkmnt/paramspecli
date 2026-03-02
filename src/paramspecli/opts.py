from types import EllipsisType
from typing import Any, Iterable, Literal, overload

from .apstub import TypeConverter
from .fake import Option, RepeatedOption


##
@overload
def option(
    *names: str,
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[str, None]: ...


## default: D
@overload
def option[D](
    *names: str,
    default: D,
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[str, D]: ...


## nargs
@overload
def option(
    *names: str,
    nargs: int | Literal["+", "*"],
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[list[str], None]: ...


## optional
@overload
def option(
    *names: str,
    nargs: Literal["?"],
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[str | EllipsisType, None]: ...


## nargs, default: D
@overload
def option[D](
    *names: str,
    nargs: int | Literal["+", "*"],
    default: D,
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[list[str], D]: ...


## optional, default: D
@overload
def option[D](
    *names: str,
    nargs: Literal["?"],
    default: D,
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[str | EllipsisType, D]: ...


## type: T
@overload
def option[T](
    *names: str,
    type: TypeConverter[T],
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[T, None]: ...


## type: T, default: str | D
# default is parsed if str, otherwise left as is
@overload
def option[T, D](
    *names: str,
    type: TypeConverter[T],
    default: str | D,
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[T, T | D]: ...


## type: T, nargs
@overload
def option[T](
    *names: str,
    type: TypeConverter[T],
    nargs: int | Literal["+", "*"],
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[list[T], None]: ...


## type: T, optional
@overload
def option[T](
    *names: str,
    type: TypeConverter[T],
    nargs: Literal["?"],
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[T | EllipsisType, None]: ...


## type: T, default: str, nargs
# yes, this one is strange. default is parsed by T, but list is not formed
@overload
def option[T](
    *names: str,
    type: TypeConverter[T],
    nargs: int | Literal["+", "*"],
    default: str,
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[list[T], T]: ...


## type: T, default: str, optional
@overload
def option[T](
    *names: str,
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: str,
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[T | EllipsisType, T]: ...


## type: T, default: D, nargs
@overload
def option[T, D](
    *names: str,
    type: TypeConverter[T],
    nargs: int | Literal["+", "*"],
    default: D,
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[list[T], D]: ...


## type: T, default: D, optional
@overload
def option[T, D](
    *names: str,
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: D,
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[T | EllipsisType, D]: ...


def option(
    *names: str,
    type: TypeConverter[Any] | None = None,
    default: Any = None,
    nargs: int | Literal["+", "*", "?"] | None = None,
    help: str | bool | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[Any, Any]:
    """Just an option"""
    return Option(
        names,
        help=help,
        type=type,
        nargs=nargs,
        default=default,
        const=... if nargs == "?" else None,
        choices=choices,
        metavar=metavar if metavar is not None else names[0].lstrip("-").upper(),
        action="store",
        #
        hard_show_default=show_default,
        soft_show_default=default is not None,
    )


##
@overload
def repeated_option(
    *names: str,
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
) -> RepeatedOption[str]: ...


## nargs
@overload
def repeated_option(
    *names: str,
    nargs: int | Literal["+", "*"],
    flatten: Literal[False] = False,
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | tuple[str, ...] | None = None,
) -> RepeatedOption[list[str]]: ...


## nargs, flatten
@overload
def repeated_option(
    *names: str,
    nargs: int | Literal["+", "*"],
    flatten: Literal[True],
    help: str | Literal[False] | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | tuple[str, ...] | None = None,
) -> RepeatedOption[str]: ...


## type: T
@overload
def repeated_option[T](
    *names: str,
    type: TypeConverter[T],
    flatten: Literal[False] = False,
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
) -> RepeatedOption[T]: ...


## type: T, flatten
# gotcha: type converter should return iterable so it could extend running list
@overload
def repeated_option[T](
    *names: str,
    type: TypeConverter[Iterable[T]],
    flatten: Literal[True],
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
) -> RepeatedOption[T]: ...


## type: T, nargs
@overload
def repeated_option[T](
    *names: str,
    type: TypeConverter[T],
    nargs: int | Literal["+", "*"],
    flatten: Literal[False] = False,
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | tuple[str, ...] | None = None,
) -> RepeatedOption[list[T]]: ...


## type: T, nargs, flatten
@overload
def repeated_option[T](
    *names: str,
    type: TypeConverter[T],
    nargs: int | Literal["+", "*"],
    flatten: Literal[True],
    help: str | Literal[False] | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | tuple[str, ...] | None = None,
) -> RepeatedOption[T]: ...


def repeated_option(
    *names: str,
    type: TypeConverter[Any] | None = None,
    nargs: int | Literal["+", "*"] | None = None,
    flatten: bool = False,
    help: str | bool | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
) -> RepeatedOption[Any]:
    """Option which could present multiple times on a command line.
    Result is collected into the list"""
    return RepeatedOption(
        names,
        help=help,
        type=type,
        nargs=nargs,
        choices=choices,
        metavar=metavar if metavar is not None else names[0].lstrip("-").upper(),
        action="extend" if flatten else "append",
        default=[],
        #
        soft_show_default=False,
    )
