import dataclasses
from typing import assert_type

import pytest

from paramspecli import Context, Handler

from .fix import ANY_FUNC, CallableGroup, assert_compat, ensure_exit


def test_simple() -> None:
    @dataclasses.dataclass
    class Ctx:
        cnt: int

    def c(*, ctx: Ctx) -> None:
        assert ctx.cnt == 0
        ctx.cnt = 1

    def g(*, ctx: Ctx) -> None:
        assert ctx.cnt == 1
        ctx.cnt = 2

    def f(*, ctx: Ctx) -> None:
        assert ctx.cnt == 2
        ctx.cnt = 3

    cli = CallableGroup(func=c)

    assert_compat[Ctx](-Context[Ctx]())

    cli.bind(ctx=assert_type(-Context[Ctx](), Ctx))

    with cli.add_callable_group("g", func=g) as group:
        group.bind(ctx=-Context[Ctx]())

        with group.add_command("f", f) as cmd:
            cmd.bind(ctx=-Context[Ctx]())

    ctx = Ctx(cnt=0)
    res = cli.parse("", context=ctx)
    assert res.nonempty == [
        Handler.from_spec(c, ctx=ctx),
        Handler.from_spec(ANY_FUNC, ctx=ctx),
    ]
    with ensure_exit:
        res()
    assert ctx.cnt == 1

    ctx = Ctx(cnt=0)
    res = cli.parse("g", context=ctx)
    assert res.nonempty == [
        Handler.from_spec(c, ctx=ctx),
        Handler.from_spec(g, ctx=ctx),
        Handler.from_spec(ANY_FUNC, ctx=ctx),
    ]
    with ensure_exit:
        res()
    assert ctx.cnt == 2

    ctx = Ctx(cnt=0)
    res = cli.parse("g f", context=ctx)
    assert res.nonempty == [
        Handler.from_spec(c, ctx=ctx),
        Handler.from_spec(g, ctx=ctx),
        Handler.from_spec(f, ctx=ctx),
    ]
    res()
    assert ctx.cnt == 3


def test_ctx_arg() -> None:
    @dataclasses.dataclass
    class Ctx:
        cnt: int

    def c(ctx: Ctx) -> None:
        assert ctx.cnt == 0
        ctx.cnt = 1

    def f(ctx: Ctx) -> None:
        assert ctx.cnt == 1

    cli = CallableGroup(func=c)

    cli.bind(-Context[Ctx]())

    with cli.add_command("f", f) as cmd:
        cmd.bind(-Context[Ctx]())

    context = Ctx(cnt=0)

    res = cli.parse("f", context=context)
    res()


def test_ctx_arg_and_opt() -> None:
    @dataclasses.dataclass
    class Ctx:
        cnt: int

    def c(ctx: Ctx) -> None:
        assert ctx.cnt == 0
        ctx.cnt = 1

    def f(*, ctx: Ctx) -> None:
        assert ctx.cnt == 1

    cli = CallableGroup(func=c)

    cli.bind(-Context[Ctx]())

    with cli.add_command("f", f) as cmd:
        cmd.bind(ctx=-Context[Ctx]())

    context = Ctx(cnt=0)

    res = cli.parse("f", context=context)
    res()


def test_ensure_ctx_passed() -> None:
    @dataclasses.dataclass
    class Ctx:
        cnt: int

    def c(ctx: Ctx) -> None:
        pass

    cli = CallableGroup(func=c)
    cli.bind(-Context[Ctx]())

    with pytest.raises(ValueError, match="can't be None"):
        cli.parse("")
