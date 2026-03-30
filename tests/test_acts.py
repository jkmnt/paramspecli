from typing import Any

from paramspecli import MISSING, Missing, custom_action

from .fix import Command, Group


def test_action_ctx() -> None:
    def f() -> None:
        pass

    def on_str_set(*, context: Any, value: str, **kwargs: Any) -> None:
        assert value is not None
        context["config"] = value

    def on_int_set(*, context: Any, value: int, **kwargs: Any) -> None:
        assert value is not None
        context["numbers"] = value

    cli = Group()
    cli.append_action(custom_action("--config", handler=on_str_set, help="path to toml"))
    with cli.add_command("f", f) as cmd:
        cmd.bind()
        cmd.append_action(custom_action("--numbers", handler=on_int_set, type=int))

    ctx: dict[str, Any] = {}
    cli.parse("", context=ctx)
    assert "config" not in ctx

    ctx = {}
    cli.parse("--config pyproject.toml", context=ctx)
    assert ctx["config"] == "pyproject.toml"

    cli.parse("f --numbers 777", context=ctx)
    assert ctx["numbers"] == 777

    cli.parse("--config blabla f --numbers 888", context=ctx)
    assert ctx["numbers"] == 888


def test_action_ctx_nargs() -> None:
    def f() -> None:
        pass

    def on_set(*, context: Any, value: list[int], **kwargs: Any) -> None:
        context["foo"] = value

    cli = Command(f)
    cli.bind()
    cli.append_action(custom_action("--foo", nargs="*", type=int, handler=on_set))

    ctx: dict[str, Any] = {}
    cli.parse("", context=ctx)
    assert "foo" not in ctx

    ctx = {}
    cli.parse("--foo", context=ctx)
    assert ctx["foo"] == []

    ctx = {}
    cli.parse("--foo 1 2 3", context=ctx)
    assert ctx["foo"] == [1, 2, 3]


def test_action_ctx_opt_nargs() -> None:
    def f() -> None:
        pass

    def on_set(*, context: Any, value: int | Missing, **kwargs: Any) -> None:
        context["foo"] = value

    cli = Command(f)
    cli.bind()
    cli.append_action(custom_action("--foo", nargs="?", type=int, handler=on_set))

    ctx: dict[str, Any] = {}
    cli.parse("", context=ctx)
    assert "foo" not in ctx

    ctx = {}
    cli.parse("--foo", context=ctx)
    assert ctx["foo"] is MISSING

    ctx = {}
    cli.parse("--foo 1", context=ctx)
    assert ctx["foo"] == 1


# ensure argparse calls actions in order of commandline appearance, not registration
def test_action_order() -> None:
    def f() -> None:
        pass

    def on_set_foo(*, context: Any, value: None, **kwargs: Any) -> None:
        context.append("foo")

    def on_set_bar(*, context: Any, value: None, **kwargs: Any) -> None:
        context.append("bar")

    cli = Command(f)
    cli.bind()
    cli.append_action(custom_action("--foo", handler=on_set_foo, nargs=0))
    cli.append_action(custom_action("--bar", handler=on_set_bar, nargs=0))

    ctx: list[str] = []
    cli.parse("", context=ctx)
    assert ctx == []

    ctx = []
    cli.parse("--foo --bar", context=ctx)
    assert ctx == ["foo", "bar"]

    ctx = []
    cli.parse("--bar --foo", context=ctx)
    assert ctx == ["bar", "foo"]


def test_acts_doc() -> None:
    cli = Group()

    def handle_number(*, context: dict[str, int], value: int | Missing, **kwargs: Any) -> None:
        if value is ...:
            v = 42
        else:
            v = value
        context["number"] = v

    cli.append_action(custom_action("--number", handler=handle_number, type=int, nargs="?"))

    ctx: dict[str, int] = {}
    cli.parse("--number 1", context=ctx)
    assert ctx["number"] == 1

    ctx = {}
    cli.parse("--number", context=ctx)
    assert ctx["number"] == 42
