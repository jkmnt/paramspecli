import sys

import pytest

from paramspecli import Handler, argument, flag, option
from paramspecli.util import resolve_later

from .fix import Command, Group, ParseError


def test_simple() -> None:
    cli = Group(info="prog")

    def f1(a: str, *, foo: int | None) -> None: ...
    def f2(a: list[str], *, foo: str | None, bar: list[int] | None) -> None: ...

    with cli.add_command("f1", f1, help="f1") as cmd1:
        cmd1.bind(
            -argument("A"),
            foo=-option("--foo", type=int),
        )

    with cli.add_command("f2", f2, help="f2") as cmd2:
        cmd2.bind(
            -argument("B", nargs="*"),
            foo=-option("--foo"),
            bar=-option("--bar", type=int, nargs="+"),
        )

    assert cli.parse("f1 a --foo=12").nonempty == [
        Handler.from_spec(f1, "a", foo=12),
    ]

    assert cli.parse("f2 a b --bar 12 13").nonempty == [
        Handler.from_spec(f2, ["a", "b"], bar=[12, 13], foo=None),
    ]


def test_simple_group() -> None:
    cli = Group(info="prog")

    def f1(a: str, *, foo: int | None) -> None: ...
    def f2(a: list[str], *, foo: str | None, bar: list[int] | None) -> None: ...

    with cli.add_group("A", help="GA") as group:
        group.add_command("nop", sys.exit, help="nop").bind(-argument("status"))

    with cli.add_group("B", help="GB") as group:
        with group.add_command("f1", f1, help="f1") as cmd1:
            cmd1.bind(
                -argument("A"),
                foo=-option("--foo", type=int),
            )
        with group.add_command("f2", f2, help="f2") as cmd2:
            cmd2.bind(
                -argument("B", nargs="*"),
                foo=-option("--foo"),
                bar=-option("--bar", type=int, nargs="+"),
            )

    assert cli.parse("A nop 1").nonempty == [
        Handler.from_spec(sys.exit, "1"),
    ]

    assert cli.parse("B f1 a").nonempty == [
        Handler.from_spec(f1, "a", foo=None),
    ]

    assert cli.parse("B f2 b").nonempty == [
        Handler.from_spec(f2, ["b"], foo=None, bar=None),
    ]


def test_direct_add() -> None:
    cli = Group(info="prog")

    def f1(a: str, *, foo: int | None) -> None: ...
    def f2(a: list[str], *, foo: str | None, bar: list[int] | None) -> None: ...

    group_a = Group(help="GA")
    cmd_exit = Command(sys.exit, help="nop")
    cmd_exit.bind(-argument("status"))

    group_a["nop"] = cmd_exit

    group_b = Group(help="GB")
    cmd1 = Command(f1, help="f1")

    cmd1.bind(
        -argument("A"),
        foo=-option("--foo", type=int),
    )

    cmd2 = Command(f2, help="f2")
    cmd2.bind(
        -argument("B", nargs="*"),
        foo=-option("--foo"),
        bar=-option("--bar", type=int, nargs="+"),
    )

    group_b.nodes = {
        "f1": cmd1,
        "f2": cmd2,
    }

    cli.nodes = {
        "A": group_a,
        "B": group_b,
    }

    assert cli.parse("A nop 1").nonempty == [
        Handler.from_spec(sys.exit, "1"),
    ]

    assert cli.parse("B f1 a").nonempty == [
        Handler.from_spec(f1, "a", foo=None),
    ]

    assert cli.parse("B f2 b").nonempty == [
        Handler.from_spec(f2, ["b"], foo=None, bar=None),
    ]


def test_aliases() -> None:
    cli = Group(info="prog")

    def f1(a: str) -> None: ...
    def f2(a: list[str]) -> None: ...

    with cli.add_command(("f1", "my_command"), f1, help="f1") as cmd1:
        cmd1.bind(
            -argument("A"),
        )

    cmd2 = Command(f2, help="f2")
    cmd2.bind(
        -argument("B", nargs="*"),
    )

    cli["f2", "my_other_command"] = cmd2

    with cli.add_group(("g", "my_group"), help="g") as group:
        group["c"] = cmd2

    assert cli.parse("f1 a").nonempty == [
        Handler.from_spec(f1, "a"),
    ]
    assert cli.parse("my_command a").nonempty == [
        Handler.from_spec(f1, "a"),
    ]
    assert cli.parse("f2 a b").nonempty == [
        Handler.from_spec(f2, ["a", "b"]),
    ]
    assert cli.parse("my_other_command a b").nonempty == [
        Handler.from_spec(f2, ["a", "b"]),
    ]

    assert cli.parse("g c a").nonempty == [
        Handler.from_spec(f2, ["a"]),
    ]
    assert cli.parse("my_group c a").nonempty == [
        Handler.from_spec(f2, ["a"]),
    ]


def test_lazy_import() -> None:
    def load():  # type: ignore[no-untyped-def]
        from . import _later

        return _later.func

    cli = Command(resolve_later(load))
    cli.bind(
        foo=-option("--foo", type=int, default=1),
        bar=-option("--bar", default="a"),
    )

    assert "tests._later" not in sys.modules

    with pytest.raises(NotImplementedError):
        cli.parse("--foo 1")()

    assert "tests._later" in sys.modules


def test_required_command() -> None:
    def f() -> None: ...

    cli = Group(default_func=None)

    cli.add_command("f1", f).bind()
    cli.add_command("f2", f).bind()

    with pytest.raises(ParseError, match="arguments are required"):
        cli.parse("")


def test_third_party() -> None:
    def f(a: str, b: int | None, *, foo: bool) -> None:
        pass

    cli = Command(f)
    cli.bind(
        a=-option("--a", default="!"),
        b=-option("--b", type=int),
        foo=-flag("--foo"),
    )

    res = cli.parse("--b 1 --foo")
    assert res.handlers == [
        Handler.from_spec(f, a="!", b=1, foo=True),
    ]

    res()
