import dataclasses
from argparse import BooleanOptionalAction
from typing import Any, Final, Iterable, Mapping, NamedTuple, Protocol, Sequence

from paramspecli import md

from .cli import Arg, Command, Group, Opt, Section, name_and_aliases, nice_str


class Renderer(Protocol):
    """
    Doc render backend interface (protocol).
    """

    def p(self, text: str) -> str: ...
    def h(self, level: int, text: str) -> str: ...
    def br(self) -> str: ...
    def b(self, text: str) -> str: ...
    def i(self, text: str) -> str: ...
    def blockquote(self, text: str) -> str: ...
    def ul(self, lis: Iterable[str]) -> str: ...
    def dl(self, dtdds: Iterable[tuple[str, str]]) -> str: ...
    def code(self, text: str) -> str: ...
    def codeblock(self, text: str, lang: str | None = None) -> str: ...
    def strike(self, text: str) -> str: ...
    def hr(self) -> str: ...
    def link(self, url: str, *, text: str | None) -> str: ...
    def e(self, text: str) -> str: ...
    def body(self, text: str) -> str: ...
    def postprocess(self, text: str) -> str: ...


class BoundGroup(NamedTuple):
    name: str
    aliases: tuple[str, ...]
    obj: Group


class BoundCommand(NamedTuple):
    name: str
    aliases: tuple[str, ...]
    obj: Command[...]


# A little helper joining all truthy strings with the sep
def _join(*args: str | None | bool | Iterable[str | None | bool], sep: str) -> str:
    out: list[str] = []
    for arg in args:
        if isinstance(arg, str) and arg:
            out.append(arg)
        elif arg is not None and arg is not True and arg is not False:
            out.extend(sub for sub in arg if isinstance(sub, str) and arg)
    return sep.join(out)


@dataclasses.dataclass(kw_only=True)
class Settings:
    """Documentation generator config"""

    commands_title: str = "Commands"
    arguments_title: str | None = "Arguments"
    arguments_headline: str | None = None
    options_title: str = "Options"
    choices_title: str = "Possible values"
    usage_title: str = "Usage"
    aliases_title: str = "Aliases"
    options_headline: str | None = None
    choice_metavar: str = "CHOICE"


class Doc:
    """Documentation generator"""

    def __init__(
        self,
        *,
        renderer: Renderer | None = None,
        settings: Settings | None = None,
    ):
        self.r: Final[Renderer] = renderer or md.Renderer()
        self.config: Final = settings or Settings()

    def r_choices(self, choices: Iterable[Any]) -> str:
        r = self.r
        out = ""

        out += r.p(self.config.choices_title + ":")
        if isinstance(choices, Mapping):
            out += r.ul(r.code(str(c)) + ": " + str(desc) for c, desc in choices.items())
        else:
            out += r.ul(r.code(str(c)) for c in choices)
        return out

    def r_argument_title(self, arg: Arg) -> str:
        r = self.r

        return r.code(arg.metavar)

    def r_argument_info(self, arg: Arg) -> str:
        r = self.r
        out = ""

        if isinstance(arg.help, str):
            out += r.p(arg.help)
        if arg.choices:
            out += self.r_choices(arg.choices)
        return out

    def r_option_title(self, option: Opt) -> str:
        r = self.r
        out = ""

        names = option.names

        if option.action == BooleanOptionalAction:
            basename = [name for name in names if name.startswith("--")][0]
            out += _join(
                r.code(basename) + "/" + r.code(f"--no-{basename[2:]}"),
                [r.code(name) for name in names if name != basename],
                sep=", ",
            )
        else:
            out += _join([r.code(name) for name in names], sep=", ")

        metavar = self.r_metavar(option)

        if metavar:
            out += " " + r.i(r.e(metavar))
        return out

    def r_option_default(self, option: Opt) -> str:
        r = self.r

        default: str | None = None

        if option.hard_show_default is not None:
            if isinstance(option.hard_show_default, str):
                default = option.hard_show_default
            elif option.hard_show_default is True:
                default = nice_str(option.default)
        else:
            if isinstance(option.soft_show_default, str):
                default = option.soft_show_default
            elif option.soft_show_default is True:
                default = nice_str(option.default)

        if default is None:
            return ""

        # this wrapping in code avoid the need for most escapes
        return f"(default: {r.code(default)})"

    def r_option_info(self, option: Opt) -> str:
        r = self.r
        out = ""

        out += r.p(
            _join(
                option.help if isinstance(option.help, str) else None,
                self.r_option_default(option),
                sep=" ",
            )
        )

        if option.choices:
            out += self.r_choices(option.choices)

        return out

    def r_metavar(self, item: Opt | Arg) -> str:
        metavar = item.metavar
        if isinstance(metavar, tuple):
            return _join(metavar, sep=" ")

        if metavar is None:
            if item.choices:
                metavar = self.config.choice_metavar
            else:
                return ""

        nargs = item.nargs

        if isinstance(nargs, int):
            return _join([metavar] * nargs, sep=" ")
        if nargs == "*":
            return f"[{metavar} ...]"
        if nargs == "+":
            return f"{metavar} [{metavar} ...]"
        if nargs == "?":
            return f"[{metavar}]"
        return metavar

    def r_arguments(self, arguments: Sequence[Arg]) -> str:
        r = self.r
        out = ""

        if not arguments:
            return ""

        title = self.config.arguments_title
        headline = self.config.arguments_headline

        if title:
            out += r.p(title + ":")
        if headline:
            out += r.p(headline)
        out += r.dl((self.r_argument_title(arg), self.r_argument_info(arg)) for arg in arguments)
        return out

    def r_options_section(self, section: Section, options: Sequence[Opt]) -> str:
        r = self.r
        out = ""

        if not options:
            return ""

        if section.title:
            out += r.p(section.title + ":")
        if section.headline:
            out += r.p(str(section.headline))
        out += r.dl((self.r_option_title(opt), self.r_option_info(opt)) for opt in options)
        return out

    def get_options(self, me: BoundGroup | BoundCommand) -> list[Opt]:
        return [*me.obj.actions, *me.obj.get_real_options()]

    def get_arguments(self, me: BoundGroup | BoundCommand) -> list[Arg]:
        return me.obj.get_real_arguments()

    def _opts_by_sections(self, me: BoundGroup | BoundCommand) -> dict[Section, list[Opt]]:
        default_section = Section(self.config.options_title, headline=self.config.options_headline)

        out: dict[Section, list[Opt]] = {}

        for option in self.get_options(me):
            sect = next((sect for sect in me.obj.sections if option in sect.options), default_section)
            out.setdefault(sect, []).append(option)

        return out

    def _group_usage_partial(self, me: BoundGroup) -> str:
        return _join(
            me.name,
            [self.r_metavar(arg) for arg in self.get_arguments(me)],
            sep=" ",
        )

    def r_aliases(self, me: BoundGroup | BoundCommand) -> str:
        r = self.r
        out = ""

        if me.aliases:
            out += r.p(self.config.aliases_title + ":")
            out += r.ul(r.b(alias) for alias in me.aliases)
        return out

    def r_command_title(self, me: BoundCommand, parents: Sequence[BoundGroup]) -> str:
        r = self.r
        out = ""

        title = _join([p.name for p in parents], me.name, sep=" ")
        out += r.h(len(parents) + 1, text=title)
        return out

    def r_command_info(self, me: BoundCommand) -> str:
        r = self.r
        out = ""

        info = me.obj.info or me.obj.help
        if info:
            out += r.p(str(info))
        return out

    def r_command_usage(
        self, me: BoundCommand, parents: Sequence[BoundGroup], options_sections: Iterable[Section]
    ) -> str:
        r = self.r
        out = ""

        out += r.p(self.config.usage_title + ":")
        out += r.codeblock(
            _join(
                [self._group_usage_partial(p) for p in parents],
                me.name,
                [f"[{section.title.lower()}]" for section in options_sections],
                [self.r_metavar(arg) for arg in self.get_arguments(me)],
                sep=" ",
            )
        )
        return out

    def r_command(self, me: BoundCommand, parents: Sequence[BoundGroup]) -> str:
        out = ""
        out += self.r_command_title(me, parents)
        out += self.r_command_info(me)
        out += self.r_aliases(me)

        opts_sections = self._opts_by_sections(me)

        out += self.r_command_usage(me, parents, opts_sections)
        out += self.r_arguments(self.get_arguments(me))

        for section, opts in opts_sections.items():
            out += self.r_options_section(section, opts)

        return out

    def r_group_legend(self, me: BoundGroup, parents: Sequence[BoundGroup]) -> str:
        r = self.r
        out = ""

        if not me.obj.nodes:
            return ""

        out += r.p((me.obj.title or self.config.commands_title) + ":")

        if me.obj.headline:
            out += r.p(str(me.obj.headline))

        dtdds: list[tuple[str, str]] = []
        for names, node in me.obj.nodes.items():
            name, _aliases = name_and_aliases(names)
            anchor = _join([p.name for p in parents], me.name, name, sep="-").lower()
            text = _join(name, "..." if isinstance(node, Group) else None, sep=" ")
            dtdds.append((r.link("#" + anchor, text=text), str(node.help or "")))

        out += r.dl(dtdds)
        return out

    def r_group_info(self, me: BoundGroup) -> str:
        r = self.r
        out = ""

        info = me.obj.info or me.obj.help
        if info:
            out += r.p(str(info))
        return out

    def r_group_title(self, me: BoundGroup, parents: Sequence[BoundGroup]) -> str:
        r = self.r
        out = ""

        title = _join([p.name for p in parents], me.name, "..." if parents else None, sep=" ")
        out += r.h(len(parents) + 1, text=title)
        return out

    def r_group(self, me: BoundGroup, parents: Sequence[BoundGroup]) -> str:
        out = ""

        out = self.r_group_title(me, parents)
        out += self.r_group_info(me)
        out += self.r_aliases(me)
        out += self.r_arguments(self.get_arguments(me))

        opts_sections = self._opts_by_sections(me)

        for section, opts in opts_sections.items():
            out += self.r_options_section(section, opts)

        out += self.r_group_legend(me, parents)

        for item_name, node in me.obj.nodes.items():
            if isinstance(node, Group):
                out += self.r_group(BoundGroup(*name_and_aliases(item_name), node), [*parents, me])
            else:
                out += self.r_command(BoundCommand(*name_and_aliases(item_name), node), [*parents, me])

        return out

    def generate(self, node: Group | Command[...], *, prog: str) -> str:
        r = self.r

        if isinstance(node, Group):
            content = self.r_group(BoundGroup(prog, (), node), [])
        else:
            content = self.r_command(BoundCommand(prog, (), node), [])

        return r.postprocess(r.body(content))
