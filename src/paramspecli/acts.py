import argparse
from typing import Any, Iterable, Literal, NoReturn, overload

from . import util
from .apstub import TypeConverter
from .cli import MISSING, Action, ActionHandler, Markup, Missing


@overload
def custom_action(
    *names: str,
    handler: ActionHandler[str],
    default: Any = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = False,
) -> Action[str]: ...


# nargs=0
@overload
def custom_action(
    *names: str,
    handler: ActionHandler[None],
    nargs: Literal[0],
    default: Any = None,
    #
    help: str | bool | Markup | None = None,
    show_default: bool | str | None = False,
) -> Action[None]: ...


# nargs
@overload
def custom_action(
    *names: str,
    handler: ActionHandler[list[str]],
    nargs: int | Literal["+", "*"],
    default: Any = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = False,
) -> Action[list[str]]: ...


# optional
@overload
def custom_action(
    *names: str,
    handler: ActionHandler[str],
    nargs: Literal["?"],
    default: Any = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = False,
) -> Action[str | Missing]: ...


# T
@overload
def custom_action[T](
    *names: str,
    handler: ActionHandler[T],
    type: TypeConverter[T],
    default: Any = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = False,
) -> Action[T]: ...


# T, nargs
@overload
def custom_action[T](
    *names: str,
    handler: ActionHandler[list[T]],
    type: TypeConverter[T],
    nargs: int | Literal["+", "*"],
    default: Any = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = False,
) -> Action[list[T]]: ...


# T, optional
@overload
def custom_action[T](
    *names: str,
    handler: ActionHandler[T | Missing],
    type: TypeConverter[T],
    nargs: Literal["?"],
    default: Any = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = False,
) -> Action[T | Missing]: ...


def custom_action(
    *names: str,
    handler: ActionHandler[Any],
    type: TypeConverter[Any] | None = None,
    nargs: int | Literal["+", "*", "?"] | None = None,
    default: Any = None,
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[Any] | None = None,
    metavar: str | tuple[str, ...] | None = None,
    show_default: bool | str | None = False,
) -> Action[Any]:
    """Custom action calling the `handler` upon the option match"""
    if metavar is None and choices is None and nargs != 0:
        metavar = names[0].lstrip("-").upper()

    return Action(
        names,
        handler=handler,
        help=help,
        conv=type,
        nargs=nargs,
        default=default,
        const=MISSING if nargs == "?" else None,
        choices=choices,
        metavar=metavar,
        #
        hard_show_default=show_default,
        soft_show_default=default is not None and default != [],
    )


class _VersionPrinter:
    def __init__(self, version: str):
        self.version = version

    def __call__(self, *, parser: argparse.ArgumentParser, **kwargs: Any) -> NoReturn:
        util.echo(self.version)
        parser.exit(0)


def version_action(
    version: str,
    *,
    help: str | Markup | bool = "Show program's version number and exit",
    names: tuple[str, ...] = ("--version",),
) -> Action[None]:
    return Action(names, help=help, nargs=0, handler=_VersionPrinter(version))
