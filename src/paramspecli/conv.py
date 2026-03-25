from argparse import ArgumentTypeError
from pathlib import Path
from typing import Final, Literal


class PathConv:
    __name__ = "PATH"

    __slots__ = ("exists", "kind", "resolve")

    def __init__(self, kind: Literal["file", "dir", None] = None, *, exists: bool | None = None, resolve: bool = True):
        self.exists: Final = exists
        self.kind: Final = kind
        self.resolve: Final = resolve

    # scenarios:
    # - existing path: check exists
    # - existing file: check exists and is_file
    # - existing dir: check exists and is_dir
    # - non-existing path/file/dir: check not exists
    # - maybe existing path: nothing
    # - maybe existing file: if exists, check is_file
    # - maybe existing dir: if exists, check is_dir
    def __call__(self, arg: str) -> Path:
        path = Path(arg)
        if self.resolve:
            path = path.resolve()

        check_kind = False

        if self.exists is True:
            if not path.exists():
                raise ArgumentTypeError(f"{path} does not exists")
            check_kind = True
        elif self.exists is False:
            if path.exists():
                raise ArgumentTypeError(f"{path} already exists")
        else:
            if self.kind and path.exists():
                check_kind = True

        if check_kind:
            if self.kind == "file":
                if not path.is_file():
                    raise ArgumentTypeError(f"{path} is not a file")
            elif self.kind == "dir":
                if not path.is_dir():
                    raise ArgumentTypeError(f"{path} is not a directory")

        return path

    @classmethod
    def file(cls, *, exists: bool | None = None, resolve: bool = True) -> "PathConv":
        return cls("file", exists=exists, resolve=resolve)

    @classmethod
    def dir(cls, *, exists: bool | None = None, resolve: bool = True) -> "PathConv":
        return cls("dir", exists=exists, resolve=resolve)
