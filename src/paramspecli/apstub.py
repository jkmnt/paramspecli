# Protocols are used since some of the needed argparse classes are internal, e.g. _SubParsersAction
# Based on a typeshed with a small changes and omissions.
import argparse
from typing import Any, Callable, Iterable, NoReturn, Protocol

type TypeConverter[T] = Callable[[str], T]


class SupportsAddArgument(Protocol):
    def add_argument(
        self,
        *names: str,
        nargs: int | str | None = ...,
        const: Any = ...,
        default: Any = ...,
        type: TypeConverter[Any] = ...,
        choices: Iterable[Any] | None = ...,
        action: str | type[argparse.Action] = ...,
        required: bool = ...,
        help: str | None = ...,
        metavar: str | tuple[str, ...] | None = ...,
        dest: str | None = ...,
        version: str = ...,
        **kwargs: Any,
    ) -> argparse.Action: ...


class SupportsSetDefaults(Protocol):
    def set_defaults(self, **kwargs: Any) -> None: ...


class SupportsAddOneofGroup(Protocol):
    def add_mutually_exclusive_group(self, *, required: bool = ...) -> SupportsAddArgument: ...


class SupportsAddParser(Protocol):
    def add_parser(
        self,
        name: str,
        *,
        # own
        help: str | None = ...,
        aliases: tuple[str, ...] = ...,
        # of ArgumentParser
        usage: str | None = ...,
        description: str | None = ...,
        epilog: str | None = ...,
        formatter_class: type[argparse.HelpFormatter] = ...,
        allow_abbrev: bool = ...,
        # NOTE: exit_on_error is broken in argparse. in same cases it's exit anyway
        exit_on_error: bool = ...,
        prog: str | None = ...,
        add_help: bool = ...,
        # untyped rest
        **kwargs: Any,
    ) -> "ArgumentParserLike": ...


class SupportsAddArgumentGroup(Protocol):
    def add_argument_group(self, title: str | None = ..., description: str | None = ...) -> "ArgumentGroupLike": ...


class ArgumentParserLike(
    SupportsAddArgument, SupportsAddArgumentGroup, SupportsAddOneofGroup, SupportsSetDefaults, Protocol
):
    def add_subparsers(
        self,
        *,
        title: str = ...,
        prog: str | None = ...,
        # parser_class: type[argparse.ArgumentParser],
        parser_class: type[Any],
        required: bool = ...,
        help: str | None = ...,
        metavar: str | None = ...,
        description: str | None = ...,
        dest: str | None = None,
    ) -> SupportsAddParser: ...

    def print_help(self) -> None: ...
    def exit(self, status: int = ..., message: str | None = ...) -> NoReturn: ...


class ArgumentGroupLike(SupportsAddArgument, SupportsAddOneofGroup, SupportsSetDefaults, Protocol): ...
