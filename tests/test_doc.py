from pathlib import Path
from typing import Any

from paramspecli import Group, argument, option, repeated_option, switch
from paramspecli.doc import Doc, Settings
from paramspecli.md import Md


# Executing a lot of doc code paths and comparing it to the snapshots
def test_kitchen_sink() -> None:
    def f(ip: list[str], **kwargs: Any) -> None:
        pass

    def dummy() -> None:
        pass

    cli = Group(info=Md("**My Program**"))

    with cli.add_group(("net", "network"), info="Net stuff", headline="some commands ...") as net:
        with net.add_command("serve", f, info=Md("**My Command**")) as cmd:
            net_options = cmd.add_section("Net options", headline="Popular network options")
            _unused = cmd.add_section("Unused options")
            cmd.bind(
                -argument("IP", nargs="+", choices=("127.0.0.1", "0.0.0.0"), help="IP address"),
                ports=-repeated_option(
                    "--port",
                    "-p",
                    type=int,
                    help="Port to use",
                    nargs="+",
                    flatten=True,
                    choices={
                        80: "production",
                        8080: "internal",
                    },
                )[net_options],
                debug=-switch("--debug", "-g", help="Enable debug"),
                some_opt=-option("--some", help="Unsure ...", default=":-)", show_default=True)[net_options],
                some_opt2=-option("--some2", help="Unsure#2 ...", show_default="who knows")[net_options],
                some_opt3=-option("--some3", help="Unsure#3 ...", default=42),
            )

        net.add_callable_group("dummy", dummy, info="Does nothing")
        net.add_command("nop", dummy, info="It nops!")

    res_cli = Doc(settings=Settings(arguments_headline="Fugazi")).generate(cli, prog="myprog")
    kitchen1 = Path("tests/kitchen1.md").read_text()
    assert res_cli == kitchen1

    res_cmd = Doc(settings=Settings(arguments_headline="Fugazi")).generate(cmd, prog="myprog")
    kitchen2 = Path("tests/kitchen2.md").read_text()
    assert res_cmd == kitchen2
