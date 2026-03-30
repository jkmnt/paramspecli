from typing import Any, overload

from .cli import MISSING, ConstLoader, Missing
from .fake import Const


@overload
def const[D](
    default: D,
    *,
    load: None = None,
) -> Const[D, D]: ...


@overload
def const[TD](
    default: Missing = ...,
    *,
    load: ConstLoader[TD],
) -> Const[TD, Missing]: ...


@overload
def const[TD, D](
    default: D,
    *,
    load: ConstLoader[TD],
) -> Const[TD, D]: ...


def const(default: Any = MISSING, *, load: ConstLoader[Any] | None = None) -> Const[Any, Any]:
    """Sets default value of parameter. May be dynamic via `load`"""

    return Const(default, load=load)
