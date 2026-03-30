# Answers

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

    Minus is chosen as producing the minimum visual noise. Also it's a nod to the `-` options prefix character.

- Why such a stupid name?

    CLI libs should have `cli` in their name. It's the law. And `clit` is already taken on the PyPI.
