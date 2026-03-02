from typing import assert_type

from paramspecli import Handler, count, flag, repeated_flag, switch

from .fix import SimpleParser, assert_compat

###


def test_flag__() -> None:
    p = SimpleParser(
        foo=assert_compat[bool](
            assert_type(
                -flag("--foo", "-f"),
                bool,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=False)
    assert p("--foo") == Handler.from_spec(None, foo=True)
    assert p("-f") == Handler.from_spec(None, foo=True)


def test_flag__value_bool() -> None:
    p = SimpleParser(
        foo=assert_compat[bool](
            assert_type(
                -flag("--foo", value=False),
                bool,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=True)
    assert p("--foo") == Handler.from_spec(None, foo=False)

    p = SimpleParser(
        foo=assert_compat[bool](
            assert_type(
                -flag("--foo", value=True),
                bool,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=False)
    assert p("--foo") == Handler.from_spec(None, foo=True)


def test_flag__value_T() -> None:
    p = SimpleParser(
        foo=assert_compat[int | None](
            assert_type(
                -flag("--foo", value=1),
                int | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo") == Handler.from_spec(None, foo=1)

    p = SimpleParser(
        foo=assert_compat[str | None](
            assert_type(
                -flag("--foo", value="12"),
                str | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo") == Handler.from_spec(None, foo="12")


def test_flag__value_T__default_D() -> None:
    p = SimpleParser(
        foo=assert_compat[int | str](
            assert_type(
                -flag("--foo", value=4, default="12"),
                int | str,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo="12")
    assert p("--foo") == Handler.from_spec(None, foo=4)


def test_flag__default_D() -> None:
    p = SimpleParser(
        foo=assert_compat[bool | str](
            assert_type(
                -flag("--foo", default="12"),
                bool | str,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo="12")
    assert p("--foo") == Handler.from_spec(None, foo=True)


def test_switch__() -> None:
    p = SimpleParser(
        foo=assert_compat[bool](
            assert_type(
                -switch("--foo"),
                bool,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=False)
    assert p("--foo") == Handler.from_spec(None, foo=True)
    assert p("--no-foo") == Handler.from_spec(None, foo=False)


def test_switch__default_D() -> None:
    p = SimpleParser(
        foo=assert_compat[bool](
            assert_type(
                -switch("--foo", default=True),
                bool,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=True)
    assert p("--foo") == Handler.from_spec(None, foo=True)
    assert p("--no-foo") == Handler.from_spec(None, foo=False)

    p = SimpleParser(
        foo=assert_compat[bool](
            assert_type(
                -switch("--foo", default=False),
                bool,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=False)
    assert p("--foo") == Handler.from_spec(None, foo=True)
    assert p("--no-foo") == Handler.from_spec(None, foo=False)

    p = SimpleParser(
        foo=assert_compat[bool | None](
            assert_type(
                -switch("--foo", default=None),
                bool | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo") == Handler.from_spec(None, foo=True)
    assert p("--no-foo") == Handler.from_spec(None, foo=False)

    p = SimpleParser(
        foo=assert_compat[bool | int](
            assert_type(
                -switch("--foo", default=13),
                bool | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=13)
    assert p("--foo") == Handler.from_spec(None, foo=True)
    assert p("--no-foo") == Handler.from_spec(None, foo=False)


def test_count__() -> None:
    p = SimpleParser(
        v=assert_compat[int](
            assert_type(
                -count("-v"),
                int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, v=0)
    assert p("-v") == Handler.from_spec(None, v=1)
    assert p("-vv") == Handler.from_spec(None, v=2)
    assert p("-vvvvvvvv") == Handler.from_spec(None, v=8)

    p = SimpleParser(
        v=assert_compat[int](
            assert_type(
                -count("-v", default=1),
                int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, v=1)
    assert p("-v") == Handler.from_spec(None, v=2)

    p = SimpleParser(
        v=assert_compat[int](
            assert_type(
                -count("-v", default=-10),
                int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, v=-10)
    assert p("-v") == Handler.from_spec(None, v=-9)


def test_count__default_None() -> None:
    p = SimpleParser(
        v=assert_compat[int | None](
            assert_type(
                -count("-v", default=None),
                int | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, v=None)
    assert p("-v") == Handler.from_spec(None, v=1)
    assert p("-vv") == Handler.from_spec(None, v=2)


def test_repeated_flag__() -> None:
    p = SimpleParser(
        foo=assert_compat[list[bool]](
            assert_type(
                -repeated_flag("--foo"),
                list[bool],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=[])
    assert p("--foo") == Handler.from_spec(None, foo=[True])
    assert p("--foo --foo") == Handler.from_spec(None, foo=[True] * 2)
    assert p("--foo " * 32) == Handler.from_spec(None, foo=[True] * 32)


def test_repeated_flag__value_T() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int]](
            assert_type(
                -repeated_flag("--foo", value=12),
                list[int],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=[])
    assert p("--foo") == Handler.from_spec(None, foo=[12])
    assert p("--foo --foo") == Handler.from_spec(None, foo=[12] * 2)
    assert p("--foo " * 32) == Handler.from_spec(None, foo=[12] * 32)


def test_with_another() -> None:
    # ensure dunder is accepted
    assert_compat[bool](
        assert_type(
            -(flag("--foo") | flag("--bar")),
            bool,
        )
    )

    p = SimpleParser(
        foobar=assert_compat[bool](
            assert_type(
                -(flag("--foo") | flag("--bar")),
                bool,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foobar=False)
    assert p("--foo") == Handler.from_spec(None, foobar=True)
    assert p("--bar") == Handler.from_spec(None, foobar=True)
    assert p("--foo --bar") == Handler.from_spec(None, foobar=True)
    assert p("--foo --foo --bar") == Handler.from_spec(None, foobar=True)

    p = SimpleParser(
        foobar=assert_compat[str | int | None](
            assert_type(
                -(flag("--foo", value="4") | flag("--bar", value=12)),
                str | int | None,
            )
        )
    )

    assert p("") == Handler.from_spec(None, foobar=None)
    assert p("--foo") == Handler.from_spec(None, foobar="4")
    assert p("--bar") == Handler.from_spec(None, foobar=12)
    assert p("--foo --bar") == Handler.from_spec(None, foobar=12)
    assert p("--foo --bar --foo") == Handler.from_spec(None, foobar="4")


def test_with_another_repeated() -> None:
    p = SimpleParser(
        foobar=assert_compat[list[str | int]](
            assert_type(
                -(
                    #
                    repeated_flag("--foo", value="a") + repeated_flag("--bar", value=12)
                ),
                list[str | int],
            )
        )
    )
    assert p("") == Handler.from_spec(None, foobar=[])
    assert p("--foo") == Handler.from_spec(None, foobar=["a"])
    assert p("--bar") == Handler.from_spec(None, foobar=[12])
    assert p("--foo --foo --bar --foo") == Handler.from_spec(None, foobar=["a", "a", 12, "a"])
