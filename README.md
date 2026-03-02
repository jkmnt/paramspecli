# paramspecli

**paramspecli** is a facade for the venerable [argparse](https://docs.python.org/3/library/argparse.html).
It's simple, composable, and fun. But, most important, it's type-safe thanks to the [ParamSpec](https://docs.python.org/3/library/typing.html#typing.ParamSpec) magic.

## Quick start

```python
from paramspecli import Command, argument, option, flag


def ping(addr: str, *, until_stopped: bool, count: int | None):
    print(f"Pinging {addr} ...")


cli = Command(ping, prog="ping")
cli.bind(
    -argument("IP"),
    until_stopped=-flag("-t"),
    count=-option("-n", type=int),
)

result = cli.parse()
result()
```

Running it:

```
$ python ping.py -t -n 10 127.0.0.1
Pinging 127.0.0.1 ...
```

Type checker catches common errors:

```python
cli.bind(
    # "bool" is not assignable to "str"
    -argument("IP", type=bool),
    # Type "bool | None" is not assignable to type "bool"
    until_stopped=-flag("-t", default=None),
    #
    # Argument missing for parameter "count"
)
```

IDE suggestions work too:

<pre>
cli.bind(⏎
    <small>(<strong>addr: str</strong>, *, until_stopped: bool, count: int | None) -> None</small>
</pre>

## Installation

```shell
pip install paramspecli
```

## Key points

**paramspecli** builds hierarchical CLIs with groups and commands.

- Commands match handler functions parameters with arguments and options.
- Arguments are bound to the handler's positional parameters.
- Options are bound to the handler's keyword parameters.
- Groups organize the commands. Groups may be nested. They could act like like an intermediate commands, i.e. have own handlers, options and arguments.
- CLI 'compiles' to the `argparse`, runs it, then outputs the parse result.
- Parse result is a callable. Calling it invokes handlers along the route.

**paramspecli** supports several advanced `argparse` features: help sections, mutually exclusive
options, options with the same destination. And adds a few own, like const options and passing contexts. It also includes a markdown documentation generator.

[Read the documentation](https://jkmnt.github.io/paramspecli)