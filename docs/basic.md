# Basic usage

Let's take a command from the [quick start example](index.md#quick-start) and put it into the group.

```python
from paramspecli import Group, argument, option, flag


def ping(addr: str, *, until_stopped: bool, count: int | None):
    print(f"Pinging {addr} ...")


def server(name: str, *, port: int, debug: bool):
    print(f"Serving {name} on port {port} ...")


cli = Group(prog="myprog")

with cli.add_group("net") as group:
    with group.add_command("ping", ping) as cmd:
        cmd.bind(
            -argument("IP"),
            until_stopped=-flag("-t"),
            count=-option("-n", type=int),
        )

    with group.add_command("server", server) as cmd:
        cmd.bind(
            -argument("TEXT"),
            port=-option("--port", type=int, default=80),
            debug=-flag("--debug", "-g"),
        )

route = cli.parse()
route()
```

Running it:

```
$ python myprog.py net ping -t -n 10 127.0.0.1
Pinging 127.0.0.1 ...

$ python myprog.py net server --port 8080 -g breakfast
Serving breakfast on port 8080 ...

$ python myprog.py net --help
usage: myprog net [--help] {ping,server} ...

options:
  --help, -h     Show help and exit

commands:
  {ping,server}
    ping
    server
```

The example is self-explaining enough, except the **crucial bit**. Did you notice the unnoticeable minus sign prefixing the option?
You **must** add it for the type check to pass:

```python
cli.bind(
    count=-option("-n", type=int),
)
```

Why? In short, paramspecli [lies to the type checker](qa.md). In the name of good, of course.

If you don't like minus, use the `t` property. Or `t` object, which overloads `[]`, `@`, `()` operations. Choose one style
and stick to it.

```python
from paramspecli import t

option("-n").t
t(option("-n"))
t[option("-n")]
t @ option("-n")
option("-n") @ t
```

!!! question "Why `with` and context managers?"

    Just for an aesthetic - they paint a very nice visual hierarchy. They are not required and in fact do nothing.

---

Now let's take a closer look at the building blocks.

## Arguments

Arguments are instances of the `Argument` class. They are created by the `argument` factory function.
Arguments are positional-only, and it's an error to bind it by keyword.

---

**argument**(_metavar, type=None, \*, help=None, nargs=None, default=None, choices=None_)

- _metavar_ - metavar name. _Note that it's required_
- _type_ - callable to convert string into the parameter type
- _help_ - help string
- _nargs_
    - int: Consume fixed number of words
    - `*`: Consume zero or more words
    - `+`: Consume one or more words
    - `?`: Consume zero or one word (optional mode)

- _default_ - Allowed if _nargs_=`"?"`. May be anything.
  If _default_ is a string, it will be converted by _type()_, otherwise left as is.
- _choices_ - Iterable of allowed values

| Code                                                      | Command line | Result            |
| --------------------------------------------------------- | ------------ | ----------------- |
| `#!python argument("N", type=int)`                        | `1`          | `#!python 1`      |
| `#!python argument("N", type=int, nargs="*")`             | `1`          | `#!python [1]`    |
|                                                           | `1 2`        | `#!python [1, 2]` |
|                                                           | ` `          | `#!python []`     |
| `#!python argument("N", type=int, nargs="?", default=-1)` | `1`          | `#!python 1`      |
|                                                           | ` `          | `#!python -1`     |

## Options

Options are instances of the `Option` class. They are created by one of factory functions.
Options are keyword-only, and it's an error to bind it positionally.

### option

Tries to consume a word from the command line. Result is a (type converted) word. If it is not present, result is _default_.

---

**option**(_\*names, type=None, help=None, default=None, nargs=None, choices=None, metavar=None, show_default=None_)

- _names_ - one or more names on a command line. Should start from the `-`, for example, `--foo`, `-g`.
- _type_ - callable to convert string into the parameter type
- _help_ - help string. Also may be set to `False` hide option from `--help`.
- _default_ - result if option is missing. May be anything. If _default_ is a string, it will be converted by _type()_, otherwise left as is.
- _nargs_:
    - int: Consume fixed number of words
    - `+`: Consume one or more words
    - `*`: Consume zero or more words
    - `?`: Consume zero or one word. If zero, `...` (ellipsis) is returned instead.
- _choices_ - Iterable of allowed values.
- _metavar_ - meta-variable string. If nargs is a fixed number, may be a tuple of strings.
- _show_default_ - show default value in help:
    - `True`: show _default_ value
    - `False`: show nothing
    - `None`: show _default_ if it makes sense
    - str: show this very string

| Code                                                     | Command line             | Result                       |
| -------------------------------------------------------- | ------------------------ | ---------------------------- |
| `#!python option("--addr")`                              | `--addr www.example.com` | `#!python "www.example.com"` |
|                                                          | ` `                      | `#!python None`              |
| `#!python option("--width", type=int, default=80)`       | `--width 120`            | `#!python 120`               |
|                                                          | ` `                      | `#!python 80`                |
| `#!python option("--user", nargs="+")`                   |                          |                              |
|                                                          | `--user bob`             | `#!python ["bob"]`           |
|                                                          | `--user bob alice`       | `#!python ["bob", "alice"]`  |
|                                                          | ` `                      | `#!python None`              |
| `#!python option("--xyz", nargs=3, type=int)`            | `--xyz 0 5 -1`           | `#!python [0, 5, -1]`        |
| `#!python option("--threads", nargs="?", type=int)`      | `--threads 2`            | `#!python 2`                 |
|                                                          | `--threads`              | `#!python ...`               |
|                                                          | ` `                      | `#!python None`              |
| `#!python option("--day", choices=("sunday", "monday"))` | `--day sunday`           | `#!python "sunday"`          |
|                                                          | `--day monday`           | `#!python "monday"`          |
|                                                          | ` `                      | `#!python None`              |

### repeated_option

Like [option](#option), but allowed to present multiple times on a command line.
Result is a list of (type converted) words. If missing, result is an empty list.

---

**repeated_option**(_names, \*, type=None, help=None, nargs=None, choices=None, flatten=False, metavar=None_)

- _names_, _type_, _help_, _choices_, _metavar_, _show_default_ - see [option](#option)
- _nargs_ - int, `+` or `*`. Consume fixed or unlimited number of words for each option occurence.
- _flatten_ - Meaningful only if _nargs_ set. Flattens the individual lists into the
  single list. Under the hood, it switches the argparse action from `append` to the `extend`.

| Code                                                                    | Command line                 | Result                          |
| ----------------------------------------------------------------------- | ---------------------------- | ------------------------------- |
| `#!python repeated_option("--port", type=int)`                          | `--port 80 --port 8080`      | `#!python [80, 8080]`           |
|                                                                         | ` `                          | `#!python []`                   |
| `#!python repeated_option("--port", type=int, nargs="+")`               | `--port 80`                  | `#!python [[80]]`               |
|                                                                         | `--port 80 --port 8080 8081` | `#!python [[80], [8080, 8081]]` |
|                                                                         | ` `                          | `#!python []`                   |
| `#!python repeated_option("--port", type=int, nargs="+", flatten=True)` | `--port 80`                  | `#!python [[80]]`               |
|                                                                         | `--port 80 --port 8080 8081` | `#!python [80, 8080, 8081]`     |
|                                                                         | ` `                          | `#!python []`                   |

---

### flag

Simple flag. Result is _value_. If missing, result is _default_.

---

**flag**(_names, \*, help=None, value=True, default=..., show_default=None_)

- _names_, _help_, _show_default_ - see [option](#option)
- _value_ - result if flag is present. May be anything.
- _default_ - result if flag is missing. If not set, choosen automatically between `True`, `False` and `None`
  depending on a _value_

| Code                                                         | Command line | Result               |
| ------------------------------------------------------------ | ------------ | -------------------- |
| `#!python flag("--debug")`                                   | `--debug`    | `#!python True`      |
|                                                              | ` `          | `#!python False`     |
| `#!python flag("--noerr", value=False)`                      | `--noerr`    | `#!python False`     |
|                                                              | ` `          | `#!python True`      |
| `#!python flag("--cheat", value="iddqd")`                    | `--cheat`    | `#!python "iddqd"`   |
|                                                              | ` `          | `#!python None`      |
| `#!python flag("--cheat", value="iddqd", default="nocheat")` | `--cheat`    | `#!python "iddqd"`   |
|                                                              | ` `          | `#!python "nocheat"` |

### switch

A `--foo/--no-foo` style complimentary flags. Result is `True` or `False` depending on a flag. If missing, result is _default_.

---

**switch**(_names, \*, help=None, default=False, show_default=None_)

- _names_, _help_, _show_default_ - see [option](#option)
- _default_ - result if flag is missing. May be anything.

| Code                                       | Command line | Result           |
| ------------------------------------------ | ------------ | ---------------- |
| `#!python switch("--magic")`               | `--magic`    | `#!python True`  |
|                                            | `--no-magic` | `#!python False` |
|                                            | ` `          | `#!python False` |
| `#!python switch("--magic", default=True)` | `--magic`    | `#!python True`  |
|                                            | `--no-magic` | `#!python False` |
|                                            | ` `          | `#!python True`  |
| `#!python switch("--magic", default=None)` | `--magic`    | `#!python True`  |
|                                            | `--no-magic` | `#!python False` |
|                                            | ` `          | `#!python None`  |

### count

A `-vvv` style flag. Result is a number of the flag occurences.
If missing, result is _default_

---

**count**(_names, \*, help=None, default=0, show_default=None_)

- _names_, _help_, _show_default_ - see [option](#option)
- _default_ - int or `None`. If int, it's also the initial count value.

| Code                                 | Command line | Result          |
| ------------------------------------ | ------------ | --------------- |
| `#!python count("-v")`               | `-vv`        | `#!python 2`    |
|                                      | ` `          | `#!python 0`    |
| `#!python count("-v", default=40)`   | `-vv`        | `#!python 42`   |
|                                      | ` `          | `#!python 40`   |
| `#!python count("-v", default=None)` | `-vv`        | `#!python 2`    |
|                                      | ` `          | `#!python None` |

### repeated_flag

Like a flag, but may present multiple times on a command line.
Result is a list of _value_. If missing, result is an empty list.
Repeated flags are most useful if [mixed](advanced.md#mixed-options).

---

**repeated_flag**(_names, \*, help=None, value=True_)

- _names_, _help_ - see [option](#option)
- _value_ - value to append to the result list for each flag occurence. May be anything.

| Code                                             | Command line    | Result                      |
| ------------------------------------------------ | --------------- | --------------------------- |
| `#!python repeated_flag("--hard")`               | `--hard`        | `#!python [True]`           |
|                                                  | `--hard --hard` | `#!python [True, True]`     |
|                                                  | ` `             | `#!python []`               |
| `#!python repeated_flag("--hard", value="core")` | `--hard`        | `#!python ["core"]`         |
|                                                  | `--hard --hard` | `#!python ["core", "core"]` |
|                                                  | ` `             | `#!python []`               |

---

!!! tip

    `Option` and `Argument` objects are immutable and may be reused in different commands. It's a great way to reduce copypaste.

## Commands

Commands are instances of the `Command` class. They could be created directly and attached to the groups later. For hierarchical CLIs it's simpler to use the `Group.add_command()` method, which combines the creation and attaching.

---

_class_ **Command**(_func, \*, help=None, info=None, usage=None, epilog=None, prog=None, add_help=True_)

- _func_ - command handler
- _help_ - short help string. Shown in the commands list of a parent group help.
- _info_ - long description
- _usage_ - usage string. By default, it's generated automatically.
- _epilog_ - epilog message
- _prog_ - program name. Part of the default usage string.
- _add_help_ - add `--help` action

## Groups

Similar the to commands, groups are created by instantiating the `Group` class or by calling the `Group.add_group()` method.
Groups may have [own options and handlers](advanced.md#group-options).

---

_class_ **Group**(_\*, help=None, info=None, usage=None, epilog=None, prog=None, title=None, headline=None, metavar=None, default_func=..., add_help=True_)

- _help_ - short help string. Shown in the commands list of a parent group help.
- _info_ - long description
- _usage_ - usage string. By default, it's generated automatically.
- _epilog_ - epilog message
- _prog_ - program name. Part of the default usage string.
- _title_ - title for the list of own commands. Default is set in [Configuration](advanced.md#configuration).
- _headline_ - description for the list of own commands
- _metavar_ - meta-variable name for own commands
- _default_func_ - default handler if no command was choosen. By default, prints own help. If set to `None`,
  choosing command is required.
- _add_help_ - add `--help` action

---

Most of the `Group` and `Command` settings are presentational.

??? info "See what they mean"

    Group

    ```
    usage: PROG GROUP_METAVAR ...

    GROUP_INFO

    GROUP_TITLE:
      GROUP_HEADLINE

    GROUP_METAVAR
      command      COMMAND_HELP

    EPILOG
    ```

    Command

    ```
    usage: COMMAND_USAGE

    COMMAND_INFO

    SECTION_TITLE:
      SECTION_HEADLINE

      --option OPTION_METAVAR  OPTION_HELP

    EPILOG
    ```

---

Group.**add_group**(_name, \*args, \*\*kwargs_)

Group.**add_command**(_name, \*args, \*\*kwargs_)

- _name_ - group or command name as seen on the command line. _May be a tuple to provide aliases_
- _args_, _kwargs_: Forwarded to the `Group` / `Command` class

---

Assembling CLI from separate groups and commands is possible too:

```python title="ping.py"
from paramspecli import Command

def ping():
    pass

cmd = Command(ping)
```

```python title="main.py"
from paramspecli import Group
from . import ping

cli = Group()
netgroup = Group()

netgroup["ping"] = ping.cmd
# aliases are supported too
cli["net", "network"] = netgroup

```

It might be more readable to define all group's nodes at once:

```python
cli.nodes = {
    "ping": ping.cmd,
    ("net", "network"): netgroup,
}
```

!!! tip

    Same `Command` objects may be reused in different groups. It's a simple way to make a top-level
    shortcut for some five-groups-deep command.

## Parse result

Parsing the command line and executing handlers are separate steps. Inside the `parse()` method, paramspecli 'compiles' itself to the `argparse.ArgumentParser`,
runs it to process the command line, then composes the final `Route` object.

`Route` contains a sequence of handlers.
It's a sequence because groups may have [own handlers](advanced.md#group-options) too.
For convenience, `Route` is callable and calling it invokes handlers one by one.

!!! tip

    Parse and execute separation allows to garbage collect CLI objects and free resources in
    long running programs. For this to happen, CLI code should reside in a separate function:

    ```python
    def process_commandline():
        cli = Group()
        cli.add_group(...)
        # etc
        return cli.parse()

    def main():
        route = process_commandline()
        # CLI object are no longer exist at this point
        route()
    ```

---

Group.**parse**(_input=None, \*, config=None, context=None_)

Command.**parse**(_input=None, \*, config=None, context=None_)

- _input_ - Sequence of strings to parse. Defaults to sys.argv if None.
- _config_ - [argparse 'compilation' settings](advanced.md#configuration)
- _context_ - Optional context object to communicate between groups and commands

---

Handlers may also be examined and called manually:

```python
route = cli.parse("net ping -t -n 10 127.0.0.1".split())

# Invoke the whole handlers sequence
route() # # Pinging 127.0.0.1 ...

# Invoke the final handler only
print(route[-1]) # Handler(func=<function ping at 0xDEADBEEF>, arguments=['127.0.0.1'], options={'until_stopped': True, 'count': 10})
route[-1]() # Pinging 127.0.0.1 ...

# Invoke handlers manually
for handler in route:
    print(handler)
    handler()

# Or even super manually
for handler in route:
    if handler.func:
        handler.func(*handler.arguments, **handler.options)

```
