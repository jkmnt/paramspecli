# Advanced usage

## Mixed options

Several options may be mixed by the `|` operator to target the same handler parameter.
Last seen (on a command line) option wins. If no options from the mix are present, default of the first registered option wins:

Here, the _time_ parameter will be one of `--timestamp`, `--iso` , `--off` options (or `None`):

```python
def alarm(*, time: int | str | bool | None):
    pass

Command(alarm).bind(
    time=-(
        # this comment is for the nice formatting with black/ruff
        option("--timestamp", type=int)
        | option("--iso")
        | flag("--off", value=False)
    )
)
```

| Code                                                                                         | Command line           | Result           |
| -------------------------------------------------------------------------------------------- | ---------------------- | ---------------- |
| `#!python option("--pid", type=int, default=1)` <br /> \| `#!python option("--prog")`        | `--pid 123`            | `#!python 123`   |
|                                                                                              | `--prog cat`           | `#!python "cat"` |
|                                                                                              | `--pid 123 --prog cat` | `#!python "cat"` |
|                                                                                              | ` `                    | `#!python 1`     |
| `#!python flag("--slow", value=10, default=0)` <br /> \| `#!python flag("--fast", value=99)` | `--slow`               | `#!python 10`    |
|                                                                                              | `--fast`               | `#!python 99`    |
|                                                                                              | `--fast --slow`        | `#!python 10`    |
|                                                                                              | ` `                    | `#!python 0`     |

Repeated options are mixed by the `+` operator. All options go into the resulting list in order of appearance on a command line.

Here, the _praises_ parameter may contain any number of `--small`, `--fast`, or `--reliable` options values:

```python
def sqlite(*, praises: list[int | str] | None):
    pass

Command(sqlite).bind(
    praises=-(
        #
        repeated_option("--small", type=int)
        + repeated_flag("--fast", value="fast")
        + repeated_flag("--reliable", value="yes")
    )
)
```

| Code                                                                                                      | Command line                       | Result                          |
| --------------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------------------- |
| `#!python repeated_option("--pid", type=int)` <br /> + `#!python repeated_option("--prog")`               | `--pid 123`                        | `#!python [123]`                |
|                                                                                                           | `--prog cat`                       | `#!python ["cat"]`              |
|                                                                                                           | `--pid 123 --prog cat --prog sudo` | `#!python [123, "cat", "sudo"]` |
|                                                                                                           | ` `                                | `#!python None`                 |
| `#!python repeated_flag("--python", value="py")` <br /> + `#!python repeated_flag("--rust", value=False)` | `--python --rust --rust`           | `#!python ["py", False, False]` |
|                                                                                                           | ` `                                | `#!python None`                 |

## Help sections

It's common to have `--help` with options sorted by sections: basic, experimental, reports, logging, etc.

Options are included in sections by a nice subscription syntax.
Or by calling the `include()` method of section.

```python
cmd = Command(func, add_help=False)
common = cmd.add_section("base options", headline="For every day use")
unknown = cmd.add_section("unknown options", headline="???")

cmd.bind(
    quiet=-flag("-q", help="Quiet")[common],
    recurse=-flag("-r", help="Recursive")[common],
    cage=-flag("--cage", value=4.33)[unknown],
    e_or_pi=-(flag("--e", value=2.72) | flag("--pi", value=3.14))[unknown],
)

cmd.parse()
```

??? note "See `--help` output"

    ```
    usage: prog [-q] [-r] [--cage] [--e] [--pi]

    base options:
      For every day use

      -q          Quiet
      -r          Recursive

    unknown options:
      ???

      --cage
      --e
      --pi
    ```

---

Command.**add_section**(_title, \*, headline=None_)

Group.**add_section**(_title, \*, headline=None_)

- _title_ - title for the list of options
- _headline_ - description of the contained options

---

## Mutually exclusive options

Some options could be made mutually exclusive by placing them in the `Oneof` section.
Options are included in `Oneof` by a wrapping call, or by oneof's `include()` method.

Here, `--fast` and `--cheap` options are mutually exclusive. `--http` and `--https` options
are forbidden to use together too:

```python
cmd = Command(func)
choose_one = cmd.add_oneof()
http_or_https = cmd.add_oneof()

cmd.bind(
    fast=-choose_one(option("--fast")),
    cheap=-choose_one(option("--cheap")),
    protocol=-http_or_https(flag("--http", value="http") | flag("--https", value="https"))
)
```

---

Command.**add_oneof**(_\*, required=False_)

Group.**add_oneof**(_\*, required=False_)

- _required_ - Require at least one option

---

!!! warning

    Due to the `argparse` implementation, [help sections](#help-sections) and oneofs are not orthogonal.
    If help sections are used, make sure all options of the concrete `Oneof` are in the same section.

## Required options

Options should be optional, but anyway. The `required()` function returns the marked-as-required copy of option:

```python
from paramspecli import required

cmd.bind(
    password=-required(option("--password")),
)
```

## Deprecating options

Options may be marked as deprecated via the `deprecated()` function. It return the marked-as-deprecated copy of option.
There would be a warning if option is used on a command line.
_Python 3.13+_

```python
from paramspecli import deprecated

cmd.bind(
    python2=-deprecated(option("--py2")),
)
```

## Path type

paramspecli includes a handy [pathlib.Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path) converter.

---

_class_ **PathConv**(_kind=None, \*, exists=None, resolve=True_)

- _kind_ - `"file"`, `"dir"` or `None` (don't care). Checks path type if applicable.
- _exists_ - check the path existence
    - `True`: path should exist
    - `False`: path should not exist
    - `None`: don't care
- _resolve_ - resolve to absolute path

---

There are also a shortcut classmethods for both path kinds.

Example:

```python
from pathlib import Path
from paramspecli import PathConv


def copy(src: Path, dest: Path):
    pass

Command(copy).bind(
    -argument("SRC", kind=PathConv.file(exists=True)),
    -argument("DST", kind=PathConv.dir(exists=False))
)

```

## Group options

Groups may behave like an intermediate commands, i.e. have a handler and own parameters.

Such groups are created by instantiating the `CallableGroup` class
or by calling the `Group.add_callable_group()` method.
They borrow a `func` setting and a `bind()` method from the `Command`.

---

One useful application of group options is to perform some global initialization.

Here, the CLI-level `--color` flag is processed before any selected command:

```python

def f():
    pass

def handle_color(*, use_color: bool):
    if use_color:
        from colorama import just_fix_windows_console
        just_fix_windows_console()


cli = CallableGroup(handle_color)
cli.bind(use_color=-flag("--color"))

with cli.add_command("f", f) as cmd:
    cmd.bind()
```

Each handler's parameters are isolated and reside in own namespaces.

## Context

Groups may pass information down the route in the user-defined context object. Handlers wishing to receive context should bind one of their parameters to the `Context()` marker.

Here, `cli` loads app settings from the `toml` config. Commands may opt-in to access them:

```python
from paramspecli import Context, CallableGroup, PathConv, option

@dataclass
class Settings:
    debug: bool


def load_toml(*, ctx: Settings, config: Path | None):
    if config:
        with config.open("rb") as f:
            cfg = tomllib.load(f)
            ctx.debug = cfg.get("debug", False)


def f(*, ctx: Settings):
    print(ctx.debug)


cli = CallableGroup(load_toml)
cli.bind(
    ctx=-Context(),
    config=-option("--config", type=PathConv.file(exists=True)),
)

with cli.add_command("f", f) as cmd:
    cmd.bind(ctx=-Context[Settings]())  # Note: Context may be specialized for the type-safety

settings = Settings(debug=False)

res = cli.parse(context=settings)
res()
```

!!! tip

    [dataclass](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass) and [TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict) works the best for the context objects.

In rare cases when handlers need to access the very parsed route, just include it into the context manually:

```python
from paramspecli import Route

@dataclass
class Ctx:
    route: Route


def f(*, ctx: Ctx):
    print(ctx.route)

with cli.add_command("f", f) as cmd:
    cmd.bind(ctx=-Context[Ctx]())

ctx = Ctx(route=Route([]))
res = cli.parse(context=ctx)
# patching context after the parse
ctx.route = res

res()
```

## Const parameters

The `const` option sets fixed or dynamic parameter default.

Used by it's own, it allows to integrate existing functions into the CLI without extra wrappers.
Mixed with other options, it sets parameter default in a more explicit way.

Here, _login_ and _frob_ parameters are internal, while _bar_'s default is defined by `const`.

```python
from paramspecli import Const

def third_party_function(login: str, password: str, *, frob: bool, foo: int | None, bar: int):
    pass

with cli.add_command("frobnicate", third_party_function) as cmd:
    cmd.bind(
        -const("bob"),
        -argument("PASSWORD"),
        frob=-const(True),
        foo=-option("--foo", type=int),
        bar=-(const(42) | option("--bar", type=int)),
    )
```

Const may load it's value dynamically at parse time. This feature makes it easy to support environment variables.

Here, `password` is loaded from the env variable. If loader returns the special `MISSING` value, load result is
ignored and default of the option (`"qwerty"`) wins:

```python
from paramspecli import MISSING

def login(*, password: str) -> None:
    pass

def load_password(context: Any):
    return os.environ.get("MY_PASSWORD", MISSING)

cli = Command(login)
cli.bind(
    password=-(
        const(load=load_password)
        | option("--password", default="qwerty")
    )
)
```

Loaders may examine the [context](#context) before taking decisions. See example in [loading file-based defaults](recipes.md#loading-file-based-defaults).

## Actions

Actions are options with side effects. They are not bound to the handlers. Actions are attached via `Group.append_action` or `Command.append_action`
methods. Two common actions are included: `version_action` and `help_action`.

Handling `--version`:

```python
from paramspecli import version_action

cli = Group()
cli.append_action(version_action("42"))
cli.parse()()
```

```
$ python prog.py --version
42
```

---

The `custom_action` calls the used-defined handler at parse time.

**custom_action**(_\*names, handler, type=None, nargs=None, default=None, help=None, choices=None, metavar=None, show_default=None_)

- _names_, _type_, _nargs_, _help_, _choices_, _metavar_, _show_default_ - see [option](basic.md#option)
- _default_: used in `--help` output only
- _handler_ (_\*, context, parser, value, option_string, config, \*\*kwargs_)
    - _context_: [Context](#context) object or `None`
    - _parser_: running `ArgumentParser`
    - _value_: value parsed from the command line after the _type()_ conversion. May be `None` if _nargs_ = 0.
      Will be `paramspecli.MISSING` if _nargs_ = `?` and no words present.
    - _option_string_: actual matched option string from the command line
    - _config_: [Config](#configuration) object

Here, we implement a custom `--number` action updating the context:

```python
cli = Group()

def handle_number(*, context: dict[str, int], value: int, **kwargs: Any):
    context["number"] = value

cli.append_action(custom_action("--number", handler=handle_number, type=int))

ctx = {}
cli.parse("--number 42", context=ctx)
print(ctx["number"]) # 42
```

This technique is useful for [loading file-based defaults](recipes#loading-file-based-defaults).
!!! tip

    Custom actions have access to the generated parser and able to call it's methods. This is how the `help_action` is implemented -
    it calls `parser.print_help()` followed by `parser.exit()`

## Lazy imports

Typically, only one of the imported handlers is ever invoked by the CLI. Some import-heavy handlers
may be lazy imported with the help of the `resolve_later()` wrapper.
The startup time reduction and memory savings could be significant.

Here, `heavy.py` file would be loaded only then `heavy_handler()` is actually used.

```python title="heavy.py"
import sqlalchemy
import matplotlib
import requests
import pandas

def handler(*, data: str | None):
    pass
```

```python title="main.py"
from paramspecli.util import resolve_later

def heavy_handler():
    from . import heavy
    return heavy.handler

cmd = Command(resolve_later(heavy_handler))
cmd.bind(data=-option("--data"))
```

!!! warning

    The `heavy_heandler()` is type safe with `pyright`, which infers it's return type just right.
    `mypy` and `ty` infers it as `Any`/`Unknown`. Of course, it could be copypaste-annotated,
    but it kind of misses the point.

## Configuration

A few aspects of the generated `ArgumentParser` may be tuned by passing a custom `Config` to the `Group.parse()` method.

`Config` is a dataclass with a following fields:

- _show_default_ = `True`. Defaults are printed in help where it makes sense. Set to `False` to globally opt-out.
  Options may set own _show_default_ to selectively opt-in.

- _propage_epilog_ = `False`. Set it to the `True` to force groups and commands show the same epilog as the root group. It's a simple way to ensure epilogs are consistent.

<!-- prettier-ignore -->
- _catch_typeconv_exceptions_ = `False`. By default, argparse recognizes
  only a few exceptions while type converting: `ValueError`, `TypeError` and `ArgumentTypeError`. Other exceptions bubble up to the program and produce ugly call traces. Set `True` to catch all type converter exceptions and report them as nice CLI errors.

    !!! tip

        Alternatively, there is a **catch_all** decorator to wrap type converters:

        ```python
        from paramspecli.util import catch_all

        @catch_all
        def to_ip(s: str):
        return IPv4Address(s)

        cmd.bind(-argument("IP", type=to_ip))

        ```

- _allow_abbrev_ = False. Allow argparse do the guesswork and accept sloppy command line.
- _parser_class_. Allows to use alternative parser class instead of the `ArgumentParser`
- _formatter_class_ - Allows to choose `HelpFormatter`-compatible formatter. By default, set to a slightly modified one, which disables wrapping if there are manual line breaks in text.
- _ignore_unknown_args_ - Silently ignore any unrecognized args and store them into the `Route.unknown_args`. _Added in 0.2.2_
- _root_parser_extra_kwargs_ - dict of extra kwargs for the root `ArgumentParser()`
- _sub_parser_extra_kwargs_ - dict of extra kwargs for every sub `ArgumentParser()`
