import textwrap
from typing import Any, Callable

import pytest

from paramspecli import Config, argument, count, deprecated, fake, flag, option, switch

from .fix import Command as Command
from .fix import Group as Group
from .fix import ensure_exit


def has_line(*, hay: str, needle: str) -> bool:
    return needle in [" ".join(line.split()) for line in hay.splitlines()]


@pytest.mark.parametrize(
    ("option", "match"),
    [
        (option("--foo"), "--foo FOO"),
        (option("--foo", type=int), "--foo FOO"),
        (option("--foo", help="foo"), "--foo FOO foo"),
        (option("--foo", type=int, help="foo"), "--foo FOO foo"),
        (option("--foo", type=int, help="foo", default=1), "--foo FOO foo (default: 1)"),
        (option("--foo", type=int, help="foo", default=1, show_default=False), "--foo FOO foo"),
        (option("--foo", type=int, help="foo", default=1, show_default=True), "--foo FOO foo (default: 1)"),
        (
            option("--foo", type=int, help="foo", default=1, show_default="<SECRET>"),
            "--foo FOO foo (default: <SECRET>)",
        ),
        (
            option("--foo", type=int, help="foo (default: %(default)s)", default=1),
            "--foo FOO foo (default: 1) (default: 1)",
        ),
    ],
)
def test_default_options(
    capsys: pytest.CaptureFixture[str],
    *,
    option: fake.Option[Any, Any],
    match: str,
) -> None:
    def func(*, foo: Any) -> None: ...

    cli = Command(func)
    cli.bind(foo=-option)

    with ensure_exit:
        cli.parse("--help")

    cap = capsys.readouterr()
    assert has_line(hay=cap.out, needle=match)


@pytest.mark.parametrize(
    ("option", "match"),
    [
        (option("--foo"), "--foo FOO"),
        (option("--foo", type=int), "--foo FOO"),
        (option("--foo", help="foo"), "--foo FOO foo"),
        (option("--foo", type=int, help="foo"), "--foo FOO foo"),
        (option("--foo", type=int, help="foo", default=1), "--foo FOO foo"),
        (option("--foo", type=int, help="foo", default=1, show_default=False), "--foo FOO foo"),
        (option("--foo", type=int, help="foo", default=1, show_default=True), "--foo FOO foo (default: 1)"),
        (
            option("--foo", type=int, help="foo", default=1, show_default="<SECRET>"),
            "--foo FOO foo (default: <SECRET>)",
        ),
        (
            option("--foo", type=int, help="foo (default: %(default)s)", default=1),
            "--foo FOO foo (default: 1)",
        ),
    ],
)
def test_default_options_with_global_off(
    capsys: pytest.CaptureFixture[str],
    *,
    option: fake.Option[Any, Any],
    match: str,
) -> None:
    def func(*, foo: Any) -> None: ...

    cli = Command(func)
    cli.bind(foo=-option)

    with ensure_exit:
        cli.parse("--help", config=Config(show_default=False))

    cap = capsys.readouterr()
    assert has_line(hay=cap.out, needle=match)


@pytest.mark.parametrize(
    ("option", "match"),
    [
        (flag("--foo"), "--foo"),
        (flag("--foo", help="foo"), "--foo foo"),
        (flag("--foo", help="foo", show_default=True), "--foo foo (default: False)"),
        (flag("--foo", help="foo", show_default="who knowns"), "--foo foo (default: who knowns)"),
        (flag("--foo", help="foo", default=4), "--foo foo (default: 4)"),
        (flag("--foo", help="foo", default=4, show_default=False), "--foo foo"),
        #
        (switch("--foo"), "--foo, --no-foo"),
        (switch("--foo", help="foo", show_default=False), "--foo, --no-foo foo"),
        (switch("--foo", help="foo"), "--foo, --no-foo foo (default: False)"),
        (switch("--foo", help="foo", default="?"), "--foo, --no-foo foo (default: ?)"),
        (switch("--foo", help="foo", default=True), "--foo, --no-foo foo (default: True)"),
        (switch("--foo", help="foo", show_default="!!!"), "--foo, --no-foo foo (default: !!!)"),
    ],
)
def test_default_flags(
    capsys: pytest.CaptureFixture[str],
    *,
    option: fake.Option[Any, Any],
    match: str,
) -> None:
    def func(*, foo: Any) -> None: ...

    cli = Command(func)
    cli.bind(foo=-option)

    with ensure_exit:
        cli.parse("--help")

    cap = capsys.readouterr()
    assert has_line(hay=cap.out, needle=match)


@pytest.mark.parametrize(
    ("option", "match"),
    [
        (flag("--foo"), "--foo"),
        (flag("--foo", help="foo"), "--foo foo"),
        (flag("--foo", help="foo", show_default=True), "--foo foo (default: False)"),
        (flag("--foo", help="foo", show_default="who knows"), "--foo foo (default: who knows)"),
        (flag("--foo", help="foo", default=4), "--foo foo"),
        (flag("--foo", help="foo", default=4, show_default=False), "--foo foo"),
        #
        (switch("--foo"), "--foo, --no-foo"),
        (switch("--foo", help="foo", show_default=False), "--foo, --no-foo foo"),
        (switch("--foo", help="foo"), "--foo, --no-foo foo"),
        (switch("--foo", help="foo", default="?"), "--foo, --no-foo foo"),
        (switch("--foo", help="foo", default=True), "--foo, --no-foo foo"),
        (switch("--foo", help="foo", show_default="!!!"), "--foo, --no-foo foo (default: !!!)"),
    ],
)
def test_default_flags_with_global_off(
    capsys: pytest.CaptureFixture[str],
    *,
    option: fake.Option[Any, Any],
    match: str,
) -> None:
    def func(*, foo: Any) -> None: ...

    cli = Command(func)
    cli.bind(foo=-option)

    with ensure_exit:
        cli.parse("--help", config=Config(show_default=False))

    cap = capsys.readouterr()
    assert has_line(hay=cap.out, needle=match)


def test_not_same_epilog(capsys: pytest.CaptureFixture[str]) -> None:
    cli = Group(epilog="Bye!")

    def func() -> None: ...

    with cli.add_group("a") as ga:
        with ga.add_group("b", epilog="Donate!") as gb:
            gb.add_command("f", func).bind()

    # same epilog off
    with ensure_exit:
        cli.parse("--help")
    cap = capsys.readouterr()
    assert "Bye!" in cap.out

    with ensure_exit:
        cli.parse("a --help ")
    cap = capsys.readouterr()
    assert "Bye!" not in cap.out

    with ensure_exit:
        cli.parse("a b --help ")
    cap = capsys.readouterr()
    assert "Donate!" in cap.out

    with ensure_exit:
        cli.parse("a b f --help ")

    cap = capsys.readouterr()
    assert "Bye!" not in cap.out
    assert "Donate!" not in cap.out

    # same epilog on
    cfg = Config(propagate_epilog=True)

    with ensure_exit:
        cli.parse("--help", config=cfg)
    cap = capsys.readouterr()
    assert "Bye!" in cap.out

    with ensure_exit:
        cli.parse("a --help ", config=cfg)
    cap = capsys.readouterr()
    assert "Bye!" in cap.out

    with ensure_exit:
        cli.parse("a b --help ", config=cfg)
    cap = capsys.readouterr()
    assert "Donate!" in cap.out
    assert "Bye!" not in cap.out

    with ensure_exit:
        cli.parse("a b f --help ", config=cfg)
    cap = capsys.readouterr()
    assert "Bye!" in cap.out
    assert "Donate!" not in cap.out


@pytest.mark.parametrize("ctor", [flag, option, switch, count])
def test_help_suppress(capsys: pytest.CaptureFixture[str], ctor: Callable[..., fake.Option[Any, Any]]) -> None:
    def func(*, foo: Any) -> None: ...

    cli = Command(func)
    cli.bind(foo=-ctor("--foo", help=False, show_default="<DEF>"))

    with ensure_exit:
        cli.parse("--help")

    cap = capsys.readouterr()
    assert "<DEF>" not in cap.out


def test_help_suppress_arg(capsys: pytest.CaptureFixture[str]) -> None:
    def func(the: str) -> None: ...

    cli = Command(func)
    cli.bind(-argument("<THE>", help=False))

    with ensure_exit:
        cli.parse("--help")

    cap = capsys.readouterr()
    assert "<THE>" not in cap.out


def test_deprecated() -> None:
    def func(*, foo: bool) -> None:
        pass

    cli = Group()
    with cli.add_command("cmd", func) as cmd:
        cmd.bind(foo=-deprecated(flag("--foo")))

    # nothing to check on a python < 3.13
    cli.parse("cmd --foo")()


def test_help_no_format(capsys: pytest.CaptureFixture[str]) -> None:
    FRONTMATTER = """\
This is an
info with
a
manual formatting
which should be pre-
    served
"""

    CMD_HELP = """\

This is a command help
with a manual for-
    -matting to be preserved
                    too"""

    def f() -> None: ...

    cli = Group(info=FRONTMATTER)

    # extra newline to push help into the next line
    cli.add_command("cmd", f, help=CMD_HELP).bind()

    with ensure_exit:
        cli.parse("")()

    cap = capsys.readouterr()

    assert FRONTMATTER in cap.out

    cmd_block = textwrap.dedent("\n".join(cap.out.splitlines()[-4:]))
    assert cmd_block == CMD_HELP.strip()
