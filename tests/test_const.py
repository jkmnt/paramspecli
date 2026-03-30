from typing import Any, assert_type

from paramspecli import Handler, argument, const, option, repeated_option, switch

from .fix import ANY_FUNC, CallableGroup, Command, Group


def test_const() -> None:
    cli = Group()

    def g(*, debug: bool, const: str, foo: str) -> None:
        pass

    def f(*, foo: str) -> None:
        pass

    with cli.add_callable_group("A", g) as group:
        group.bind(
            debug=-switch("--debug"),
            const=-const("<boo>"),
            foo=-const("<foo>"),
        )

        with group.add_command("f", f) as cmd:
            cmd.bind(foo=assert_type(-const("<a>"), str))

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
            frob=-const(True),
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
            -const(2),
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
    cli.bind(path=-const("root"))

    with cli.add_callable_group("a", func=ignore) as group:
        group.bind(path=const("group_a"))

        with group.add_callable_group("c", func=ignore) as inner:
            inner.bind(path=const("group_c"))

            with inner.add_callable_group("d", func=ignore) as inner2:
                inner2.bind(path=const("group_d"))

    with cli.add_callable_group("b", func=ignore) as group:
        group.bind(path=const("group_b"))

    res = cli.parse("a c d")
    assert res[0].options["path"] == "root"
    assert res[1].options["path"] == "group_a"
    assert res[2].options["path"] == "group_c"
    assert res[3].options["path"] == "group_d"


def test_cmp() -> None:
    a = const("a")
    assert a == const("a")
    assert a != "a"


def test_const_mix() -> None:
    def f(*, fooboo: int | str | float) -> None:
        pass

    assert_type(-(const("<foo>") | option("--foo", type=int, default=None)), str | int)
    assert_type(
        -(const("<foo>") | option("--foo", type=int, default=None) | option("--boo", type=float, default=None)),
        str | int | float,
    )
    assert_type(
        -(const("<foo>") | (option("--foo", type=int, default=None) | option("--boo", type=float, default=None))),
        str | int | float,
    )

    cli = Command(f)

    cli.bind(
        fooboo=assert_type(
            -(
                (const("<foo>") | option("--foo", type=int, default=None))
                #
                | option("--boo", type=float, default=None)
            ),
            int | str | float,
        ),
    )

    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, fooboo="<foo>")]
    assert cli.parse("--foo 1").nonempty == [Handler.from_spec(ANY_FUNC, fooboo=1)]
    assert cli.parse("--foo 3 --boo 3.4").nonempty == [Handler.from_spec(ANY_FUNC, fooboo=3.4)]

    cli = Command(f)

    cli.bind(
        fooboo=assert_type(
            -(
                const("<foo>")
                #
                | (option("--foo", type=int, default=None) | option("--boo", type=float, default=None))
            ),
            int | str | float,
        ),
    )

    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, fooboo="<foo>")]
    assert cli.parse("--foo 1").nonempty == [Handler.from_spec(ANY_FUNC, fooboo=1)]
    assert cli.parse("--foo 3 --boo 3.4").nonempty == [Handler.from_spec(ANY_FUNC, fooboo=3.4)]


def test_const_repeated_mix() -> None:
    def f(*, fooboo: str | list[int | float]) -> None:
        pass

    cli = Command(f)

    cli.bind(
        fooboo=assert_type(
            -(
                (
                    const("<foo>")
                    #
                    | repeated_option("--foo", type=int)
                )
                + repeated_option("--boo", type=float)
            ),
            str | list[int | float],
        ),
    )

    assert cli.parse("").nonempty == [Handler.from_spec(ANY_FUNC, fooboo="<foo>")]
    assert cli.parse("--foo 1").nonempty == [Handler.from_spec(ANY_FUNC, fooboo=[1])]

    cli = Command(f)

    cli.bind(
        fooboo=assert_type(
            -(
                const("<foo>")
                #
                | (repeated_option("--foo", type=int) + repeated_option("--boo", type=float))
            ),
            str | list[int | float],
        ),
    )

    assert cli.parse("").nonempty == [
        Handler.from_spec(ANY_FUNC, fooboo="<foo>"),
    ]

    assert cli.parse("--foo 1").nonempty == [
        Handler.from_spec(ANY_FUNC, fooboo=[1]),
    ]

    assert cli.parse("--foo 3 --boo 3.4").nonempty == [
        Handler.from_spec(ANY_FUNC, fooboo=[3, 3.4]),
    ]
