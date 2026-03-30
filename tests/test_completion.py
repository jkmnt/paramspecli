# just make sure complete is not failing, that's all

from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Any

import pytest

from paramspecli import Config, Context, custom_action, option

from .fix import Group, ensure_called, track_call

try:
    import shtab
except ImportError:
    pytest.skip("not shtab, skipping completion tests", allow_module_level=True) # ty: ignore[invalid-argument-type, too-many-positional-arguments] # fmt: skip


def test_ext_completion() -> None:
    def f() -> None:
        pass

    cli = Group(prog="prog")
    with cli.add_command("cmd", f, help="f") as cmd:
        cmd.bind()

    parser = cli.build_parser(config=Config())
    shtab.complete(parser, shell="bash")
    shtab.complete(parser, shell="zsh")
    shtab.complete(parser, shell="tcsh")

    parser = cmd.build_parser(config=Config())
    shtab.complete(parser, shell="bash")
    shtab.complete(parser, shell="zsh")
    shtab.complete(parser, shell="tcsh")


def test_option_completion() -> None:
    def f(*, foo: str) -> None:
        pass

    @track_call
    def gen_completion(*, parser: ArgumentParser, value: str, **kwargs: Any) -> None:
        shtab.complete(parser, value)

    cli = Group(prog="prog")
    cli.append_action(custom_action("--completion", handler=gen_completion, choices=shtab.SUPPORTED_SHELLS))

    with cli.add_command("cmd", f, help="f") as cmd:
        cmd.bind(foo=-option("--foo", default="a").with_injected(completion=shtab.FILE))

    with ensure_called(gen_completion):
        cli.parse("--completion bash")

    with ensure_called(gen_completion):
        cli.parse("--completion zsh")

    with ensure_called(gen_completion):
        cli.parse("--completion tcsh")


# passing parser thru ctx
def test_command_completion() -> None:
    def f() -> None:
        pass

    @dataclass
    class Ctx:
        root: Group

    @track_call
    def gen_completion(*, ctx: Ctx, shell: str) -> None:
        shtab.complete(ctx.root.build_parser(config=Config(), context=ctx), shell)

    cli = Group(prog="prog")

    with cli.add_command("cmd", f, help="f") as cmd:
        cmd.bind()

    with cli.add_command("completion", gen_completion, help="f") as cmd2:
        cmd2.bind(
            ctx=-Context[Ctx](),
            shell=-option("--shell", choices=shtab.SUPPORTED_SHELLS, default="bash"),
        )

    ctx = Ctx(cli)
    with ensure_called(gen_completion):
        cli.parse("completion", context=ctx)()

    with ensure_called(gen_completion):
        cli.parse("completion --shell zsh", context=ctx)()

    with ensure_called(gen_completion):
        cli.parse("completion --shell tcsh", context=ctx)()
