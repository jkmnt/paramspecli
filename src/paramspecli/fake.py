import dataclasses
from typing import Any, Final, overload

from .cli import Arg, Cnst, Ctx, MixedOpts, Opt

# These specialized arguments/options classes are for the typechecher benefit
# These are really shouldn't be referenced anywhere else


class LieMixin[T]:
    # NOTE: arguments, options, etc are using this mixin.
    # they all define __slots__ for extra savings, so we should define an empty __slots__ too
    __slots__ = ()

    @property
    def t(self) -> T:
        return self  # type: ignore[return-value]  # ty: ignore[invalid-return-type]

    def __neg__(self) -> T:
        return self  # type: ignore[return-value]  # ty: ignore[invalid-return-type]


class Argument[T, D](Arg, LieMixin[T | D]):
    """Parameter-argument"""

    __slots__ = ()


class Option[T, D](Opt, LieMixin[T | D]):
    """Parameter-option"""

    __slots__ = ()

    def mixed_with[O](self, other: "Option[O, Any]") -> "MixedOptions[T | O, D]":
        return MixedOptions(self, other)

    __or__ = mixed_with


class RepeatedOption[T](Opt, LieMixin[list[T]]):
    """Parameter-option which could be repeated multiple times on command line"""

    __slots__ = ()

    def mixed_with[O](self, other: "RepeatedOption[O]") -> "MixedRepeatedOptions[T | O]":
        return MixedRepeatedOptions(self, other)

    __add__ = mixed_with


class MixedOptions[T, D](MixedOpts, LieMixin[T | D]):
    """Parameter-mix of several options targeting the same parameter"""

    __slots__ = ()

    def mixed_with[O](self, other: "Option[O, Any]") -> "MixedOptions[T | O, D]":
        return MixedOptions(*self.options, other)

    __or__ = mixed_with


class MixedRepeatedOptions[T](MixedOpts, LieMixin[list[T]]):
    """Parameter-mix of several repeated options targeting the same parameter"""

    __slots__ = ()

    def mixed_with[O](self, other: RepeatedOption[O]) -> "MixedRepeatedOptions[T | O]":
        # ty wants this specialization for some reason
        return MixedRepeatedOptions[T | O](*self.options, other)

    __add__ = mixed_with


class Const[T](Cnst, LieMixin[T]):
    """Parameter-constant value. Allows to remove parameter from the command line"""

    __slots__ = ()

    def __init__(self, value: T):
        super().__init__(value)


class Context[T](Ctx, LieMixin[T]):
    """Parameter-context. Marks parameter as accepting the shared context object"""

    __slots__ = ()


class Lier:
    """Cast argument/option to its type. In other words, lie to the type checker"""

    @overload
    def __call__[T, D](self, obj: Option[T, D] | MixedOptions[T, D] | Argument[T, D]) -> T | D: ...

    @overload
    def __call__[T](self, obj: RepeatedOption[T] | MixedRepeatedOptions[T]) -> list[T]: ...

    @overload
    def __call__[T](self, obj: Const[T]) -> T: ...

    def __call__(self, obj: Any) -> Any:
        return obj

    __getitem__ = __call__
    __matmul__ = __call__
    __rmatmul__ = __call__


@overload
def required[T](option: Option[T, Any]) -> Option[T, T]: ...


@overload
def required[T](option: RepeatedOption[T]) -> RepeatedOption[T]: ...


def required(option: Opt) -> Opt:
    """Return a copy of option with the `required` flag set"""
    return dataclasses.replace(option, required=True)


def deprecated[T: Opt](option: T) -> T:
    """Return a copy of option with the `deprecated` flag set"""
    return dataclasses.replace(option, deprecated=True)


t: Final = Lier()
