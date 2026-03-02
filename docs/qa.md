# Answers

- Are environment valiables supported?

    Do it manually:

    ```python
    cmd.bind(
        login=-option(
            "--password",
            default=os.environ.get("MY_PASSWORD"),
            help="Server password",
            show_default="Won't tell you !",
        )
    )
    ```

    Generally, environment variables should be treated as an external input
    and validated:

    ```python
    def get_default_nthreads() -> int | None:
        try:
            val = int(os.environ["MYSERVER_NTHREADS"])
        except (ValueError, KeyError):
            return None
        return val if 0 < val < 100 else None

    cmd.bind(
        threads=-option("--threads", type=int, default=get_default_nthreads() or 4),
    )
    ```

- What about the bash autocompletion?

    Maybe someday.

- Where is the [FileType](https://docs.python.org/3/library/argparse.html#argparse.FileType) with auto-opening?

    Use the `pathlib.Path` methods instead:

    ```python
    def func(*, file: pathlib.Path):
        data=path.read_bytes()

    cmd.bind(file=option("--file", type=PathConv.file(exist=True)))
    ```

- May I use `Enum` as a type converter?

    `StrEnum` is nice and actually works.

    ```python
    class MyEnum(StrEnum):
          A = "a"
          B = "b"

    def func(*, foo: MyEnum):
        pass

    Command(func).bind(
        foo=-option("--foo", type=MyEnum, choices=tuple(MyEnum))
    )
    ```

- Tell me more about this [minus operator hack](basic.md#basic-usage)

    paramspecli abuses the [ParamSpec](https://docs.python.org/3/library/typing.html#typing.ParamSpec):

    ```python

    def func(*, port: int | None) -> None: ...

    cmd = Command(func)
    opt = option("--port", type=int)

    reveal_type(opt) # type is "Option[int, None]"
    reveal_type(-opt) # type is "int | None"

    reveal_type(cmd.bind) # type is "(*, port: int | None) -> None"
    cmd.bind(port=-opt) # typechecks ok!

    ```

    The negation operator is type-annotated as returning the `Option`'s resulting type. Signatures match, type checker is happy.
    It's a lie - in runtime it's still the same `Option` class.

    ```python
    class Option[T]:

        def __neg__() -> T:
            return self # type: ignore
    ```

    Minus is choosen as producing the minimum visual noise. Also it's a nod to the `-` options prefix character.

- Why such a stupid name?

    CLI libs should have `cli` in their name. It's the law. And `clit` is already taken on the PyPI.
