import os
from typing import assert_type

from paramspecli import Handler, argument

from .fix import SimpleParser, assert_compat


# 1.
# {'type': 'None', 'nargs': 'None'}
def test_1() -> None:
    p = SimpleParser(
        assert_compat[str](
            assert_type(
                argument("foo").t,
                str,
            )
        ),
    )
    assert p("a") == Handler.from_spec(None, "a")


# 2.
# {'type': 'None', 'nargs': 'int | Literal["*", "+"]'}
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


# 3.
# {'type': 'None', 'nargs': 'Literal["?"]', 'default': 'None'}
def test_3() -> None:
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


# 4.
# {'type': 'None', 'nargs': 'Literal["?"]', 'default': 'D'}
def test_4() -> None:
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


# 5.
# {'type': 'TypeConverter[T]', 'nargs': 'None'}
def test_5() -> None:
    p = SimpleParser(
        assert_compat[int](
            assert_type(
                -argument("foo", type=int),
                int,
            )
        ),
    )
    assert p("123") == Handler.from_spec(None, 123)


# 6.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]'}
def test_6() -> None:
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


# 7.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"', 'default': 'None'}
def test_7() -> None:
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


# 8.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"', 'default': 'str'}
def test_8() -> None:
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


# 9.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"', 'default': 'D'}
def test_9() -> None:
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


# 9.1, typing is off here, it fails
def test_9_union() -> None:
    p = SimpleParser(
        -argument("foo", type=int, nargs="?", default=os.environ.get("__REALLY_ABSENT_ENVVAR")),
    )

    assert p("") == Handler.from_spec(None, None)

    p = SimpleParser(
        -argument("--foo", type=int, nargs="?", default=os.environ.get("__REALLY_ABSENT_ENVVAR", 4)),
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
