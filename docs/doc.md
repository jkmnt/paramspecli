# Generating documentation

Documentation is important. Out of the box, paramspecli includes a simple markdown documentation generator.
While the documentation format is fixed, some small tweaks are possible.

Documenting the basic example with some extra info:

```python
from paramspecli import Group, option, argument, flag
from paramspecli.doc import Doc


def server(name: str, *, port: int, debug: bool):
    print("Serving!")


def ping(addr: str, *, until_stopped: bool, count: int | None):
    print("PING!")


cli = Group(
    prog="myprog",
    info="**!!!** [My Awesome Program](http://127.0.0.1/awesome.php) **!!!**",
)

with cli.add_group("net", help="Network stuff") as group:
    with group.add_command("server", server, help="Start server") as cmd:
        cmd.bind(
            -argument("TEXT"),
            port=-option("--port", type=int, default=80, help="Port to use"),
            debug=-flag("--debug", "-g", help="Enable debug"),
        )

    with group.add_command("ping", ping, help="Do ping") as cmd:
        cmd.bind(
            -argument("IP", help="target address"),
            until_stopped=-flag("-t", help="Ping the specified host until stopped"),
            count=-option("-n", type=int, help="Number of echo requests to send"),
        )

doc = Doc().generate(cli, "myprog")
print(doc)
```

??? info "See the result"

    # myprog

    **!!!** [My Awesome Program](http://127.0.0.1/awesome.php) **!!!**

    Options:

    - `--help`, `-h`

        Show help and exit

    Commands:

    - [net ...](#myprog-net)

        Network stuff

    ## myprog net ...

    Network stuff

    Options:

    - `--help`, `-h`

        Show help and exit

    Commands:

    - [server](#myprog-net-server)

        Start server

    - [ping](#myprog-net-ping)

        Do ping

    ### myprog net server

    Start server

    Usage:

    ```
    myprog net server [options] TEXT
    ```

    Arguments:

    - `TEXT`

    Options:

    - `--help`, `-h`

        Show help and exit

    - `--port` *PORT*

        Port to use (default: `80`)

    - `--debug`, `-g`

        Enable debug

    ### myprog net ping

    Do ping

    Usage:

    ```
    myprog net ping [options] IP
    ```

    Arguments:

    - `IP`

        target address

    Options:

    - `--help`, `-h`

        Show help and exit

    - `-t`

        Ping the specified host until stopped

    - `-n` *N*

        Number of echo requests to send

---

_class_ doc.**Doc**(_\*, renderer=None, settings=None_)

- _renderer_ - object implementing the `Renderer` protocol. It should have a methods for rendering `p`, `ul`, `br` and other tags. Defaults to the md.`Renderer`, which makes a basic markdown.
- _settings_ - dataclass with some text strings (default sections titles, etc)

---

Doc.**generate**(_node, \*, prog_)

- _node_ - `Group` or `Command`
- _prog_ - program name

---

Any `Doc` methods except the `generate` are considered implementation details.
If you ok with no guarantees, all methods starting with `r_` are override-friendly.

Help strings end up in the generated doc as is. It means they could include a valid markup. It also means
some may be unintentionally interpreted as markup codes, for example, `x*y*z` -> x*y*z.
Of course, codes may be escaped with backslashes, but then backslashes will mess up the `--help` output.

To fix it, paramspecli supports `Markup` objects in place of text strings.
Any object with `plain` method is considered a `Markup`.
paramspecli will call `str(obj)` when producing the doc, and `obj.plain()` when producing the help.

```python

class Md(str):
    # just strip the backslashes
    def plain(self) -> str:
        return self.replace("\\", "")

a = option("--math", help=Md("x\*y\*z"))
```
