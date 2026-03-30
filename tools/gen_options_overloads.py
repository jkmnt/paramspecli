# Q&D: generate overwhelming number of option overloads

from typing import Any


def iter_matrix(src: Any):
    (common, *head_row), *data_rows = src
    for data_row in data_rows:
        head_col, *data_cols = data_row
        for col_row, data_col in zip(head_row, data_cols):
            yield common | head_col | col_row, data_col


def render_option(vars: dict[str, Any], result_type: str, *, desc: str, name: str) -> str:

    generics = [typ for typ in "TDC" if typ in result_type]
    generics_line = f"[{', '.join(generics)}]" if generics else ""

    args = [f"    {k}: {v}," for k, v in vars.items()]
    args.sort()
    args.reverse()

    res = f"""\
{desc}
@overload
def {name}{generics_line}(
    *names: str,
    #
{'\n'.join(args)}
    #
    help: str | bool | Markup | None = None,
    choices: Iterable[{'T' if 'T' in result_type else 'str'}] | None = None,
    metavar: str | None = None,
    show_default: bool | str | None = None,
) -> {result_type}: ...
"""
    return res


TYPE_NONE = {"type": "None = None"}
TYPE_T = {"type": "TypeConverter[T]"}
NARGS_NONE = {"nargs": "None = None"}
NARGS_MANY = {"nargs": 'int | Literal["*", "+"]'}
NARGS_OPT = {"nargs": 'Literal["?"]'}
CONST = {"const": "C"}
FLATTEN_TRUE = {"flatten": "Literal[True]"}
FLATTEN_FALSE = {"flatten": "Literal[False] = False"}
DEFAULT_NONE = {"default": "None = None"}
DEFAULT_STR = {"default": "str"}
DEFAULT_D = {"default": "D"}

# fmt: off
option_str = [
    [TYPE_NONE,         DEFAULT_NONE,       DEFAULT_D],
    [NARGS_NONE,        "str, None",        "str, D"],
    [NARGS_MANY,        "list[str], None",  "list[str], D"],
    [NARGS_OPT | CONST, "str | C, None",    "str | C, D"],
]

option_t = [
    [TYPE_T,            DEFAULT_NONE,       DEFAULT_STR,    DEFAULT_D],
    [NARGS_NONE,        "T, None",          "T, T",         "T, D"],
    [NARGS_MANY,        "list[T], None",    "list[T], T",   "list[T], D"],
    [NARGS_OPT | CONST, "T | C, None",      "T | C, T",     "T | C, D"],
]

repeated_str = [
    [TYPE_NONE,                     DEFAULT_NONE,       DEFAULT_D],
    [NARGS_NONE,                    "str, None",        "str, D"],
    [NARGS_MANY | FLATTEN_FALSE,    "list[str], None",  "list[str], D"],
    [NARGS_MANY | FLATTEN_TRUE,     "str, None",        "str, D"],
    [NARGS_OPT | CONST,             "str | C, None",    "str | C, D"],
]

repeated_t = [
    [TYPE_T,                        DEFAULT_NONE,       DEFAULT_STR,    DEFAULT_D],
    [NARGS_NONE,                    "T, None",          "T, T",         "T, D"],
    [NARGS_MANY | FLATTEN_FALSE,    "list[T], None",    "list[T], T",   "list[T], D"],
    [NARGS_MANY | FLATTEN_TRUE,     "T, None",          "T, T",         "T, D"],
    [NARGS_OPT | CONST,             "T | C, None",      "T | C, T",     "T | C, D"],
]
# fmt: on


def test_name(args: dict[str, Any]):
    return "test_{i}_" + "__".join(f"{k}_{v}" for k, v in args.items())


res = []

res.append("#---")

for i, (args, ret) in enumerate((*iter_matrix(option_str), *iter_matrix(option_t)), 1):
    res.append(render_option(args, f"Option[{ret}]", desc=f"# {i}.\n# {args}", name="option"))

res.append("#---")

for i, (args, ret) in enumerate((*iter_matrix(repeated_str), *iter_matrix(repeated_t)), 1):
    res.append(render_option(args, f"RepeatedOption[{ret}]", desc=f"# {i}.\n# {args}", name="repeated_option"))

print("\n\n".join(res))
