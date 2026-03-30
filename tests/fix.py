import dataclasses
import os
import shlex
from argparse import ArgumentParser
from contextlib import contextmanager
from typing import Any, Callable, Final, Generator, NoReturn

import pytest

import paramspecli as ps
from paramspecli.cli import Route


class ParseError(Exception):
    pass


class ParseExit(Exception):
    pass


class Parser(ArgumentParser):
    def exit(self, status: int = 0, message: str | None = None) -> NoReturn:
        if status == 0:
            raise ParseExit(message)
        raise ParseError(message)


class AnyFunc:
    def __eq__(self, other: object) -> bool:
        return True

    def __call__(self, args: Any, **kwargs: Any) -> None:
        pass


ANY_FUNC: Final = AnyFunc()


class Group(ps.Group):
    def parse(self, inp: str | list[str], *, config: ps.Config | None = None, context: Any = None) -> Route:  # type: ignore[override]  # ty: ignore[invalid-method-override]
        if not isinstance(inp, list):
            inp = shlex.split(inp)

        config = dataclasses.replace(config or ps.Config(), parser_class=Parser)
        return super().parse(inp, config=config, context=context)


class CallableGroup[**P](ps.CallableGroup[P]):
    def parse(self, inp: str | list[str], *, config: ps.Config | None = None, context: Any = None) -> Route:  # type: ignore[override]  # ty: ignore[invalid-method-override]
        if not isinstance(inp, list):
            inp = shlex.split(inp)

        config = dataclasses.replace(config or ps.Config(), parser_class=Parser)
        return super().parse(inp, config=config, context=context)


class Command[**P](ps.Command[P]):
    def parse(self, inp: str | list[str], *, config: ps.Config | None = None, context: Any = None) -> Route:  # type: ignore[override]  # ty: ignore[invalid-method-override]
        if not isinstance(inp, list):
            inp = shlex.split(inp)

        config = dataclasses.replace(config or ps.Config(), parser_class=Parser)
        return super().parse(inp, config=config, context=context)


class SimpleParser(Command[...]):
    def __init__(self, *args: Any, **kwargs: Any):
        def f() -> None: ...

        super().__init__(f)
        self.bind(*args, **kwargs)

    def __call__(self, inp: str | list[str]) -> ps.Handler:
        handler = super().parse(inp)[0]
        handler.func = ANY_FUNC
        return handler


# dumb and not recursive, ok
def track_call[**P, T](f: Callable[P, T]) -> Callable[P, T]:
    def _wrap(*args: P.args, **kwargs: P.kwargs) -> T:
        setattr(_wrap, "_called", True)
        return f(*args, **kwargs)

    return _wrap


@contextmanager
def ensure_called(func: Callable[..., Any]) -> Generator[None, None, None]:
    setattr(func, "_called", False)
    try:
        yield
        assert getattr(func, "_called") is True, f"{func!r} was not called"
    finally:
        delattr(func, "_called")


# Generic callable with "may by assigned to" type check

# mypy don't understand it


class assert_compat[T]:
    def __new__(cls, val: T) -> T:  # type: ignore[misc]
        return val


ensure_exit = pytest.raises(ParseExit)


@contextmanager
def set_env(key: str, value: str | None) -> Generator[None, None, None]:
    was = os.environ.get(key, ...)
    if value is not None:
        os.environ[key] = value
    else:
        os.environ.pop(key, None)
    try:
        yield
    finally:
        if was is not ...:
            os.environ[key] = was
        else:
            os.environ.pop(key, None)
