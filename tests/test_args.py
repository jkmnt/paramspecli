import os
from typing import assert_type

from paramspecli import Handler, argument

from .fix import SimpleParser, assert_compat


def test__() -> None:
    p = SimpleParser(
        assert_compat[str](
            assert_type(
                argument("foo").t,
                str,
            )
        ),
    )
    assert p("a") == Handler.from_spec(None, "a")


def test__nargs() -> None:
    p = SimpleParser(
        assert_compat[list[str]](
            assert_type(
                -argument("foo", nargs=1),
                list[str],
            )
        ),
    )
    assert p("a") == Handler.from_spec(None, ["a"])

    p = SimpleParser(
        assert_compat[list[str]](
            assert_type(
                -argument("foo", nargs="*"),
                list[str],
            )
        ),
    )
    assert p("a") == Handler.from_spec(None, ["a"])
    assert p("a b") == Handler.from_spec(None, ["a", "b"])

    p = SimpleParser(
        assert_compat[list[str]](
            assert_type(
                -argument("foo", nargs="+"),
                list[str],
            )
        ),
    )
    assert p("a") == Handler.from_spec(None, ["a"])
    assert p("a b") == Handler.from_spec(None, ["a", "b"])


def test__optional() -> None:
    p = SimpleParser(
        assert_compat[str | None](
            assert_type(
                -argument("foo", nargs="?"),
                str | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, None)
    assert p("a") == Handler.from_spec(None, "a")


def test__optional__default_D() -> None:
    p = SimpleParser(
        assert_compat[str | int](
            assert_type(
                -argument("foo", nargs="?", default=123),
                str | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, 123)
    assert p("a") == Handler.from_spec(None, "a")


def test__type_T() -> None:
    p = SimpleParser(
        assert_compat[int](
            assert_type(
                -argument("foo", type=int),
                int,
            )
        ),
    )
    assert p("123") == Handler.from_spec(None, 123)


def test__type_T__nargs() -> None:
    p = SimpleParser(
        assert_compat[list[int]](
            assert_type(
                -argument("foo", type=int, nargs=1),
                list[int],
            )
        ),
    )
    assert p("123") == Handler.from_spec(None, [123])

    p = SimpleParser(
        assert_compat[list[int]](
            assert_type(
                -argument("foo", type=int, nargs=2),
                list[int],
            )
        ),
    )
    assert p("123 456") == Handler.from_spec(None, [123, 456])


def test__type_T__optional() -> None:
    p = SimpleParser(
        assert_compat[int | None](
            assert_type(
                -argument("foo", type=int, nargs="?"),
                int | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, None)
    assert p("123") == Handler.from_spec(None, 123)


def test__type_T__optional__str() -> None:
    p = SimpleParser(
        assert_compat[int](
            assert_type(
                -argument("foo", type=int, nargs="?", default="12"),
                int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, 12)
    assert p("123") == Handler.from_spec(None, 123)


def test__type_T__optional__default_D() -> None:
    p = SimpleParser(
        assert_compat[int | type[int]](
            assert_type(
                -argument("foo", type=int, nargs="?", default=int),
                int | type[int],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, int)
    assert p("123") == Handler.from_spec(None, 123)

    p = SimpleParser(
        assert_compat[int | None](
            assert_type(
                -argument("foo", type=int, nargs="?", default=os.environ.get("__REALLY_ABSENT_ENVVAR")),
                int | None,
            )
        ),
    )

    assert p("") == Handler.from_spec(None, None)

    p = SimpleParser(
        assert_compat[int](
            assert_type(
                -argument("--foo", type=int, nargs="?", default=os.environ.get("__REALLY_ABSENT_ENVVAR", 4)),
                int,
            )
        ),
    )

    assert p("") == Handler.from_spec(None, 4)


def test_choices() -> None:
    p = SimpleParser(
        assert_compat[str](
            assert_type(
                -argument("--foo", choices=("1",)),
                str,
            )
        ),
    )
    assert p("1") == Handler.from_spec(None, "1")

    p = SimpleParser(
        assert_compat[list[str]](
            assert_type(
                -argument("--foo", nargs="*", choices=tuple("abcd")),
                list[str],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, [])
    assert p("a b c d") == Handler.from_spec(None, ["a", "b", "c", "d"])

    p = SimpleParser(
        assert_compat[int](
            assert_type(
                -argument("--foo", type=int, choices=(1,)),
                int,
            )
        ),
    )
    assert p("1") == Handler.from_spec(None, 1)

    p = SimpleParser(
        assert_compat[list[int]](
            assert_type(
                -argument("--foo", type=int, choices=(1, 2), nargs=2),
                list[int],
            )
        ),
    )
    assert p("1 2") == Handler.from_spec(None, [1, 2])

    p = SimpleParser(
        assert_compat[int | None](
            assert_type(
                -argument("--foo", type=int, choices=tuple(range(-100, 100)), nargs="?"),
                int | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, None)
    assert p("1") == Handler.from_spec(None, 1)


def test_hash() -> None:
    a = argument("a")

    s = {a}

    assert a in s
