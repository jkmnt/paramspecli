from typing import Any, Iterable, Literal, overload

from .apstub import TypeConverter
from .cli import AppendAction, ExtendAction, Markup
from .fake import Option, RepeatedOption

# ---


# 1.
# {'type': 'None = None', 'nargs': 'None = None', 'default': 'None = None'}
@overload
def option(
    *names: str,
    #
    type: None = None,
    nargs: None = None,
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[str, None]: ...


# 2.
# {'type': 'None = None', 'nargs': 'None = None', 'default': 'D'}
@overload
def option[D](
    *names: str,
    #
    type: None = None,
    nargs: None = None,
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[str, D]: ...


# 3.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'default': 'None = None'}
@overload
def option(
    *names: str,
    #
    type: None = None,
    nargs: int | Literal["*", "+"],
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[list[str], None]: ...


# 4.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'default': 'D'}
@overload
def option[D](
    *names: str,
    #
    type: None = None,
    nargs: int | Literal["*", "+"],
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[list[str], D]: ...


# 5.
# {'type': 'None = None', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'None = None'}
@overload
def option[C](
    *names: str,
    #
    type: None = None,
    nargs: Literal["?"],
    default: None = None,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[str | C, None]: ...


# 6.
# {'type': 'None = None', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'D'}
@overload
def option[D, C](
    *names: str,
    #
    type: None = None,
    nargs: Literal["?"],
    default: D,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[str | C, D]: ...


# 7.
# {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'None = None'}
@overload
def option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: None = None,
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[T, None]: ...


# 8.
# {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'str'}
@overload
def option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: None = None,
    default: str,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[T, T]: ...


# 9.
# {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'D'}
@overload
def option[T, D](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: None = None,
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[T, D]: ...


# 10.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'default': 'None = None'}
@overload
def option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[list[T], None]: ...


# 11.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'default': 'str'}
@overload
def option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    default: str,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[list[T], T]: ...


# 12.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'default': 'D'}
@overload
def option[T, D](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[list[T], D]: ...


# 13.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'None = None'}
@overload
def option[T, C](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: None = None,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[T | C, None]: ...


# 14.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'str'}
@overload
def option[T, C](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: str,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[T | C, T]: ...


# 15.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'D'}
@overload
def option[T, D, C](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: D,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> Option[T | C, D]: ...


def option(
    *names: str,
    #
    type: TypeConverter[Any] | None = None,
    nargs: int | Literal["+", "*", "?"] | None = None,
    default: Any = None,
    const: Any = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> Option[Any, Any]:
    """Just an option"""

    if isinstance(nargs, int) and nargs <= 0:
        raise ValueError("Options could not have nargs == 0. Use the flags.")

    if metavar is None and choices is None:
        metavar = names[0].lstrip("-").upper()

    return Option(
        names,
        help=help,
        conv=type,
        nargs=nargs,
        default=default,
        const=const,
        choices=choices,
        metavar=metavar,
        action="store",
        #
        hard_show_default=show_default,
        soft_show_default=default is not None,
    )


# ---


# 1.
# {'type': 'None = None', 'nargs': 'None = None', 'default': 'None = None'}
@overload
def repeated_option(
    *names: str,
    #
    type: None = None,
    nargs: None = None,
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[str, None]: ...


# 2.
# {'type': 'None = None', 'nargs': 'None = None', 'default': 'D'}
@overload
def repeated_option[D](
    *names: str,
    #
    type: None = None,
    nargs: None = None,
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[str, D]: ...


# 3.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'None = None'}
@overload
def repeated_option(
    *names: str,
    #
    type: None = None,
    nargs: int | Literal["*", "+"],
    flatten: Literal[False] = False,
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[list[str], None]: ...


# 4.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'D'}
@overload
def repeated_option[D](
    *names: str,
    #
    type: None = None,
    nargs: int | Literal["*", "+"],
    flatten: Literal[False] = False,
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[list[str], D]: ...


# 5.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'None = None'}
@overload
def repeated_option(
    *names: str,
    #
    type: None = None,
    nargs: int | Literal["*", "+"],
    flatten: Literal[True],
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[str, None]: ...


# 6.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'D'}
@overload
def repeated_option[D](
    *names: str,
    #
    type: None = None,
    nargs: int | Literal["*", "+"],
    flatten: Literal[True],
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[str, D]: ...


# 7.
# {'type': 'None = None', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'None = None'}
@overload
def repeated_option[C](
    *names: str,
    #
    type: None = None,
    nargs: Literal["?"],
    default: None = None,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[str | C, None]: ...


# 8.
# {'type': 'None = None', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'D'}
@overload
def repeated_option[D, C](
    *names: str,
    #
    type: None = None,
    nargs: Literal["?"],
    default: D,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[str] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[str | C, D]: ...


# 9.
# {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'None = None'}
@overload
def repeated_option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: None = None,
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[T, None]: ...


# 10.
# {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'str'}
@overload
def repeated_option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: None = None,
    default: str,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[T, T]: ...


# 11.
# {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'D'}
@overload
def repeated_option[T, D](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: None = None,
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[T, D]: ...


# 12.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'None = None'}
@overload
def repeated_option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    flatten: Literal[False] = False,
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[list[T], None]: ...


# 13.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'str'}
@overload
def repeated_option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    flatten: Literal[False] = False,
    default: str,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[list[T], T]: ...


# 14.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'D'}
@overload
def repeated_option[T, D](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    flatten: Literal[False] = False,
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[list[T], D]: ...


# 15.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'None = None'}
@overload
def repeated_option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    flatten: Literal[True],
    default: None = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[T, None]: ...


# 16.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'str'}
@overload
def repeated_option[T](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    flatten: Literal[True],
    default: str,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[T, T]: ...


# 17.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'D'}
@overload
def repeated_option[T, D](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: int | Literal["*", "+"],
    flatten: Literal[True],
    default: D,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[T, D]: ...


# 18.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'None = None'}
@overload
def repeated_option[T, C](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: None = None,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[T | C, None]: ...


# 19.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'str'}
@overload
def repeated_option[T, C](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: str,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[T | C, T]: ...


# 20.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'D'}
@overload
def repeated_option[T, D, C](
    *names: str,
    #
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: D,
    const: C,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[T] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[T | C, D]: ...


def repeated_option(
    *names: str,
    type: TypeConverter[Any] | None = None,
    nargs: int | Literal["+", "*", "?"] | None = None,
    default: Any = None,
    flatten: bool = False,
    const: Any = None,
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = None,
) -> RepeatedOption[Any, Any]:
    """Option which could present multiple times on a command line.
    Result is collected into the list"""

    if isinstance(nargs, int) and nargs <= 0:
        raise ValueError("Options could not have nargs == 0. Use the flags.")

    if metavar is None and choices is None:
        metavar = names[0].lstrip("-").upper()

    return RepeatedOption(
        names,
        help=help,
        conv=type,
        nargs=nargs,
        choices=choices,
        metavar=metavar,
        action=ExtendAction if flatten else AppendAction,
        default=default,
        const=const,
        #
        hard_show_default=show_default,
        soft_show_default=default is not None and default != [],
    )
