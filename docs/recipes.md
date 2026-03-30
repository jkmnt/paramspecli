## Loading file-based defaults

It's common to load parameters defaults from external config files and then
allow CLI to override them.

In a simple cases, this pattern is supported with a help of [const](advanced.md#const-parameters) and [Context](advanced.md#context).
First, [custom_action](advanced.md#actions) loads the config into the context, then dynamic `const` options do the loads.

```python
from paramspecli import Missing, MISSING

@dataclass
class Ctx:
    toml: dict[str, dict[str, str]] | None = None

def load_foo(context: Ctx) -> str | Missing:
    if not context.toml:
        return MISSING
    try:
        return context.toml["app"]["foo"]
    except KeyError:
        return MISSING

def load_toml(context: Ctx, value: Path, **kwargs: Any) -> None:
    with value.open("rb") as f:
        context.toml = tomllib.load(f)

def f(*, foo: str):
    pass

cli = Command(f)
cli.bind(foo=-(const(load=load_foo) | option("--foo", default="a")))
cli.append_action(custom_action("--toml", handler=load_toml, type=PathConv.file(exists=True)))

cli.parse(context=Ctx())
```

This code have some not very evident bug. Argparse parse options in order of appearance on a command line.
The line `myprog --foo b --toml pyproject.toml` would load toml too late, then the `foo` is already processed.

There are two crude solutions to this problem. For one, `--toml` may be defined as a group option, with loadable options moved to the subcommands: `myprog --toml pyproject.toml my_command --foo b`. For another, parse could be restarted if toml found:

```python
ctx = Ctx()
cli.parse(context=ctx)
if ctx.toml:    # toml found, parse again
    cli.parse(context=ctx)
```

Or, simpler, handler may throw a special `ParseAgain` exception.

```python
from paramspecli import ParseAgain

def load_toml(context: Ctx, value: Path, **kwargs: Any) -> None:
    # if second pass, do nothing
    if context.toml:
        return
    # on a first pass, load and restart
    with value.open("rb") as f:
        context.toml = tomllib.load(f)
    raise ParseAgain
```

## Emulating the [FileType](https://docs.python.org/3/library/argparse.html#argparse.FileType)

Don't. Use the `pathlib.Path` methods instead:

```python
def func(*, file: pathlib.Path):
    data=path.read_bytes()

cmd.bind(file=option("--file", type=PathConv.file(exist=True)))
```

## Using `Enum` as a type converter

`StrEnum` is nice and actually works.

```python
class MyEnum(StrEnum):
        A = "a"
        B = "b"

def func(*, foo: MyEnum):
    pass

Command(func).bind(
    foo=-option("--foo", type=MyEnum, choices=MyEnum, default=MyEnum.A)
)
```

## Clean multiarg options

To make the list options less ugly, mix a few mutually exclusive options and flags.
Here, `tags` list may be set manually, set to some predefined value, cleared or left default:

```python
cmd.bind(
    tags=-cmd.add_oneof().include(
        option(
            "--tags",
            nargs="+",
            default=["head", "title", "body"],
        )
        | flag("--tags-recommended", value=["pre", "code"])
        | flag("--tags-not-recommended", value=["blink"])
        | flag("--no-tags", value=[])
    )
)
```

## Generating shell completions

Use the [shtab](https://github.com/iterative/shtab). While there may be some minor incompatibles, generally result is ok.

For external build, use the `Group.build_parser`/`Command.build_parser` method (specially included to expose the generated `ArgumentParser`):

```python

import shtab

cli = Group(prog="prog")
...

parser = cli.build_parser(config=Config())
script = shtab.complete(parser)
print(script)
```

For embedding the completions generation in your app, use the custom action:

```python
def gen_completion(*, parser: ArgumentParser, value: str, **kwargs: Any) -> None:
    script = shtab.complete(parser, value)
    sys.stdout.write(script)
    parser.exit()

cli = Group(prog="prog")
cli.append_action(custom_action("--completion", handler=gen_completion, choices=shtab.SUPPORTED_SHELLS))
```
