import re
from typing import Iterable

# NOTE: dots are not escaped
_MD_ESCAPE = re.compile("[" + re.escape(r"\`*_{}[]<>()#+-!") + "]")


class Md(str):
    __slots__ = ()

    def plain(self) -> str:
        return self.replace("\\", "")


class Renderer:
    """Default markdown renderer"""

    def p(self, text: str) -> str:
        return text + "\n\n"

    def h(self, level: int, text: str) -> str:
        return f"{'#' * level} {text}\n\n"

    def br(self) -> str:
        return "<br />\n"

    def b(self, text: str) -> str:
        return f"**{text}**"

    def i(self, text: str) -> str:
        return f"*{text}*"

    def blockquote(self, text: str) -> str:
        return "\n".join([f"> {line}" for line in text.splitlines()]) + "\n\n"

    def ul(self, lis: Iterable[str]) -> str:
        elts: list[str] = []
        for li in lis:
            lines = li.splitlines()
            if lines:
                elts.append(f"- {lines[0]}")
                elts.extend(f"    {line}" for line in lines[1:])
        return "\n".join(elts) + "\n\n"

    def dl(self, dtdds: Iterable[tuple[str, str]]) -> str:
        return self.ul(self.p(dt) + self.p(dd) for dt, dd in dtdds)

    def code(self, text: str) -> str:
        return f"`{text}`"

    def codeblock(self, text: str, lang: str | None = None) -> str:
        return f"```{lang or ''}\n{text}\n```\n\n"

    def strike(self, text: str) -> str:
        return f"~~~{text}~~~"

    def hr(self) -> str:
        return "---\n\n"

    def link(self, url: str, *, text: str | None) -> str:
        if text:
            return f"[{text}]({url})"
        return f"({url})"

    def e(self, text: str) -> str:
        return _MD_ESCAPE.sub(r"\\\g<0>", text)

    def body(self, text: str) -> str:
        return text

    # It's easier to post-process markdown than account for extra newlines while generating
    def postprocess(self, text: str) -> str:
        out = "\n".join(line.rstrip() for line in text.splitlines())
        out = re.sub(r"\n{3,}", "\n\n", out)
        return out
