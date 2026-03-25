import gc
from pathlib import Path
from typing import Any, assert_type

import pytest

from paramspecli import (
    Action,
    Config,
    Const,
    Context,
    PathConv,
    Route,
    argument,
    fake,
    flag,
    option,
    repeated_flag,
    repeated_option,
    util,
    version_action,
)
from paramspecli.md import Md

from .fix import Command, Group, ParseError, ensure_called, ensure_exit, track_call

# Random bits to boost test coverage


def test_simple() -> None:
    @track_call
    def func(a: str, *, foo: int | None) -> None:
        assert isinstance(a, str)
        assert isinstance(foo, (int | None))

    with Group(info="prog") as cli:
        cli.append_action(version_action("0.1"))
        with cli.add_command("f1", func, help="f1") as cmd1:
            cmd1.bind(
                -argument("A"),
                foo=-option("--foo", type=int),
            )
        assert cli.nodes["f1"] == cmd1

    with ensure_called(func):
        cli.parse("f1 a --foo=12")()
    with ensure_exit:
        cli.parse("--version")


def test_just_command() -> None:
    @track_call
    def func(a: str, *, foo: int | None) -> None:
        assert isinstance(a, str)
        assert isinstance(foo, (int | None))

    with Command(func) as cli:
        cli.bind(
            -argument("A"),
            foo=-option("--foo", type=int, help=False),
        )

    with ensure_called(func):
        cli.parse("a --foo=12")()
    with ensure_exit:
        cli.parse("--help")


def test_bad_params_registration() -> None:
    def func(a: str, *, foo: int | None) -> None: ...

    cli1 = Command(func)

    with pytest.raises(ValueError, match="should start"):
        cli1.bind(
            -option("A", default="B"),
            foo=-option("--foo", type=int),
        )

    with pytest.raises(TypeError, match="should be Option"):
        cli1.bind(
            -argument("A"),
            foo=-argument("--foo", type=int),
        )

    with pytest.raises(TypeError, match="should be an Argument"):
        cli1.bind(
            -option("--A", default="B"),
            foo=-argument("foo", type=int),
        )


def test_alt_lie() -> None:
    assert_type(
        option("--foo").t,
        str | None,
    )
    assert_type(
        repeated_option("--foo").t,
        list[str],
    )
    assert_type(
        (option("--foo") | option("--boo")).t,
        str | None,
    )

    assert_type(
        (repeated_option("--foo") + repeated_option("--boo", type=int)).t,
        list[str | int],
    )


def test_catchall() -> None:
    def func(a: float, *, foo: int | None, path: Path | None) -> None: ...

    cfg = Config(catch_typeconv_exceptions=True)

    with Group() as cli:
        with cli.add_command("f1", func, help="f1") as cmd1:
            cmd1.bind(
                -argument("A", type=float),
                foo=-option("--foo", type=int),
                path=-option("--path", type=PathConv(exists=False)),
            )

    with pytest.raises(ParseError):
        cli.parse("f1 1.2 --foo a", config=cfg)

    with pytest.raises(ParseError):
        cli.parse("f1 3.4 --path README.md", config=cfg)

    with pytest.raises(ParseError):
        cli.parse("f1 a", config=cfg)


def test_exit() -> None:
    with pytest.raises(SystemExit):
        util.exit(2, "ERROR")


def test_micro() -> None:
    def f1(a: str) -> None: ...
    def f2(*, foo: str | None) -> None: ...

    arg = fake.Argument[Any, Any](metavar="A", extra={"a": "b"}, help=True)
    cli1 = Command(f1)
    cli1.bind(-arg)

    with pytest.raises(TypeError, match="got an unexpected"):
        cli1.parse("a")

    opt = fake.Option[Any, Any](
        names=("--foo",), hard_show_default=True, soft_show_default=True, help=True, extra={"a": "b"}
    )
    cli2 = Command(f2)
    cli2.bind(foo=-opt)

    with pytest.raises(TypeError, match="got an unexpected"):
        cli2.parse("--foo b")

    cli3 = Group(info=Md("** My Program ***"))
    cli3.add_group("A")

    with ensure_exit:
        cli3.parse("")()

    with ensure_exit:
        cli3.parse("A")()

    with ensure_exit:
        cli3.parse("A --help")

    with ensure_exit:
        cli3.parse(
            "A --help",
            config=Config(
                root_parser_extra_kwargs={"exit_on_error": True},
                sub_parser_extra_kwargs={"exit_on_error": False},
            ),
        )

    with pytest.raises(ValueError, match="least one name"):
        fake.Option(())

    #


def test_res_meths() -> None:
    cli = Group()

    res = cli.parse("")

    assert len(res) == 2
    next(h for h in res)

    assert res == res
    assert res != 2

    assert res[0] == res[0]
    assert res[0] != 2


def test_repr() -> None:
    def func(a: str, **kwargs: Any) -> None:
        pass

    with Group() as cli:
        with cli.add_command("f1", func, help="f1") as cmd1:
            h = cmd1.add_section("helpy")
            one = cmd1.add_oneof()

            cmd1.bind(
                -argument("A"),
                foo=-one(option("--foo", type=int)[h]),
                mix=-(flag("--mix") | flag("--fix")),
                mixlist=-(repeated_flag("--r") + repeated_flag("--f")),
                c=Const(42),
            )

    util.echo(str(PathConv()))
    util.echo(str(cli))
    util.echo(str(cmd1))

    res = cli.parse("")

    util.echo(str(res))


@pytest.mark.parametrize(
    "obj",
    [
        argument("foo"),
        option("--foo"),
        repeated_option("--foo"),
        option("--foo") | option("--bar"),
        repeated_option("--foo") + repeated_option("--bar"),
        Action(("--bla",)),
        Context(),
    ],
)
def test_ensure_slots(obj: Any) -> None:
    obj.__slots__  # noqa: B018
    with pytest.raises(AttributeError):
        obj.__dict__  # noqa: B018


def test_action_instead_of_option() -> None:
    def func(**kwargs: Any) -> None:
        pass

    with Command(func) as cli:
        cli.bind(foo=version_action("1"))

    with pytest.raises(TypeError, match="used in place of Option"):
        cli.parse("")


def test_ensure_bind() -> None:
    def f() -> None: ...

    cli = Command(f)

    with pytest.raises(ValueError, match=r"bind\(\)"):
        cli.parse("")


def test_gc() -> None:
    group_was_collected: bool = False
    command_was_collected: bool = False
    was_called: bool = False

    def parse() -> Route:
        class GroupWithDel(Group):
            def __del__(self) -> None:
                nonlocal group_was_collected
                group_was_collected = True

        class CommandWithDel(Command[...]):
            def __del__(self) -> None:
                nonlocal command_was_collected
                command_was_collected = True

        def f() -> None:
            nonlocal was_called
            was_called = True

        cli = GroupWithDel()
        cmd = CommandWithDel(f)
        cmd.bind()
        cli["command"] = cmd

        return cli.parse("command")

    res = parse()

    gc.collect()
    gc.collect()
    gc.collect()
    gc.collect()

    res()

    assert group_was_collected
    assert command_was_collected
    assert was_called
