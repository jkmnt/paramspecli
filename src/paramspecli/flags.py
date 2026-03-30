from argparse import BooleanOptionalAction
from typing import Any, overload

from .cli import MISSING, AppendConstAction, Markup
from .fake import Option, RepeatedOption


##
# common use - set: True, unset: False
@overload
def flag(  # type: ignore[overload-overlap]
    *names: str,
    value: bool = True,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[bool, bool]: ...


## value: T
# even less common use - set: T, unset: None
@overload
def flag[T](
    *names: str,
    value: T,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[T, None]: ...


## value: T, default: D
# even even less common use - set: T, unset: D
@overload
def flag[T, D](
    *names: str,
    value: T,
    default: D,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[T, D]: ...


## default: D
# for completeness. shouldn't be really used
@overload
def flag[D](
    *names: str,
    default: D,
    value: bool = True,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[bool, D]: ...


def flag(
    *names: str,
    value: Any = True,
    default: Any = MISSING,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[Any, Any]:
    """flag

    In basic configuration it's boolean:
    ```
    flag() -> True if --foo else False
    ```
    Pass `value=False` to invert:
    ```
    flag(value=False) -> False if --foo else True
    ```

    Pass non-bool `value` to disable the boolean mode:
    ```
    flag(value=123) -> 123 if --foo else None
    ```
    Pass `default` to change default:
    ```
    flag(value=123, default=456) -> 123 if --foo else 456
    ```


    """
    if default is MISSING:
        soft_show_default = False
        if value is True:
            default = False
        elif value is False:
            default = True
        else:
            default = None
    else:
        soft_show_default = default is not None

    return Option(
        names,
        help=help,
        action="store_const",
        const=value,
        default=default,
        #
        hard_show_default=show_default,
        soft_show_default=soft_show_default,
    )


## -> bool
@overload
def switch(
    *names: str,
    default: bool = False,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[bool, bool]: ...


## default: D
@overload
def switch[D](
    *names: str,
    default: D,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[bool, D]: ...


def switch(
    *names: str,
    default: Any = False,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[bool, Any]:
    """On/Off switch with complimentary flags: `--foo/--no-foo`. Default is `False`"""

    return Option(
        names,
        help=help,
        action=BooleanOptionalAction,
        default=default,
        #
        hard_show_default=show_default,
        soft_show_default=True,
    )


## -> int
@overload
def count(
    *names: str,
    default: int = 0,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[int, int]: ...


## default: None
@overload
def count(
    *names: str,
    default: None,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[int, None]: ...


def count(
    *names: str,
    default: int | None = 0,
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = None,
) -> Option[int, Any]:
    """Counter: `-vvv`. Default is `0`"""
    return Option(
        names,
        help=help,
        action="count",
        default=default,
        #
        hard_show_default=show_default,
        soft_show_default=False,
    )


## ---


##
@overload
def repeated_flag(
    *names: str,
    value: bool = True,
    default: None = None,
    help: str | bool | Markup | None = None,
) -> RepeatedOption[bool, None]: ...


# value: T
@overload
def repeated_flag[T](
    *names: str,
    value: T,
    default: None = None,
    help: str | bool | Markup | None = None,
) -> RepeatedOption[T, None]: ...


##
@overload
def repeated_flag[D](
    *names: str,
    value: bool = True,
    default: D,
    help: str | bool | Markup | None = None,
) -> RepeatedOption[bool, D]: ...


# value: T
@overload
def repeated_flag[T, D](
    *names: str,
    value: T,
    default: D,
    help: str | bool | Markup | None = None,
) -> RepeatedOption[T, D]: ...


def repeated_flag(
    *names: str,
    value: Any = True,
    default: Any = None,
    help: str | bool | Markup | None = None,
) -> RepeatedOption[Any, Any]:
    """Flag which could be present multiple times on a command line.
    Each appearance adds `value` to the list.
    """
    return RepeatedOption(
        names,
        help=help,
        action=AppendConstAction,
        default=default,
        const=value,
        soft_show_default=False,
    )
