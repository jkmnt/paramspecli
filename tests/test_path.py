from argparse import ArgumentTypeError
from enum import StrEnum
from pathlib import Path
from typing import Literal

import pytest

from paramspecli import PathConv


# well-known paths are relative to the project root
class Fs(StrEnum):
    F = "README.md"
    D = "tests"
    NA = "__not_here__"


# ok, we have a permutations here:
# typ: None | file | dir
# exists: None | True | False
# resolve: True | False
#
# split into the two parametric loops to keep it simple
@pytest.mark.parametrize(
    ("type", "exists", "arg", "expected"),
    [
        ## type: None
        (None, None, Fs.NA, Fs.NA),
        (None, True, Fs.D, Fs.D),
        (None, True, Fs.F, Fs.F),
        (None, True, Fs.NA, "does not exists"),
        (None, False, Fs.NA, Fs.NA),
        (None, False, Fs.D, "already exists"),
        ## type: file
        ("file", None, Fs.NA, Fs.NA),
        ("file", None, Fs.D, "not a file"),
        ("file", True, Fs.F, Fs.F),
        ("file", True, Fs.D, "not a file"),
        ("file", True, Fs.NA, "does not exists"),
        ("file", False, Fs.NA, Fs.NA),
        ("file", False, Fs.F, "already exists"),
        ("file", False, Fs.D, "already exists"),
        ## type: dir
        ("dir", None, Fs.NA, Fs.NA),
        ("dir", None, Fs.F, "not a directory"),
        ("dir", True, Fs.D, Fs.D),
        ("dir", True, Fs.F, "not a directory"),
        ("dir", True, Fs.NA, "does not exists"),
        ("dir", False, Fs.NA, Fs.NA),
        ("dir", False, Fs.F, "already exists"),
        ("dir", False, Fs.D, "already exists"),
    ],
)
@pytest.mark.parametrize("resolve", [True, False])
def test_path(
    *,
    type: Literal[None, "file", "dir"],
    arg: str,
    exists: bool | None,
    expected: Fs | str,
    resolve: bool,
) -> None:
    if type == "file":
        conv = PathConv.file(exists=exists, resolve=resolve)
    elif type == "dir":
        conv = PathConv.dir(exists=exists, resolve=resolve)
    else:
        conv = PathConv(type=None, exists=exists, resolve=resolve)

    if isinstance(expected, Fs):
        path = Path(expected)
        if resolve:
            path = path.resolve()
        assert conv(arg) == path
    else:
        with pytest.raises(ArgumentTypeError, match=expected):
            conv(arg)


def test_bad_path() -> None:
    conv = PathConv(type="file")
    with pytest.raises(ValueError, match="nul"):
        conv("\0")
