# simple terminal escape codes.
# color names are tailwind-inspired

import os
from typing import Literal

Token = Literal[
    #
    "text-black",
    "text-red",
    "text-green",
    "text-yellow",
    "text-blue",
    "text-magenta",
    "text-cyan",
    "text-white",
    #
    "bg-black",
    "bg-red",
    "bg-green",
    "bg-yellow",
    "bg-blue",
    "bg-magenta",
    "bg-cyan",
    "bg-white",
    #
    "text-bold",
    #
    "text-black-bright",
    "text-red-bright",
    "text-green-bright",
    "text-yellow-bright",
    "text-blue-bright",
    "text-magenta-bright",
    "text-cyan-bright",
    "text-white-bright",
    #
    "bg-black-bright",
    "bg-red-bright",
    "bg-green-bright",
    "bg-yellow-bright",
    "bg-blue-bright",
    "bg-magenta-bright",
    "bg-cyan-bright",
    "bg-white-bright",
]


CODES: dict[Token, int] = {
    "text-black": 30,
    "text-red": 31,
    "text-green": 32,
    "text-yellow": 33,
    "text-blue": 34,
    "text-magenta": 35,
    "text-cyan": 36,
    "text-white": 37,
    #
    "text-bold": 1,
    #
    "bg-black": 40,
    "bg-red": 41,
    "bg-green": 42,
    "bg-yellow": 43,
    "bg-blue": 44,
    "bg-magenta": 45,
    "bg-cyan": 46,
    "bg-white": 47,
    #
    "text-black-bright": 90,
    "text-red-bright": 91,
    "text-green-bright": 92,
    "text-yellow-bright": 93,
    "text-blue-bright": 94,
    "text-magenta-bright": 95,
    "text-cyan-bright": 96,
    "text-white-bright": 97,
    #
    "bg-black-bright": 100,
    "bg-red-bright": 101,
    "bg-green-bright": 102,
    "bg-yellow-bright": 103,
    "bg-blue-bright": 104,
    "bg-magenta-bright": 105,
    "bg-cyan-bright": 106,
    "bg-white-bright": 107,
}


def enable(*, stdin: bool = True, stderr: bool = True) -> None:
    """Enable color output with escape sequences on Windows"""
    if os.name != "nt":
        return

    from ctypes import byref, windll, wintypes

    defs: list[int] = []
    if stdin:
        defs.append(-11)
    if stderr:
        defs.append(-12)

    # set ENABLE_PROCESSED_OUTPUT | ENABLE_VIRTUAL_TERMINAL_PROCESSING
    for d in defs:
        hnd = windll.kernel32.GetStdHandle(d)
        mode = wintypes.DWORD()
        windll.kernel32.GetConsoleMode(hnd, byref(mode))
        windll.kernel32.SetConsoleMode(hnd, mode.value | 0x0004 | 0x0001)


def style(text: str, *tokens: Token | int) -> str:
    if not tokens:
        return text
    code = ";".join(str(CODES[tok] if isinstance(tok, str) else tok) for tok in tokens)
    return f"\x1b[{code}m{text}\x1b[0m"
