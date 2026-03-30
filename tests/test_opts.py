import os
from enum import StrEnum
from ipaddress import IPv4Address
from typing import assert_type

import pytest

from paramspecli import Handler, option, repeated_option, required, t
from paramspecli.cli import MISSING, Missing

from .fix import ParseError, SimpleParser, assert_compat


# 1. {'type': 'None = None', 'nargs': 'None = None', 'default': 'None = None'}
def test_opt_1() -> None:
    assert_compat[str | None](
        assert_type(
            -option("--foo"),
            str | None,
        )
    )

    p = SimpleParser(
        foo=assert_compat[str | None](
            assert_type(
                -option("--foo"),
                str | None,
            )
        ),
    )

    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a") == Handler.from_spec(None, foo="a")


# 2. {'type': 'None = None', 'nargs': 'None = None', 'default': 'D'}
def test_opt_2() -> None:
    assert_type(-option("--foo", default="1"), str)

    p = SimpleParser(
        foo=assert_compat[str](
            assert_type(
                -option("--foo", default="1"),
                str,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo="1")
    assert p("--foo a") == Handler.from_spec(None, foo="a")

    p = SimpleParser(
        foo=assert_compat[str | int](
            assert_type(
                -option("--foo", default=1),
                str | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=1)
    assert p("--foo a") == Handler.from_spec(None, foo="a")

    p = SimpleParser(
        foo=assert_compat[str | list[int]](
            assert_type(
                -option("--foo", default=[1]),
                str | list[int],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=[1])
    assert p("--foo a") == Handler.from_spec(None, foo="a")

    p = SimpleParser(
        foo=assert_compat[str | None](
            assert_type(
                -option("--foo", default=None),
                str | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a") == Handler.from_spec(None, foo="a")
    assert p("--foo a --foo b") == Handler.from_spec(None, foo="b")

    p = SimpleParser(
        foo=assert_compat[str | None](
            assert_type(
                -option("--foo", default=os.environ.get("__REALLY_ABSENT_ENVVAR")),
                str | None,
            )
        ),
    )

    assert p("") == Handler.from_spec(None, foo=None)


# 3. {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'default': 'None = None'}
def test_opt_3() -> None:
    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -option("--foo", nargs=1),
                list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])
    with pytest.raises(ParseError, match="unrecognized argument"):
        p("--foo a b")

    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -option("--foo", nargs="+"),
                list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])
    assert p("--foo a b c") == Handler.from_spec(None, foo=["a", "b", "c"])

    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -option("--foo", nargs="*"),
                list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo") == Handler.from_spec(None, foo=[])
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])
    assert p("--foo a b c") == Handler.from_spec(None, foo=["a", "b", "c"])


# 4. {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'default': 'D'}
def test_opt_4() -> None:
    p = SimpleParser(
        foo=assert_compat[list[str]](
            assert_type(
                -option("--foo", nargs=1, default=["2"]),
                list[str],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=["2"])
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])
    with pytest.raises(ParseError, match="unrecognized argument"):
        p("--foo a b")

    p = SimpleParser(
        foo=assert_compat[list[str]](
            assert_type(
                -option("--foo", nargs="+", default=["2"]),
                list[str],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=["2"])
    assert p("--foo a b") == Handler.from_spec(None, foo=["a", "b"])

    p = SimpleParser(
        foo=assert_compat[list[str]](
            assert_type(
                -option("--foo", nargs="*", default=["2"]),
                list[str],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=["2"])
    assert p("--foo") == Handler.from_spec(None, foo=[])
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])
    assert p("--foo a b") == Handler.from_spec(None, foo=["a", "b"])

    p = SimpleParser(
        foo=assert_compat[list[str] | list[int]](
            assert_type(
                -option("--foo", nargs=1, default=[2]),
                list[str] | list[int],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=[2])
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])

    p = SimpleParser(
        foo=assert_compat[list[str] | int](
            assert_type(
                -option("--foo", nargs=1, default=3),
                list[str] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=3)
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])

    p = SimpleParser(
        foo=assert_compat[list[str]](
            assert_type(
                -option("--foo", nargs=1, default=[]),
                list[str],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=[])
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])

    p = SimpleParser(
        foo=assert_compat[list[str] | list[None]](
            assert_type(
                -option("--foo", nargs=1, default=[None]),
                list[str] | list[None],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=[None])
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])


# 5. {'type': 'None = None', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'None = None'}
def test_opt_5() -> None:
    p = SimpleParser(
        foo=assert_compat[str | None | Missing](
            assert_type(
                -option("--foo", nargs="?", const=MISSING),
                str | None | Missing,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a") == Handler.from_spec(None, foo="a")
    assert p("--foo") == Handler.from_spec(None, foo=MISSING)


# 6. {'type': 'None = None', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'D'}
def test_opt_6() -> None:
    p = SimpleParser(
        foo=assert_compat[str | int | float](
            assert_type(
                -option("--foo", nargs="?", default=2, const=3.3),
                str | int | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=2)
    assert p("--foo a") == Handler.from_spec(None, foo="a")
    assert p("--foo") == Handler.from_spec(None, foo=3.3)


# 7. {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'None = None'}
def test_opt_7() -> None:
    p = SimpleParser(
        foo=assert_compat[int | None](
            assert_type(
                -option("--foo", type=int),
                int | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1") == Handler.from_spec(None, foo=1)

    p = SimpleParser(
        foo=assert_compat[IPv4Address | None](
            assert_type(
                -option("--foo", type=IPv4Address),
                IPv4Address | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1.1.1.1") == Handler.from_spec(None, foo=IPv4Address("1.1.1.1"))

    def f_split(x: str) -> list[str]:
        return x.split(".")

    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -option("--foo", type=f_split),
                list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1.1.1.1") == Handler.from_spec(None, foo=["1", "1", "1", "1"])

    def f2(x: str) -> None:
        return None

    p = SimpleParser(
        foo=assert_compat[None](
            assert_type(
                -option("--foo", type=f2),
                None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a") == Handler.from_spec(None, foo=None)


# 8. {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'str'}
def test_opt_8() -> None:
    p = SimpleParser(
        foo=assert_compat[int](
            assert_type(
                -option("--foo", type=int, default="1"),
                int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=1)
    assert p("--foo 1") == Handler.from_spec(None, foo=1)

    p = SimpleParser(
        foo=assert_compat[IPv4Address](
            assert_type(
                -option("--foo", type=IPv4Address, default="1.1.1.1"),
                IPv4Address,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=IPv4Address("1.1.1.1"))
    assert p("--foo 2.2.2.2") == Handler.from_spec(None, foo=IPv4Address("2.2.2.2"))

    def f_split(x: str) -> list[str]:
        return x.split(".")

    p = SimpleParser(
        foo=assert_compat[list[str]](
            assert_type(
                -option("--foo", type=f_split, default="1.1"),
                list[str],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=["1", "1"])
    assert p("--foo 2.2") == Handler.from_spec(None, foo=["2", "2"])


# 9. {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'D'}
def test_opt_9() -> None:
    p = SimpleParser(
        foo=assert_compat[int | float](
            assert_type(
                -option("--foo", type=int, default=1.1),
                int | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=1.1)
    assert p("--foo 1") == Handler.from_spec(None, foo=1)

    p = SimpleParser(
        foo=assert_compat[int | None](
            assert_type(
                -option("--foo", type=int, default=None),
                int | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1") == Handler.from_spec(None, foo=1)

    p = SimpleParser(
        foo=assert_compat[IPv4Address | list[int]](
            assert_type(
                -option("--foo", type=IPv4Address, default=[1]),
                IPv4Address | list[int],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=[1])
    assert p("--foo 2.2.2.2") == Handler.from_spec(None, foo=IPv4Address("2.2.2.2"))

    def f_split(x: str) -> list[str]:
        return x.split(".")

    p = SimpleParser(
        foo=assert_compat[list[str] | int](
            assert_type(
                -option("--foo", type=f_split, default=42),
                list[str] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=42)
    assert p("--foo a.b") == Handler.from_spec(None, foo=["a", "b"])

    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -option("--foo", type=f_split, default=None),
                list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a.b") == Handler.from_spec(None, foo=["a", "b"])

    def f2(x: str) -> None:
        return None

    p = SimpleParser(
        foo=assert_compat[None | int](
            assert_type(
                -option("--foo", type=f2, default=4),
                None | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=4)
    assert p("--foo a.b.c.d") == Handler.from_spec(None, foo=None)

    p = SimpleParser(
        foo=assert_compat[None](
            assert_type(
                -option("--foo", type=f2, default=None),
                None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a.b.c.d") == Handler.from_spec(None, foo=None)


# This one is tricky - D is union.
# In runtime it's ok. typing is off
def test_opt_9__union() -> None:
    p = SimpleParser(
        foo=-option("--foo", type=int, default=os.environ.get("__REALLY_ABSENT_ENVVAR")),
    )

    assert p("") == Handler.from_spec(None, foo=None)

    p = SimpleParser(
        foo=-option("--foo", type=int, default=os.environ.get("__REALLY_ABSENT_ENVVAR", 4)),
    )

    assert p("") == Handler.from_spec(None, foo=4)

    p = SimpleParser(
        foo=-option("--foo", type=int, default=os.environ.get("__REALLY_ABSENT_ENVVAR", 0) or 3.3),
    )

    assert p("") == Handler.from_spec(None, foo=3.3)


# 10. {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'default': 'None = None'}
def test_opt_10() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int] | None](
            assert_type(
                -option("--foo", type=int, nargs=1),
                list[int] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1") == Handler.from_spec(None, foo=[1])

    p = SimpleParser(
        foo=assert_compat[list[int] | None](
            assert_type(
                -option("--foo", type=int, nargs="+"),
                list[int] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1 2 3") == Handler.from_spec(None, foo=[1, 2, 3])

    p = SimpleParser(
        foo=assert_compat[list[int] | None](
            assert_type(
                -option("--foo", type=int, nargs="*"),
                list[int] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo") == Handler.from_spec(None, foo=[])
    assert p("--foo 1 2 3") == Handler.from_spec(None, foo=[1, 2, 3])

    p = SimpleParser(
        foo=assert_compat[list[IPv4Address] | None](
            assert_type(
                -option("--foo", type=IPv4Address, nargs="+"),
                list[IPv4Address] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1.1.1.1 2.2.2.2") == Handler.from_spec(None, foo=[IPv4Address("1.1.1.1"), IPv4Address("2.2.2.2")])

    def f_split(x: str) -> list[str]:
        return x.split(".")

    p = SimpleParser(
        foo=assert_compat[list[list[str]] | None](
            assert_type(
                -option("--foo", type=f_split, nargs=1),
                list[list[str]] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1.1") == Handler.from_spec(None, foo=[["1", "1"]])

    def f_none(x: str) -> None:
        return None

    p = SimpleParser(
        foo=assert_compat[list[None] | None](
            assert_type(
                -option("--foo", type=f_none, nargs=1),
                list[None] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1.1") == Handler.from_spec(None, foo=[None])


# 11. {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'default': 'str'}
def test_opt_11() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int] | int](
            assert_type(
                -option("--foo", type=int, nargs=1, default="1"),
                list[int] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=1)
    assert p("--foo 1") == Handler.from_spec(None, foo=[1])

    p = SimpleParser(
        foo=assert_compat[list[int] | int](
            assert_type(
                -option("--foo", type=int, nargs="+", default="1"),
                list[int] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=1)
    assert p("--foo 1 2") == Handler.from_spec(None, foo=[1, 2])

    p = SimpleParser(
        foo=assert_compat[list[int] | int](
            assert_type(
                -option("--foo", type=int, nargs="*", default="1"),
                list[int] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=1)
    assert p("--foo") == Handler.from_spec(None, foo=[])
    assert p("--foo 1 2") == Handler.from_spec(None, foo=[1, 2])

    p = SimpleParser(
        foo=assert_compat[list[IPv4Address] | IPv4Address](
            assert_type(
                -option("--foo", type=IPv4Address, nargs=1, default="1.1.1.1"),
                list[IPv4Address] | IPv4Address,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=IPv4Address("1.1.1.1"))
    assert p("--foo 1.1.1.1") == Handler.from_spec(None, foo=[IPv4Address("1.1.1.1")])

    def f_split(x: str) -> list[str]:
        return x.split(".")

    p = SimpleParser(
        foo=assert_compat[list[list[str]] | list[str]](
            assert_type(
                -option("--foo", type=f_split, nargs=1, default="1.1"),
                list[list[str]] | list[str],
            )
        )
    )
    assert p("") == Handler.from_spec(None, foo=["1", "1"])
    assert p("--foo 2.2") == Handler.from_spec(None, foo=[["2", "2"]])

    def f_none(x: str) -> None:
        return None

    p = SimpleParser(
        foo=assert_compat[list[None] | None](
            assert_type(
                -option("--foo", type=f_none, nargs=1, default="1"),
                list[None] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 2.2") == Handler.from_spec(None, foo=[None])


# 12. {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'default': 'D'}
def test_opt_12() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int] | float](
            assert_type(
                -option("--foo", type=int, nargs=1, default=1.1),
                list[int] | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=1.1)
    assert p("--foo 2") == Handler.from_spec(None, foo=[2])

    p = SimpleParser(
        foo=assert_compat[list[int] | float](
            assert_type(
                -option("--foo", type=int, nargs="+", default=1.1),
                list[int] | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=1.1)
    assert p("--foo 2 3") == Handler.from_spec(None, foo=[2, 3])

    p = SimpleParser(
        foo=assert_compat[list[int] | float](
            assert_type(
                -option("--foo", type=int, nargs="*", default=1.1),
                list[int] | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=1.1)
    assert p("--foo") == Handler.from_spec(None, foo=[])
    assert p("--foo 2 3") == Handler.from_spec(None, foo=[2, 3])

    p = SimpleParser(
        foo=assert_compat[list[int] | None](
            assert_type(
                -option("--foo", type=int, nargs=1, default=None),
                list[int] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 2") == Handler.from_spec(None, foo=[2])

    p = SimpleParser(
        foo=assert_compat[list[IPv4Address] | list[int]](
            assert_type(
                -option("--foo", type=IPv4Address, nargs=1, default=[1]),
                list[IPv4Address] | list[int],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=[1])
    assert p("--foo 1.1.1.1") == Handler.from_spec(None, foo=[IPv4Address("1.1.1.1")])

    def f_split(x: str) -> list[str]:
        return x.split(".")

    p = SimpleParser(
        foo=assert_compat[list[list[str]] | int](
            assert_type(
                -option("--foo", type=f_split, nargs=1, default=42),
                list[list[str]] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=42)
    assert p("--foo 1.1") == Handler.from_spec(None, foo=[["1", "1"]])

    p = SimpleParser(
        foo=assert_compat[list[list[str]] | None](
            assert_type(
                -option("--foo", type=f_split, nargs=1, default=None),
                list[list[str]] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1.1") == Handler.from_spec(None, foo=[["1", "1"]])

    def f_none(x: str) -> None:
        return None

    p = SimpleParser(
        foo=assert_compat[list[None] | int](
            assert_type(
                -option("--foo", type=f_none, nargs=1, default=4),
                list[None] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=4)
    assert p("--foo 1.1") == Handler.from_spec(None, foo=[None])

    p = SimpleParser(
        foo=assert_compat[list[None] | None](
            assert_type(
                -option("--foo", type=f_none, nargs="+", default=None),
                list[None] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a b") == Handler.from_spec(None, foo=[None, None])

    p = SimpleParser(
        foo=assert_compat[list[None] | None](
            assert_type(
                -option("--foo", type=f_none, nargs="*", default=None),
                list[None] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo") == Handler.from_spec(None, foo=[])
    assert p("--foo a b") == Handler.from_spec(None, foo=[None, None])


# 13. {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'None = None'}
def test_opt_13() -> None:
    p = SimpleParser(
        foo=assert_compat[int | None | Missing](
            assert_type(
                -option("--foo", nargs="?", type=int, const=MISSING),
                int | None | Missing,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 2") == Handler.from_spec(None, foo=2)
    assert p("--foo") == Handler.from_spec(None, foo=MISSING)


# 14. {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'str'}
def test_opt_14() -> None:
    p = SimpleParser(
        foo=assert_compat[int | Missing](
            assert_type(
                -option("--foo", nargs="?", type=int, default="4", const=MISSING),
                int | Missing,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=4)
    assert p("--foo 2") == Handler.from_spec(None, foo=2)
    assert p("--foo") == Handler.from_spec(None, foo=MISSING)


# 15. {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'D'}
def test_opt_15() -> None:
    p = SimpleParser(
        foo=assert_compat[int | Missing | type[int]](
            assert_type(
                -option("--foo", nargs="?", type=int, default=int, const=MISSING),
                int | Missing | type[int],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=int)
    assert p("--foo 2") == Handler.from_spec(None, foo=2)
    assert p("--foo") == Handler.from_spec(None, foo=MISSING)


#


# 1.
# {'type': 'None = None', 'nargs': 'None = None', 'default': 'None = None'}
def test_repeated_1() -> None:
    # mypy fails to assert_compat for this line for some reason
    assert_type(t(repeated_option("--foo")), list[str] | None)

    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -repeated_option("--foo"),
                list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a --foo b") == Handler.from_spec(None, foo=["a", "b"])

    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -repeated_option("--foo", default=None),
                list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a --foo b") == Handler.from_spec(None, foo=["a", "b"])


# 2.
# {'type': 'None = None', 'nargs': 'None = None', 'default': 'D'}
def test_repeated_2() -> None:
    p = SimpleParser(
        foo=assert_compat[list[str] | int](
            assert_type(
                -repeated_option("--foo", default=22),
                list[str] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo a --foo b") == Handler.from_spec(None, foo=["a", "b"])


# 3.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'None = None'}
def test_repeated_3() -> None:
    p = SimpleParser(
        foo=assert_compat[list[list[str]] | None](
            assert_type(
                -repeated_option("--foo", nargs="+"),
                list[list[str]] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a --foo b --foo c d") == Handler.from_spec(None, foo=[["a"], ["b"], ["c", "d"]])

    p = SimpleParser(
        foo=assert_compat[list[list[str]] | None](
            assert_type(
                -repeated_option("--foo", nargs="*", default=None),
                list[list[str]] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo --foo") == Handler.from_spec(None, foo=[[], []])
    assert p("--foo a --foo b --foo c d") == Handler.from_spec(None, foo=[["a"], ["b"], ["c", "d"]])

    p = SimpleParser(
        foo=assert_compat[list[list[str]] | None](
            assert_type(
                -repeated_option("--foo", flatten=False, nargs=1),
                list[list[str]] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a --foo b --foo c") == Handler.from_spec(None, foo=[["a"], ["b"], ["c"]])


# 4.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'D'}
def test_repeated_4() -> None:
    p = SimpleParser(
        foo=assert_compat[list[list[str]] | int](
            assert_type(
                -repeated_option("--foo", nargs="+", default=22),
                list[list[str]] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo a --foo b --foo c d") == Handler.from_spec(None, foo=[["a"], ["b"], ["c", "d"]])

    p = SimpleParser(
        foo=assert_compat[list[list[str]] | int](
            assert_type(
                -repeated_option("--foo", nargs="*", default=22),
                list[list[str]] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo --foo") == Handler.from_spec(None, foo=[[], []])
    assert p("--foo a --foo b --foo c d") == Handler.from_spec(None, foo=[["a"], ["b"], ["c", "d"]])

    p = SimpleParser(
        foo=assert_compat[list[list[str]] | int](
            assert_type(
                -repeated_option("--foo", flatten=False, nargs=1, default=22),
                list[list[str]] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo a --foo b --foo c") == Handler.from_spec(None, foo=[["a"], ["b"], ["c"]])


# 5.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'None = None'}
def test_repeated_5() -> None:
    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -repeated_option("--foo", flatten=True, nargs="+"),
                list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo a --foo b --foo c d") == Handler.from_spec(None, foo=["a", "b", "c", "d"])

    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -repeated_option("--foo", flatten=True, nargs="*"),
                list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo --foo") == Handler.from_spec(None, foo=[])
    assert p("--foo a --foo b --foo c d") == Handler.from_spec(None, foo=["a", "b", "c", "d"])


# 6.
# {'type': 'None = None', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'D'}
def test_repeated_6() -> None:
    p = SimpleParser(
        foo=assert_compat[list[str] | int](
            assert_type(
                -repeated_option("--foo", flatten=True, nargs="+", default=22),
                list[str] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo a --foo b --foo c d") == Handler.from_spec(None, foo=["a", "b", "c", "d"])

    p = SimpleParser(
        foo=assert_compat[list[str] | int](
            assert_type(
                -repeated_option("--foo", flatten=True, nargs="*", default=22),
                list[str] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo --foo") == Handler.from_spec(None, foo=[])
    assert p("--foo a --foo b --foo c d") == Handler.from_spec(None, foo=["a", "b", "c", "d"])


# 7.
# {'type': 'None = None', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'None = None'}
def test_repeated_7() -> None:
    p = SimpleParser(
        foo=assert_compat[list[str | Missing] | None](
            assert_type(
                -repeated_option("--foo", nargs="?", const=MISSING),
                list[str | Missing] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo") == Handler.from_spec(None, foo=[MISSING])
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])
    assert p("--foo --foo --foo a --foo b") == Handler.from_spec(None, foo=[MISSING, MISSING, "a", "b"])


# 8.
# {'type': 'None = None', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'D'}
def test_repeated_8() -> None:
    p = SimpleParser(
        foo=assert_compat[list[str | Missing] | int](
            assert_type(
                -repeated_option("--foo", nargs="?", const=MISSING, default=2),
                list[str | Missing] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=2)
    assert p("--foo") == Handler.from_spec(None, foo=[MISSING])
    assert p("--foo a") == Handler.from_spec(None, foo=["a"])
    assert p("--foo --foo --foo a --foo b") == Handler.from_spec(None, foo=[MISSING, MISSING, "a", "b"])


# 9.
# {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'None = None'}
def test_repeated_9() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int] | None](
            assert_type(
                -repeated_option("--foo", type=int),
                list[int] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1 --foo 2 --foo 3") == Handler.from_spec(None, foo=[1, 2, 3])


# 10.
# {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'str'}
def test_repeated_10() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int] | int](
            assert_type(
                -repeated_option("--foo", type=int, default="22"),
                list[int] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo 1 --foo 2 --foo 3") == Handler.from_spec(None, foo=[1, 2, 3])


# 11.
# {'type': 'TypeConverter[T]', 'nargs': 'None = None', 'default': 'D'}
def test_repeated_11() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int] | float](
            assert_type(
                -repeated_option("--foo", type=int, default=3.14),
                list[int] | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=3.14)
    assert p("--foo 1 --foo 2 --foo 3") == Handler.from_spec(None, foo=[1, 2, 3])


# 12.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'None = None'}
def test_repeated_12() -> None:
    p = SimpleParser(
        foo=assert_compat[list[list[int]] | None](
            assert_type(
                -repeated_option("--foo", type=int, nargs="+"),
                list[list[int]] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1 2 --foo 3") == Handler.from_spec(None, foo=[[1, 2], [3]])

    p = SimpleParser(
        foo=assert_compat[list[list[int]] | None](
            assert_type(
                -repeated_option("--foo", type=int, nargs="*"),
                list[list[int]] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo --foo 1 2") == Handler.from_spec(None, foo=[[], [1, 2]])
    assert p("--foo 1 2 --foo 3") == Handler.from_spec(None, foo=[[1, 2], [3]])

    p = SimpleParser(
        foo=assert_compat[list[list[int]] | None](
            assert_type(
                -repeated_option("--foo", type=int, nargs=4, flatten=False),
                list[list[int]] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1 2 3 4 --foo 5 6 7 8") == Handler.from_spec(None, foo=[[1, 2, 3, 4], [5, 6, 7, 8]])


# 13.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'str'}
def test_repeated_13() -> None:
    p = SimpleParser(
        foo=assert_compat[list[list[int]] | int](
            assert_type(
                -repeated_option("--foo", type=int, nargs="+", default="22"),
                list[list[int]] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo 1 2 --foo 3") == Handler.from_spec(None, foo=[[1, 2], [3]])

    p = SimpleParser(
        foo=assert_compat[list[list[int]] | int](
            assert_type(
                -repeated_option("--foo", type=int, nargs="*", default="22"),
                list[list[int]] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo --foo 1 2") == Handler.from_spec(None, foo=[[], [1, 2]])
    assert p("--foo 1 2 --foo 3") == Handler.from_spec(None, foo=[[1, 2], [3]])

    p = SimpleParser(
        foo=assert_compat[list[list[int]] | int](
            assert_type(
                -repeated_option("--foo", type=int, nargs=4, flatten=False, default="22"),
                list[list[int]] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo 1 2 3 4 --foo 5 6 7 8") == Handler.from_spec(None, foo=[[1, 2, 3, 4], [5, 6, 7, 8]])


# 14.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[False] = False', 'default': 'D'}
def test_repeated_14() -> None:
    p = SimpleParser(
        foo=assert_compat[list[list[int]] | float](
            assert_type(
                -repeated_option("--foo", type=int, nargs="+", default=3.14),
                list[list[int]] | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=3.14)
    assert p("--foo 1 2 --foo 3") == Handler.from_spec(None, foo=[[1, 2], [3]])

    p = SimpleParser(
        foo=assert_compat[list[list[int]] | float](
            assert_type(
                -repeated_option("--foo", type=int, nargs="*", default=3.14),
                list[list[int]] | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=3.14)
    assert p("--foo --foo 1 2") == Handler.from_spec(None, foo=[[], [1, 2]])
    assert p("--foo 1 2 --foo 3") == Handler.from_spec(None, foo=[[1, 2], [3]])

    p = SimpleParser(
        foo=assert_compat[list[list[int]] | float](
            assert_type(
                -repeated_option("--foo", type=int, nargs=4, flatten=False, default=3.14),
                list[list[int]] | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=3.14)
    assert p("--foo 1 2 3 4 --foo 5 6 7 8") == Handler.from_spec(None, foo=[[1, 2, 3, 4], [5, 6, 7, 8]])


# 15.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'None = None'}
def test_repeated_15() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int] | None](
            assert_type(
                -repeated_option("--foo", type=int, flatten=True, nargs="+"),
                list[int] | None,
            )
        )
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 1 2 3 4 --foo 5 6 7 8") == Handler.from_spec(None, foo=[1, 2, 3, 4, 5, 6, 7, 8])

    p = SimpleParser(
        foo=assert_compat[list[int] | None](
            assert_type(
                -repeated_option("--foo", type=int, flatten=True, nargs="*", default=None),
                list[int] | None,
            )
        )
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo --foo 1 2 3 4 --foo --foo 5 6 7 8") == Handler.from_spec(None, foo=[1, 2, 3, 4, 5, 6, 7, 8])


# 16.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'str'}
def test_repeated_16() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int] | int](
            assert_type(
                -repeated_option("--foo", type=int, flatten=True, nargs="+", default="22"),
                list[int] | int,
            )
        )
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo 1 2 3 4 --foo 5 6 7 8") == Handler.from_spec(None, foo=[1, 2, 3, 4, 5, 6, 7, 8])

    p = SimpleParser(
        foo=assert_compat[list[int] | int](
            assert_type(
                -repeated_option("--foo", type=int, flatten=True, nargs="*", default="22"),
                list[int] | int,
            )
        )
    )
    assert p("") == Handler.from_spec(None, foo=22)
    assert p("--foo --foo 1 2 3 4 --foo --foo 5 6 7 8") == Handler.from_spec(None, foo=[1, 2, 3, 4, 5, 6, 7, 8])


# 17.
# {'type': 'TypeConverter[T]', 'nargs': 'int | Literal["*", "+"]', 'flatten': 'Literal[True]', 'default': 'D'}
def test_repeated_17() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int] | float](
            assert_type(
                -repeated_option("--foo", type=int, flatten=True, nargs="+", default=4.33),
                list[int] | float,
            )
        )
    )
    assert p("") == Handler.from_spec(None, foo=4.33)
    assert p("--foo 1 2 3 4 --foo 5 6 7 8") == Handler.from_spec(None, foo=[1, 2, 3, 4, 5, 6, 7, 8])

    p = SimpleParser(
        foo=assert_compat[list[int] | float](
            assert_type(
                -repeated_option("--foo", type=int, flatten=True, nargs="*", default=4.33),
                list[int] | float,
            )
        )
    )
    assert p("") == Handler.from_spec(None, foo=4.33)
    assert p("--foo --foo 1 2 3 4 --foo --foo 5 6 7 8") == Handler.from_spec(None, foo=[1, 2, 3, 4, 5, 6, 7, 8])


# 18.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'None = None'}
def test_repeated_18() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int | Missing] | None](
            assert_type(
                -repeated_option("--foo", nargs="?", type=int, const=MISSING),
                list[int | Missing] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=None)
    assert p("--foo 2 --foo 2 --foo --foo") == Handler.from_spec(None, foo=[2, 2, MISSING, MISSING])


# 19.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'str'}
def test_repeated_19() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int | Missing] | int](
            assert_type(
                -repeated_option("--foo", nargs="?", type=int, default="4", const=MISSING),
                list[int | Missing] | int,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=4)
    assert p("--foo 2 --foo 2 --foo --foo") == Handler.from_spec(None, foo=[2, 2, MISSING, MISSING])


# 20.
# {'type': 'TypeConverter[T]', 'nargs': 'Literal["?"]', 'const': 'C', 'default': 'D'}
def test_repeated_20() -> None:
    p = SimpleParser(
        foo=assert_compat[list[int | Missing] | type[int]](
            assert_type(
                -repeated_option("--foo", nargs="?", type=int, default=int, const=MISSING),
                list[int | Missing] | type[int],
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foo=int)
    assert p("--foo 2 --foo 2 --foo --foo") == Handler.from_spec(None, foo=[2, 2, MISSING, MISSING])


###


def test_choices() -> None:
    p = SimpleParser(
        foo=assert_compat[str | None](
            assert_type(
                -option("--foo", choices=("a",)),
                str | None,
            )
        ),
    )
    p("--foo a")

    p = SimpleParser(
        foo=assert_compat[str | None](
            assert_type(
                -option("--foo", choices=("a", "b")),
                str | None,
            )
        ),
    )
    p("--foo a")

    p = SimpleParser(
        foo=assert_compat[list[str] | None](
            assert_type(
                -option("--foo", nargs=1, choices=("a", "b")),
                list[str] | None,
            )
        ),
    )
    p("--foo a")

    p = SimpleParser(
        foo=assert_compat[int | None](
            assert_type(
                -option("--foo", type=int, choices=tuple(range(1, 100, 2))),
                int | None,
            )
        ),
    )
    p("--foo 55")

    # Choices is not fired for defaults
    p = SimpleParser(
        foo=assert_compat[int | list[str]](
            assert_type(
                -option("--foo", type=int, choices=tuple(range(1, 100, 2)), default=["nope"]),
                int | list[str],
            )
        ),
    )
    p("--foo 55")
    assert p("") == Handler.from_spec(None, foo=["nope"])

    p = SimpleParser(
        foo=assert_compat[int](
            assert_type(
                -option("--foo", type=int, choices=tuple(range(1, 100, 2)), default="-100"),
                int,
            )
        ),
    )
    p("--foo 55")
    assert p("") == Handler.from_spec(None, foo=-100)

    p = SimpleParser(
        foo=assert_compat[IPv4Address | None,](
            assert_type(
                -option(
                    "--foo",
                    type=IPv4Address,
                    choices=(IPv4Address("1.1.1.1"), IPv4Address("2.2.2.2")),
                ),
                IPv4Address | None,
            )
        ),
    )
    p("--foo 1.1.1.1")

    p = SimpleParser(
        foo=assert_compat[list[int] | int](
            assert_type(
                -option("--foo", type=int, nargs=1, choices=(1, 2), default=1),
                list[int] | int,
            )
        ),
    )
    assert p("--foo 1") == Handler.from_spec(None, foo=[1])
    assert p("") == Handler.from_spec(None, foo=1)

    p = SimpleParser(
        foo=assert_compat[list[int] | int](
            assert_type(
                -option("--foo", type=int, nargs=1, choices=(1, 2), default="1"),
                list[int] | int,
            )
        ),
    )
    assert p("--foo 1") == Handler.from_spec(None, foo=[1])
    assert p("") == Handler.from_spec(None, foo=1)
    with pytest.raises(ParseError, match="invalid choice"):
        p("--foo 3")

    p = SimpleParser(
        foo=assert_compat[list[int]](
            assert_type(
                -option("--foo", type=int, nargs=1, choices=(1, 2), default=[3, 3]),
                list[int],
            )
        ),
    )
    assert p("--foo 1") == Handler.from_spec(None, foo=[1])
    assert p("") == Handler.from_spec(None, foo=[3, 3])

    p = SimpleParser(
        foo=assert_compat[list[int] | None](
            assert_type(
                -repeated_option("--foo", type=int, choices=(1, 2)),
                list[int] | None,
            )
        ),
    )
    p("--foo 01 --foo 2")

    # argparse doc recommends against enums, but StrEnum is really ok
    class MyEnum(StrEnum):
        A = "a"
        B = "b"

    p = SimpleParser(
        foo=assert_compat[MyEnum | None](
            assert_type(
                -option("--foo", type=MyEnum, choices=tuple(MyEnum)),
                MyEnum | None,
            )
        ),
    )
    assert p("--foo a") == Handler.from_spec(None, foo=MyEnum.A)

    option("--foo", "-f", type=MyEnum, choices=tuple(MyEnum))


def test_with_another() -> None:
    assert_compat[str | None](
        assert_type(
            -(option("--foo") | option("--bar")),
            str | None,
        )
    )

    assert_compat[str | None](
        assert_type(
            -(option("--foo") | option("--bar")),
            str | None,
        )
    )

    assert_compat[str | None](
        assert_type(
            t(option("--foo") | option("--bar")),
            str | None,
        )
    )

    p = SimpleParser(
        foobar=assert_compat[str | None,](
            assert_type(
                -(
                    #
                    option("--foo")
                    | option("--bar")
                    | option("--baz")
                ),
                str | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foobar=None)
    assert p("--foo a") == Handler.from_spec(None, foobar="a")
    assert p("--bar b") == Handler.from_spec(None, foobar="b")
    assert p("--baz c") == Handler.from_spec(None, foobar="c")
    assert p("--foo a --baz c --bar b --foo c") == Handler.from_spec(None, foobar="c")

    p = SimpleParser(
        foobar=assert_compat[str | int | float,](
            assert_type(
                -(
                    #
                    option("--foo", type=int, default=3.2)
                    | option("--bar")
                ),
                str | int | float,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foobar=3.2)
    assert p("--foo 1") == Handler.from_spec(None, foobar=1)
    assert p("--bar b") == Handler.from_spec(None, foobar="b")

    p = SimpleParser(
        foobar=assert_compat[str | int | None](
            assert_type(
                -(
                    # mix
                    option("--foo", type=int)
                    | option("--bar", default=3.2)
                ),
                str | int | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foobar=None)
    assert p("--foo 1") == Handler.from_spec(None, foobar=1)
    assert p("--bar b") == Handler.from_spec(None, foobar="b")

    p = SimpleParser(
        foobar=assert_compat[int | list[str] | None](
            assert_type(
                -(
                    #
                    option("--foo", nargs=1)
                    | option("--bar", type=int)
                ),
                int | list[str] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foobar=None)
    assert p("--foo a") == Handler.from_spec(None, foobar=["a"])
    assert p("--bar 1") == Handler.from_spec(None, foobar=1)

    p = SimpleParser(
        foobar=assert_compat[list[int] | list[str] | int | str | Missing](
            assert_type(
                -(
                    #
                    option("--foo", nargs=1, default=4)
                    | option("--bar", type=int, nargs="+")
                    | option("--far", nargs="?", const=MISSING)
                ),
                list[int] | list[str] | int | str | Missing,
            )
        )
    )

    assert p("") == Handler.from_spec(None, foobar=4)
    assert p("--foo a") == Handler.from_spec(None, foobar=["a"])
    assert p("--bar 1 2 3 4") == Handler.from_spec(None, foobar=[1, 2, 3, 4])
    assert p("--bar 1 2 3 4 --far") == Handler.from_spec(None, foobar=MISSING)
    assert p("--bar 1 2 3 4 --far near") == Handler.from_spec(None, foobar="near")


def test_with_another_repeated() -> None:
    assert_type(
        -(
            #
            repeated_option("--foo")
            + repeated_option("--bar", type=int)
        ),
        list[str | int] | None,
    )

    assert_type(
        -(
            #
            repeated_option("--foo")
            + repeated_option("--bar", type=int)
        ),
        list[str | int] | None,
    )

    p = SimpleParser(
        foobar=assert_compat[list[str | int] | None](
            assert_type(
                (
                    #
                    repeated_option("--foo")
                    + repeated_option("--bar", type=int)
                ).t,
                list[str | int] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foobar=None)
    assert p("--foo a") == Handler.from_spec(None, foobar=["a"])
    assert p("--bar 1") == Handler.from_spec(None, foobar=[1])
    assert p("--foo a --foo b --bar 2 --foo d --bar 3") == Handler.from_spec(None, foobar=["a", "b", 2, "d", 3])

    p = SimpleParser(
        foobarbaz=assert_compat[list[list[str] | int] | None](
            assert_type(
                -(
                    #
                    repeated_option("--foo", nargs=2)
                    + repeated_option("--bar", type=int)
                    + repeated_option("--baz", nargs="+")
                ),
                list[list[str] | int] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foobarbaz=None)
    assert p("--foo a b --foo c d") == Handler.from_spec(None, foobarbaz=[["a", "b"], ["c", "d"]])
    assert p("--bar 1") == Handler.from_spec(None, foobarbaz=[1])
    assert p("--baz x y") == Handler.from_spec(None, foobarbaz=[["x", "y"]])
    assert p("--foo a b --foo c d --bar 1 --baz x y --bar 1") == Handler.from_spec(
        None, foobarbaz=[["a", "b"], ["c", "d"], 1, ["x", "y"], 1]
    )

    p = SimpleParser(
        foobarbaz=assert_compat[list[str | int | list[str] | Missing] | None](
            assert_type(
                -(
                    #
                    repeated_option("--foo", nargs=2, flatten=True)
                    + repeated_option("--bar", type=int)
                    + repeated_option("--baz", nargs="+")
                    + repeated_option("--faz", nargs="?", const=MISSING)
                ),
                list[str | int | list[str] | Missing] | None,
            )
        ),
    )
    assert p("") == Handler.from_spec(None, foobarbaz=None)
    assert p("--foo a b --foo c d") == Handler.from_spec(None, foobarbaz=["a", "b", "c", "d"])
    assert p("--bar 1") == Handler.from_spec(None, foobarbaz=[1])
    assert p("--baz x y") == Handler.from_spec(None, foobarbaz=[["x", "y"]])
    assert p("--foo a b --foo c d --bar 1 --baz x y --bar 1") == Handler.from_spec(
        None, foobarbaz=["a", "b", "c", "d", 1, ["x", "y"], 1]
    )
    assert p("--faz x") == Handler.from_spec(None, foobarbaz=["x"])
    assert p("--faz --faz") == Handler.from_spec(None, foobarbaz=[MISSING, MISSING])


def test_required() -> None:
    p = SimpleParser(
        foo=assert_compat[str](
            assert_type(
                -required(option("--foo")),
                str,
            )
        ),
    )

    with pytest.raises(ParseError, match="arguments are required"):
        p("")
    assert p("--foo a") == Handler.from_spec(None, foo="a")

    p = SimpleParser(
        foo=assert_compat[list[str]](
            assert_type(
                -required(repeated_option("--foo")),
                list[str],
            )
        ),
    )

    with pytest.raises(ParseError, match="arguments are required"):
        p("")

    assert p("--foo a") == Handler.from_spec(None, foo=["a"])


def test_t() -> None:
    assert_type(t(option("--foo")), str | None)
    assert_type(t[option("--foo")], str | None)
    assert_type(t @ option("--foo"), str | None)
    assert_type(option("--foo") @ t, str | None)

    assert_type(t(option("--foo") | option("--bar", type=int)), str | int | None)
    assert_type(t[option("--foo") | option("--bar", type=int)], str | int | None)
    assert_type(t @ (option("--foo") | option("--bar", type=int)), str | int | None)
    assert_type((option("--foo") | option("--bar", type=int)) @ t, str | int | None)

    assert_type(t(repeated_option("--foo") + repeated_option("--bar", type=int)), list[str | int] | None)
    assert_type(t[repeated_option("--foo") + repeated_option("--bar", type=int)], list[str | int] | None)
    assert_type(t @ (repeated_option("--foo") + repeated_option("--bar", type=int)), list[str | int] | None)
    assert_type((repeated_option("--foo") + repeated_option("--bar", type=int)) @ t, list[str | int] | None)


def test_cmp() -> None:
    a = option("--foo")
    a_too = option("--foo")
    b = option("--bar")
    b_too = option("--bar")

    assert a == a_too

    mix0 = a | b
    mix1 = a_too | b_too

    assert mix0 == mix1
    assert mix0 != 2


def test_hash() -> None:
    a = option("--a")

    s = {a}

    assert a in s
