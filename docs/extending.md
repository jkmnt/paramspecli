# Extending paramspecli

There are a few extension points to the paramspecli.

## Type converters

The most common extension is a custom type converter. Type converter is a callable converting string to the parameter type.

Example of `int` converter with some validation:

```python
class IntConv:
    def __init__(self, min: int | None = None, max: int | None = None, base: int = 10):
        self.min = min
        self.max = max
        self.base = base

    def __call__(self, arg: str) -> int:
        val = int(arg, base=self.base) # may rise ValueError
        if self.min is not None and self.val < self.min:
            raise ArgumentTypeError(f"{val} is too small")
        # more checks follows
        return val


cmd.bind(foo=-option("--foo", type=IntConv(min=0, max=42)))
```

## Option factories

In some cases, it's worth to code a custom option factory function.

Example of custom regexp option:

```python
import re
from paramspecli.fake import Option
from paramspecli.util import catch_all

def regexp(*names: str, help: str | bool | None = None) -> Option[re.Pattern[str], None]:
    conv = catch_all(re.compile)
    return Option(names=names, type=conv, help=help, metavar="REGEXP")

cmd.bind(match_re=-regexp("--match"))

```

The factory function should return the instance of the generic `Option` class.
To play nice with the rest of the typing, Option must be specialized by two type parameters:

- _T_ - type of result if option is present
- _D_ - type of result if option is missing

In most cases Option resulting type would be Union\[_T_, _D_\]. _D_ is starting to be important when option is mixed with another options.

---

_class_ **Option**\[_T_, _D_\](_names, \*, type=None, help=None, nargs=None, default=None, const=None,
required=False, choices=None, metavar=None, action=None, deprecated=False, extra=None_)

_class_ **Argument**\[_T_, _D_\](_metavar, \*, type=None, help=None, nargs=None, choices=None, default=None, extra=None_)

- _names_ - tuple of names
- _type_ - type converter
- _help_ - help message
    - str: this string
    - `None`: nothing
    - `False`: hide option from the `--help` output
- _hard_show_default_ - show default in help message
    - `True`: show _default_
    - `False`: show nothing
    - str: show this very string
    - `None`: consult the _soft_show_default_
- _soft_show_default_ - show default in help message unless globally disabled
    - `True`: show _default_
    - `False`: show nothing
    - str: show this very string
- _required_, _choices_, _metavar_, _action_, _nargs_, _default_, _const_, _deprecated_ - forwarded to the `ArgumentParser.add_argument()`
- _extra_ - dict of extra \*\*kwargs for the `ArgumentParser.add_argument()`

---

If option is repeated (that is, action is `extend`, `append`, or `append_const`), factory should return the `RepeatedOption[T]` class. This is a list-producing variant of `Option`.

## Actions

Custom actions should return the instance of the `Action` class. The `Action` has a same constructor as an `Option`, but since actions are not bound to parameters, there is no need for type specialization.

This is how the [version_action()](advanced.md#actions) factory function is defined:

```python
def version_action(
    version: str,
    *,
    help: str | Markup | bool = "Show program's version number and exit"
) -> Action:
    return Action(("--version",), action="version", help=help, extra={"version": version})
```
