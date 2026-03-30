import os
import tomllib
from dataclasses import dataclass
from typing import Any, assert_type

from paramspecli import (
    MISSING,
    Handler,
    Missing,
    ParseAgain,
    const,
    custom_action,
    option,
    repeated_option,
    util,
)

from .fix import ANY_FUNC, Command, set_env


def test_load_smoke() -> None:
    def f(foobar: int | str | None) -> None:
        pass

    loaded_foo: int | Missing = MISSING

    def load_foobar(*, context: Any) -> int | Missing:
        nonlocal loaded_foo
        return loaded_foo

    cli = Command(f)
    cli.bind(
        foobar=assert_type(
            -(
                const(load=load_foobar)
                #
                | option("--foo")
                | option("--bar", type=int)
            ),
            int | str | None,
        ),
    )

    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foobar=None)]
    assert cli.parse("--foo a").nonempty == [Handler.from_spec(ANY_FUNC, foobar="a")]
    assert cli.parse("--bar 2").nonempty == [Handler.from_spec(ANY_FUNC, foobar=2)]

    loaded_foo = 4
    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foobar=4)]
    assert cli.parse("--foo a").nonempty == [Handler.from_spec(ANY_FUNC, foobar="a")]
    assert cli.parse("--bar 2").nonempty == [Handler.from_spec(ANY_FUNC, foobar=2)]


def test_load_repeated_smoke() -> None:
    def f(foobar: int | list[str | int] | None) -> None:
        pass

    loaded_foobar: int | Missing = MISSING

    def load_foobar(*, context: Any) -> int | Missing:
        nonlocal loaded_foobar
        return loaded_foobar

    cli = Command(f)
    cli.bind(
        foobar=assert_type(
            -(const(load=load_foobar) | repeated_option("--foo") + repeated_option("--bar", type=int)),
            int | list[str | int] | None,
        ),
    )

    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foobar=None)]
    assert cli.parse("--foo a --bar 1 --foo c").nonempty == [Handler.from_spec(ANY_FUNC, foobar=["a", 1, "c"])]

    loaded_foobar = 4
    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foobar=4)]
    assert cli.parse("--foo a --bar 1 --foo c").nonempty == [Handler.from_spec(ANY_FUNC, foobar=["a", 1, "c"])]


def test_load_with_ctx() -> None:
    def f(foo: int | str | None) -> None:
        pass

    def load_foo(*, context: dict[str, Any]) -> int:
        context["loaded"] = True
        cfg = context.get("config")
        if cfg:
            return 2
        return 1

    def load_ctx(*, context: dict[str, Any], value: str, **kwargs: Any) -> None:
        if "config" not in context:
            context["config"] = value
            raise ParseAgain

    cli = Command(f)
    cli.bind(
        foo=assert_type(
            -(const(load=load_foo) | option("--foo")),
            int | str | None,
        ),
    )
    cli.append_action(custom_action("--config", handler=load_ctx))

    ctx: dict[str, Any] = {}
    assert cli.parse("", context=ctx).nonempty == [Handler.from_spec(ANY_FUNC, foo=1)]
    assert ctx["loaded"] is True

    ctx = {}
    assert cli.parse("--foo a", context=ctx).nonempty == [Handler.from_spec(ANY_FUNC, foo="a")]
    assert ctx["loaded"] is True
    assert "config" not in ctx

    ctx = {}
    assert cli.parse("--config my.toml", context=ctx).nonempty == [Handler.from_spec(ANY_FUNC, foo=2)]
    assert ctx["loaded"] is True
    assert ctx["config"] == "my.toml"

    ctx = {}
    assert cli.parse("--config my.toml --foo=a", context=ctx).nonempty == [Handler.from_spec(ANY_FUNC, foo="a")]
    assert ctx["loaded"] is True
    assert ctx["config"] == "my.toml"


def test_just_load() -> None:
    def f(foobar: int | Missing) -> None:
        pass

    loaded_foo: int | Missing = MISSING

    def load_foobar(*, context: Any) -> int | Missing:
        nonlocal loaded_foo
        return loaded_foo

    cli = Command(f)
    cli.bind(
        foobar=assert_type(
            -const(load=load_foobar),
            int | Missing,
        ),
    )

    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foobar=MISSING)]

    loaded_foo = 4
    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foobar=4)]


def test_just_load_nonmissing() -> None:
    def f(foobar: int) -> None:
        pass

    loaded_foo: int | Missing = MISSING

    def load_foobar(*, context: Any) -> int | Missing:
        nonlocal loaded_foo
        return loaded_foo

    cli = Command(f)
    cli.bind(
        foobar=assert_type(
            -const(load=load_foobar, default=1234),
            int,
        ),
    )

    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foobar=1234)]

    loaded_foo = 4
    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foobar=4)]


def test_load_and_const() -> None:
    def f(foo: int | str) -> None:
        pass

    loaded_foo: int | Missing = MISSING

    def load_foo(*, context: Any) -> int | Missing:
        nonlocal loaded_foo
        return loaded_foo

    cli = Command(f)
    cli.bind(
        foo=assert_type(
            -(const(load=load_foo, default=42) | option("--foo")),
            int | str,
        ),
    )

    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foo=42)]
    assert cli.parse("--foo a").nonempty == [Handler.from_spec(ANY_FUNC, foo="a")]

    loaded_foo = 4
    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, foo=4)]
    assert cli.parse("--foo a").nonempty == [Handler.from_spec(ANY_FUNC, foo="a")]


def test_load_from_env() -> None:
    def f(password: str) -> None:
        pass

    cli = Command(f)
    cli.bind(
        password=assert_type(
            -(
                const(load=lambda context: os.environ.get("MY_PASSWORD", MISSING), default="qwerty")
                #
                | option("--password")
            ),
            str,
        ),
    )

    with set_env("MY_PASSWORD", None):
        assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, password="qwerty")]
        assert cli.parse("--password PaSsWoRd").nonempty == [Handler.from_spec(ANY_FUNC, password="PaSsWoRd")]

    with set_env("MY_PASSWORD", "admin"):
        assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, password="admin")]
        assert cli.parse("--password PaSsWoRd").nonempty == [Handler.from_spec(ANY_FUNC, password="PaSsWoRd")]


# JSUT
def test_load_from_toml() -> None:
    def f(password: str | int) -> None:
        pass

    @dataclass
    class Ctx:
        toml: dict[str, dict[str, str]] | None = None

    def load_pass(context: Ctx) -> str | Missing:
        if not context.toml:
            return MISSING
        try:
            return context.toml["app"]["password"]
        except KeyError:
            return MISSING

    @util.catch_all
    def load_toml(context: Ctx, value: None, **kwargs: Any) -> None:
        # already 'loaded'
        if context.toml:
            return

        text = """\
[app]
password = "qwerty"
        """
        context.toml = tomllib.loads(text)
        raise ParseAgain

    cli = Command(f)
    cli.bind(
        password=assert_type(
            -(
                const(load=load_pass)
                #
                | option("--password", default=1234)
            ),
            str | int,
        ),
    )
    cli.append_action(custom_action("--toml", handler=load_toml, nargs=0))

    assert cli.parse("", context=Ctx()).nonempty == [Handler.from_spec(ANY_FUNC, password=1234)]
    assert cli.parse("--password PaSsWoRd", context=Ctx()).nonempty == [
        Handler.from_spec(ANY_FUNC, password="PaSsWoRd")
    ]

    assert cli.parse("--toml", context=Ctx()).nonempty == [Handler.from_spec(ANY_FUNC, password="qwerty")]
    assert cli.parse("--toml --password PaSsWoRd", context=Ctx()).nonempty == [
        Handler.from_spec(ANY_FUNC, password="PaSsWoRd")
    ]
