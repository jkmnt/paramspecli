from typing import Any

import pytest

from paramspecli import Handler, argument, flag, option, repeated_option

from .fix import Group, ParseError, ParseExit


def test_help() -> None:
    cli = Group(info="prog")

    def func(
        a: int,
        b: str,
        c: float,
        *,
        foo: int | None,
        bar: str | None,
        baz: str | None,
        f: bool,
        g: bool,
        e: bool,
    ) -> None: ...

    with cli.add_command("func", func) as cmd:
        preview = cmd.add_section("preview")
        extra = cmd.add_section("extra")
        flags = cmd.add_section("flags")
        _unused = cmd.add_section("unused")

        cmd.bind(
            -argument("A", type=int),
            -argument("B"),
            -argument("C", type=float),
            foo=-(option("--foo", type=int)[extra]),
            bar=-option("--bar")[preview],
            baz=-extra(option("--baz")),
            f=-flag("-f")[flags],
            g=-flag("-g")[flags],
            e=-flags.include(flag("-m") | flag("-n")),
        )

    assert cli.parse("func 42 b 4.33 --foo=12").nonempty == [
        Handler.from_spec(func, 42, "b", 4.33, foo=12, bar=None, baz=None, f=False, g=False, e=False),
    ]

    with pytest.raises(ParseExit):
        cli.parse("func --help")


def test_oneof() -> None:
    cli = Group(info="prog")

    def func(foo: int | None, bar: str | None, baz: str | None) -> None: ...

    with cli.add_command("func", func) as cmd:
        exclusive = cmd.add_oneof()
        _unused = cmd.add_oneof()

        cmd.bind(
            foo=-exclusive(option("--foo", type=int)),
            bar=-option("--bar"),
            baz=-exclusive(option("--baz")),
        )

    assert cli.parse("func --foo=12").nonempty == [
        Handler.from_spec(func, foo=12, bar=None, baz=None),
    ]

    with pytest.raises(ParseError, match="not allowed with"):
        cli.parse("func --foo=12 --baz=16")


def test_oneof_repeateds() -> None:
    cli = Group(info="prog")

    def func(foo: list[int], bar: str | None, baz: str | None) -> None: ...

    with cli.add_command("func", func) as cmd:
        exclusive = cmd.add_oneof()

        cmd.bind(
            foo=-exclusive.include(repeated_option("--foo", type=int)),
            bar=-option("--bar"),
            baz=-exclusive(option("--baz")),
        )

    assert cli.parse("func --foo=12 --foo 13").nonempty == [
        Handler.from_spec(func, foo=[12, 13], bar=None, baz=None),
    ]

    with pytest.raises(ParseError, match="not allowed with"):
        cli.parse("func --foo=12 --baz=16")


def test_required_oneof() -> None:
    cli = Group(info="prog")

    def func(foo: int | None, bar: str | None, baz: str | None) -> None: ...

    # required
    with cli.add_command("func", func) as cmd:
        exclusive = cmd.add_oneof(required=True)

        cmd.bind(
            foo=-exclusive.include(option("--foo", type=int)),
            bar=-exclusive.include(option("--bar")),
            baz=-option("--baz"),
        )

    assert cli.parse("func --foo=12 --baz 1").nonempty == [
        Handler.from_spec(func, foo=12, bar=None, baz="1"),
    ]

    assert cli.parse("func --bar=13 --baz 1").nonempty == [
        Handler.from_spec(func, foo=None, bar="13", baz="1"),
    ]

    with pytest.raises(ParseError, match="is required"):
        cli.parse("func --baz 1")

    with pytest.raises(ParseError, match="not allowed with"):
        cli.parse("func --foo 12 --bar 13")


def test_oneof_mixed() -> None:
    cli = Group(info="prog")

    def func(foobar: int | str | None) -> None: ...

    with cli.add_command("func", func) as cmd:
        exclusive = cmd.add_oneof()

        cmd.bind(
            foobar=-exclusive(
                option("--foo", type=int) | option("--bar"),
            ),
        )

    assert cli.parse("func").nonempty == [
        Handler.from_spec(func, foobar=None),
    ]

    assert cli.parse("func --foo 12").nonempty == [
        Handler.from_spec(func, foobar=12),
    ]

    assert cli.parse("func --bar a").nonempty == [
        Handler.from_spec(func, foobar="a"),
    ]

    # cli.parse("func --help")
    with pytest.raises(ParseError, match="not allowed with"):
        cli.parse("func --foo 12 --bar a")


def test_required_oneof_mixed() -> None:
    cli = Group(info="prog")

    # NOTE: in this specific case real type is int | str. None is impossible
    def func(foobar: int | str | None) -> None: ...

    with cli.add_command("func", func) as cmd:
        exclusive = cmd.add_oneof(required=True)

        cmd.bind(foobar=-exclusive(option("--foo", type=int) | option("--bar")))

    with pytest.raises(ParseError, match="is required"):
        cli.parse("func")

    assert cli.parse("func --foo 12").nonempty == [
        Handler.from_spec(func, foobar=12),
    ]

    assert cli.parse("func --bar a").nonempty == [
        Handler.from_spec(func, foobar="a"),
    ]

    with pytest.raises(ParseError, match="not allowed with"):
        cli.parse("func --foo 12 --bar a")


def test_oneof_mixed_repeateds() -> None:
    cli = Group(info="prog")

    def func(foobar: list[int | str]) -> None: ...

    with cli.add_command("func", func) as cmd:
        exclusive = cmd.add_oneof()

        cmd.bind(
            foobar=-exclusive(
                repeated_option("--foo", type=int) + repeated_option("--bar"),
            ),
        )

    assert cli.parse("func").nonempty == [
        Handler.from_spec(func, foobar=[]),
    ]

    assert cli.parse("func --foo 12 --foo 13").nonempty == [
        Handler.from_spec(func, foobar=[12, 13]),
    ]

    assert cli.parse("func --bar a --bar b").nonempty == [
        Handler.from_spec(func, foobar=["a", "b"]),
    ]

    # cli.parse("func --help")
    with pytest.raises(ParseError, match="not allowed with"):
        cli.parse("func --foo 12 --bar a")


def test_required_oneof_mixed_repeateds() -> None:
    cli = Group(info="prog")

    # NOTE: in this specific case real type is list[int] | list[str]
    def func(foobar: list[int | str], baz: list[str]) -> None: ...

    #
    with cli.add_command("func", func) as cmd:
        # test help_group too

        hlp = cmd.add_section("oneof")
        ex1 = cmd.add_oneof(required=True)
        ex2 = cmd.add_oneof(required=True)

        cmd.bind(
            foobar=-(
                #
                ex1(repeated_option("--foo", type=int)) + ex1(repeated_option("--bar"))
            )[hlp],
            baz=-ex2(repeated_option("--baz"))[hlp],
        )

    with pytest.raises(ParseError, match="is required"):
        cli.parse("func")

    assert cli.parse("func --foo 12 --foo 13 --baz c --baz c").nonempty == [
        Handler.from_spec(
            func,
            foobar=[12, 13],
            baz=["c", "c"],
        ),
    ]

    assert cli.parse("func --bar a --bar b --baz c --baz c").nonempty == [
        Handler.from_spec(
            func,
            foobar=["a", "b"],
            baz=["c", "c"],
        ),
    ]

    with pytest.raises(ParseError, match="not allowed with"):
        cli.parse("func --foo 12 --bar a")

    with pytest.raises(ParseError, match="is required"):
        cli.parse("func --foo 12")


def test_group_help() -> None:
    cli = Group(info="prog")

    def f(**kwargs: Any) -> None: ...

    def g(**kwargs: Any) -> None: ...

    with cli.add_callable_group("g", func=g) as group:
        opts = group.add_section("extra")
        bar_or_far = group.add_oneof()
        baz_or_faz = group.add_oneof()
        required_must = group.add_oneof(required=True)

        group.bind(
            foo=option("--foo", type=int)[opts],
            bar=bar_or_far(option("--bar")),
            far=bar_or_far(option("--far")),
            baz=baz_or_faz(option("--baz")[opts]),
            faz=baz_or_faz(option("--faz")[opts]),
            must=required_must(flag("--must")),
        )

        group.add_command("cmd", f).bind()

    assert cli.parse("g --foo 12 --bar 13 --baz 14 --must cmd").nonempty[0] == Handler.from_spec(
        g,
        foo=12,
        bar="13",
        far=None,
        baz="14",
        faz=None,
        must=True,
    )

    assert cli.parse("g --far 13 --baz 14 --must cmd").nonempty[0] == Handler.from_spec(
        g,
        foo=None,
        bar=None,
        far="13",
        baz="14",
        faz=None,
        must=True,
    )

    with pytest.raises(ParseError, match="not allowed"):
        cli.parse("g --bar 12 --far 13 --baz 14 --must cmd")
    with pytest.raises(ParseError, match="not allowed"):
        cli.parse("g --bar 12 --baz 14 --faz 15 --must cmd")


def test_sections_collision() -> None:
    cli = Group()

    def func(**kwargs: Any) -> None: ...

    with cli.add_command("func", func) as cmd:
        helpy = cmd.add_section("helpy")
        unhelpy = cmd.add_section("unhelpy")

        cmd.bind(
            foo=-(option("--foo")[helpy][unhelpy]),
            moo=-(option("--foo")[helpy][unhelpy]),
        )

    with pytest.raises(KeyError, match="in several sections at once"):
        cli.parse("func --help")


def test_oneofs_collision() -> None:
    cli = Group()

    def func(**kwargs: Any) -> None: ...

    with cli.add_command("func", func) as cmd:
        oneof_a = cmd.add_oneof()
        oneof_b = cmd.add_oneof()

        cmd.bind(
            foo=-oneof_a(oneof_b(option("--foo"))),
        )

    with pytest.raises(KeyError, match="in several oneofs at once"):
        cli.parse("")


def test_nonorthogonal_oneofs() -> None:
    cli = Group()

    def func(**kwargs: Any) -> None: ...

    with cli.add_command("func", func) as cmd:
        helpy = cmd.add_section("helpy")
        unhelpy = cmd.add_section("unhelpy")
        oneof = cmd.add_oneof()

        cmd.bind(
            foo=-oneof(option("--foo")[helpy]),
            bar=-oneof(option("--bar")[unhelpy]),
        )

    with pytest.raises(KeyError, match="should belong to the same section"):
        cli.parse("")


def test_unconsumed() -> None:
    cli = Group()

    def func(**kwargs: Any) -> None: ...

    with cli.add_command("func", func) as cmd:
        helpy = cmd.add_section("helpy")
        helpy.include(flag("--boo"))

        cmd.bind(bar=-option("--bar")[helpy])

    with pytest.raises(KeyError, match="unconsumed"):
        cli.parse("")
