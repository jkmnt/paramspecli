import dataclasses
from typing import Any, Final, overload

from .cli import Arg, ConstOpt, CtxOpt, Missing, MixedOpts, Opt

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


# Type model: T is resulting type if option is present, D if absent (default, nargs='?')
class Argument[T, D](Arg, LieMixin[T | D]):
    """Parameter-argument"""

    __slots__ = ()


# Type model: T is resulting type if option is present, D if absent (default)
class Option[T, D](Opt, LieMixin[T | D]):
    """Parameter-option"""

    __slots__ = ()

    # T's are joined. Our default wins
    def mixed_with[OT](self, other: "Option[OT, Any] | MixedOptions[OT, Any]") -> "MixedOptions[T | OT, D]":
        if isinstance(other, (Option, MixedOptions)):
            return MixedOptions._from_items(self, other)
        raise TypeError("Unsupported mix type")

    __or__ = mixed_with


# Type model: list[T] is resulting type if option is present, D if absent (default)
# T is the list element type to get correct 'list[T1 | T2 | T3]' in mix
class RepeatedOption[T, D](Opt, LieMixin[list[T] | D]):
    """Parameter-option which could be repeated multiple times on command line"""

    __slots__ = ()

    # T's are joined. Our default wins
    def mixed_with[OT](
        self, other: "RepeatedOption[OT, Any] | MixedRepeatedOptions[OT, Any]"
    ) -> "MixedRepeatedOptions[T | OT, D]":
        if isinstance(other, (RepeatedOption, MixedRepeatedOptions)):
            return MixedRepeatedOptions._from_items(self, other)
        raise TypeError("Unsupported mix type")

    __add__ = mixed_with


# Type model: just the default
class Const[TD, D](ConstOpt, LieMixin[TD | D]):
    """Parameter-loaded value. Allows to load parameter default
    without inspecting the command line"""

    __slots__ = ()

    # If our default is Missing, our TD or other default may win
    @overload
    def mixed_with[OT, OD](
        self: "Const[TD, Missing]", other: "Option[OT, OD] | MixedOptions[OT, OD]"
    ) -> "MixedOptions[OT, TD | OD]": ...

    @overload
    def mixed_with[OT, OD](
        self: "Const[TD, Missing]", other: "RepeatedOption[OT, OD] | MixedRepeatedOptions[OT, OD]"
    ) -> "MixedRepeatedOptions[OT, TD | OD]": ...

    # Our default wins
    @overload
    def mixed_with[OT](self, other: "Option[OT, Any] | MixedOptions[OT, Any]") -> "MixedOptions[OT, TD | D]": ...

    @overload
    def mixed_with[OT](
        self, other: "RepeatedOption[OT, Any] | MixedRepeatedOptions[OT, Any]"
    ) -> "MixedRepeatedOptions[OT, TD | D]": ...

    def mixed_with(
        self,
        other: "Option[Any, Any] | MixedOptions[Any, Any] | RepeatedOption[Any, Any] | MixedRepeatedOptions[Any, Any]",
    ) -> "MixedOptions[Any, Any] | MixedRepeatedOptions[Any, Any]":
        if isinstance(other, (Option, MixedOptions)):
            return MixedOptions._from_items(self, other)
        if isinstance(other, (RepeatedOption, MixedRepeatedOptions)):
            return MixedRepeatedOptions._from_items(self, other)
        raise TypeError("Unsupported mix type")

    __or__ = mixed_with


# Type model: T is resulting type if some or all options are present, D if all absent (default)
# T is a union of all possible options T's
class MixedOptions[T, D](MixedOpts, LieMixin[T | D]):
    """Parameter-mix of several options targeting the same parameter"""

    __slots__ = ()

    # T's are joined. Our default wins
    def mixed_with[OT](self, other: "Option[OT, Any] | MixedOptions[OT, Any]") -> "MixedOptions[T | OT, D]":
        if isinstance(other, (Option, MixedOptions)):
            return MixedOptions._from_items(self, other)
        raise TypeError("Unsupported mix type")

    __or__ = mixed_with


# Type model: list[T] is resulting type if some or all options are present, D if all absent (default)
# T is a union of all possible option's elements T's
class MixedRepeatedOptions[T, D](MixedOpts, LieMixin[list[T] | D]):
    """Parameter-mix of several repeated options targeting the same parameter"""

    __slots__ = ()

    # T's are joined. Our default wins
    def mixed_with[OT](
        self, other: "RepeatedOption[OT, Any] | MixedRepeatedOptions[OT, Any]"
    ) -> "MixedRepeatedOptions[T | OT, D]":
        if isinstance(other, (RepeatedOption, MixedRepeatedOptions)):
            return MixedRepeatedOptions._from_items(self, other)
        raise TypeError("Unsupported mix type")

    __add__ = mixed_with


# Type model: T is context type, set as default
class Context[TD](CtxOpt, LieMixin[TD]):
    """Parameter-context. Marks parameter as accepting the shared context object"""

    __slots__ = ()


class Lier:
    """Cast argument/option to its type. In other words, lie to the type checker"""

    @overload
    def __call__[T, D](self, obj: Option[T, D] | MixedOptions[T, D] | Argument[T, D]) -> T | D: ...

    @overload
    def __call__[T, D](self, obj: RepeatedOption[T, D]) -> list[T] | D: ...

    @overload
    def __call__[T, D](self, obj: MixedRepeatedOptions[T, D]) -> list[T] | D: ...

    @overload
    def __call__[TD, D](self, obj: Const[TD, D]) -> TD | D: ...

    def __call__(self, obj: Any) -> Any:
        return obj

    __getitem__ = __call__
    __matmul__ = __call__
    __rmatmul__ = __call__


@overload
def required[T](option: Option[T, Any]) -> Option[T, T]: ...


@overload
def required[T](option: RepeatedOption[T, Any]) -> RepeatedOption[T, list[T]]: ...


def required(option: Opt) -> Opt:
    """Return a copy of option with the `required` flag set"""
    return dataclasses.replace(option, required=True)


def deprecated[T: Opt](option: T) -> T:
    """Return a copy of option with the `deprecated` flag set"""
    return dataclasses.replace(option, deprecated=True)


t: Final = Lier()
