from typing import Any, assert_type

from paramspecli import Const, Handler, argument, option, switch

from .fix import ANY_FUNC, CallableGroup, Group


def test_const() -> None:
    cli = Group()

    def g(*, debug: bool, const: str, foo: str) -> None:
        pass

    def f(*, foo: str) -> None:
        pass

    with cli.add_callable_group("A", g) as group:
        group.bind(
            debug=-switch("--debug"),
            const=-Const("<boo>"),
            foo=-Const("<foo>"),
        )

        with group.add_command("f", f) as cmd:
            cmd.bind(foo=assert_type(-Const("<a>"), str))

    assert cli.parse("").nonempty == [
        Handler.from_spec(ANY_FUNC),
    ]

    assert cli.parse("A").nonempty == [
        Handler.from_spec(g, debug=False, const="<boo>", foo="<foo>"),
        Handler.from_spec(ANY_FUNC, debug=False, const="<boo>", foo="<foo>"),
    ]
    assert cli.parse("A --debug f").nonempty == [
        Handler.from_spec(g, debug=True, const="<boo>", foo="<foo>"),
        Handler.from_spec(f, foo="<a>"),
    ]


def test_frob_opt() -> None:
    cli = Group()

    def third_party_function(*, frob: bool, foo: int | None) -> None:
        pass

    with cli.add_command("frobnicate", third_party_function) as cmd:
        cmd.bind(
            frob=-Const(True),
            foo=-option("--foo", type=int),
        )

    res = cli.parse("frobnicate")
    res()
    assert res.nonempty[0].options["frob"] is True


def test_frob_arg() -> None:
    cli = Group()

    def third_party_function(frob: int, a: str, *, foo: int | None) -> None:
        pass

    with cli.add_command("frobnicate", third_party_function) as cmd:
        cmd.bind(
            -Const(2),
            -argument("a"),
            foo=-option("--foo", type=int),
        )

    res = cli.parse("frobnicate a")
    res()
    assert res.nonempty[0].arguments == [2, "a"]


def test_trace_group() -> None:
    def ignore(**kwargs: Any) -> None:
        pass

    cli = CallableGroup(ignore)
    cli.bind(path=-Const("root"))

    with cli.add_callable_group("a", func=ignore) as group:
        group.bind(path=Const("group_a"))

        with group.add_callable_group("c", func=ignore) as inner:
            inner.bind(path=Const("group_c"))

            with inner.add_callable_group("d", func=ignore) as inner2:
                inner2.bind(path=Const("group_d"))

    with cli.add_callable_group("b", func=ignore) as group:
        group.bind(path=Const("group_b"))

    res = cli.parse("a c d")
    assert res[0].options["path"] == "root"
    assert res[1].options["path"] == "group_a"
    assert res[2].options["path"] == "group_c"
    assert res[3].options["path"] == "group_d"


def test_cmp() -> None:
    a = Const("a")
    assert a == Const("a")
    assert a != "a"

