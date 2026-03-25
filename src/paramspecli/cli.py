import argparse
import dataclasses
import sys
from types import EllipsisType
from typing import (
    Any,
    Callable,
    Concatenate,
    Final,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    NamedTuple,
    Protocol,
    Self,
    Sequence,
    TypeGuard,
    overload,
)

from . import util
from .apstub import (
    ArgumentGroupLike,
    ArgumentParserLike,
    SupportsAddArgument,
    SupportsAddArgumentGroup,
    SupportsAddOneofGroup,
    SupportsAddParser,
    SupportsSetDefaults,
    TypeConverter,
)
from .conv import PathConv

# TODO:
# if section has a headline, it's not auto-purged from the help.
# Ok for user sections, bad for the default options/arguments sections

type Missing = EllipsisType
MISSING: Final = ...


class HandlerSpec(NamedTuple):
    func: Callable[..., None] | None
    args: list[str]  # [arg_key]
    opts: dict[str, str]  # {opt_name: opt_key}


class Markup(Protocol):
    def plain(self) -> str: ...

    def __str__(self) -> str: ...


class DefaultFunc[**P](Protocol):
    def __call__(self, parser: ArgumentParserLike, /, *args: P.args, **kwargs: P.kwargs) -> None: ...


def _make_spec(
    level: int,
    func: Callable[..., None] | None,
    args: Sequence["Arg | Cnst | Ctx"],
    options: Mapping[str, "Opt | MixedOpts | Cnst | Ctx"],
) -> HandlerSpec:
    return HandlerSpec(
        func=func,
        args=[f"{level}[{i}]" for i in range(len(args))],
        opts={param: f"{level}.{param}" for param in options},
    )


def _repr_class(obj: object, fields: Mapping[str, Any], *, skip_none: bool = True, skip_empty: bool = True) -> str:
    items: list[str] = []
    for k, v in fields.items():
        if skip_none and v is None:
            continue
        if skip_empty and isinstance(v, (list, dict, set)) and not len(v):
            continue
        items.append(f"{k}={v!r}")

    return f"{obj.__class__.__name__}({', '.join(items)})"


def name_and_aliases(arg: str | tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    if isinstance(arg, str):
        return arg, ()
    return arg[0], arg[1:]


def is_markup(obj: object) -> TypeGuard[Markup]:
    return hasattr(obj, "plain")


@overload
def _as_plain(arg: str | Markup) -> str: ...


@overload
def _as_plain(arg: None) -> None: ...


def _as_plain(arg: str | Markup | None) -> str | None:
    if arg is None:
        return arg
    if is_markup(arg):
        return arg.plain()
    return str(arg)


def _may_raise_custom_exceptions(conv: TypeConverter[Any]) -> bool:
    if conv is int:
        return False
    if conv is float:
        return False
    if conv is bool:
        return False
    if isinstance(conv, PathConv):
        return False
    return True


def print_group_help(parser: ArgumentParserLike, /, *args: Any, **kwargs: Any) -> None:
    parser.print_help()
    parser.exit()


# print some values in a nicer way. currently it's a lists w/o quotes
def nice_str(val: Any) -> str:
    if isinstance(val, list):
        return f"[{ ", ".join([str(item) for item in val])}]"
    return str(val)


def _with_argparser_arg[**P](
    f: Callable[Concatenate[ArgumentParserLike, P], None], argparser: ArgumentParserLike
) -> Callable[P, None]:
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        f(argparser, *args, **kwargs)

    # ty as of 0.0.18 suggests some nonsense here
    return _wrapper  # ty: ignore[invalid-return-type]


# took the idea from mypy. nice and simple.
# if there are newlines in text, emit as is (with indent)
# otherwise use default wrapping HelpFormatter.
class HelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(prog=prog, max_help_position=28)

    def _fill_text(self, text: str, width: int, indent: str) -> str:
        if "\n" in text:
            return "".join(indent + line for line in text.splitlines(keepends=True))
        return super()._fill_text(text, width, indent)

    def _split_lines(self, text: str, width: int) -> list[str]:
        if "\n" in text:
            return text.splitlines()
        return super()._split_lines(text, width)

    # interpolate lists manually to avoid extra quotes
    def _get_help_string(self, action: argparse.Action) -> str | None:
        help = action.help

        if help is not None and "%(default)s" in help:
            if isinstance(action.default, list):
                s = nice_str(action.default)
                help = help.replace("%(default)s", s)

        return help


@dataclasses.dataclass
class Config:
    """Settings to fine-tune the generated argparser"""

    show_default: bool = True
    """Show default value in help. Set to `False` to globally opt-out. Options may set own `show default` to selectively opt-in"""
    propagate_epilog: bool = False
    """Propagate root epilog for all groups and commands"""
    commands_title: str = "commands"
    """Section for the list of commands in group"""
    arguments_title: str = "arguments"
    """Title for the list of arguments"""
    options_title: str = "options"
    """Title for the list of options"""
    arguments_headline: str | Markup | None = None
    """Headline for the list of arguments"""
    options_headline: str | Markup | None = None
    """Headline for the list of options"""
    catch_typeconv_exceptions: bool = False
    """Catch all type converter exceptions and print as CLI errors"""
    allow_abbrev: bool = False
    """Guess incomplete arguments"""
    parser_class: type[argparse.ArgumentParser] = argparse.ArgumentParser
    """Argparge parser class to use"""
    formatter_class: type[argparse.HelpFormatter] = HelpFormatter
    """Silently ignore unknown args and place them into the Route.unknown_args"""
    ignore_unknown_args: bool = False
    """Argparse help formatter class to use"""
    root_parser_extra_kwargs: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    """Dict of extra kwargs for the root (CLI) argparse.ArgumentParser"""
    sub_parser_extra_kwargs: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    """Dict of extra kwargs for sub (groups) argparse.ArgumentParsers"""


@dataclasses.dataclass(repr=False, slots=True)
class Arg:
    """Represents the argument"""

    metavar: str
    _: dataclasses.KW_ONLY
    conv: TypeConverter[Any] | None = None
    help: str | Markup | bool | None = None
    choices: Iterable[Any] | None = None
    nargs: int | Literal["*", "+", "?"] | None = None
    default: Any = None
    extra: Mapping[str, Any] | None = None

    def __repr__(self) -> str:
        return _repr_class(self, {k: getattr(self, k) for k in self.__dataclass_fields__}, skip_empty=False)

    # (weak) hash is based on a metavar
    def __hash__(self) -> int:
        return hash(self.metavar)

    def _build(self, owner: SupportsAddArgument, config: Config, *, dest: str, **_rest: Any) -> None:
        conv = self.conv
        if conv and config.catch_typeconv_exceptions and _may_raise_custom_exceptions(conv):
            conv = util.catch_all(conv)

        help = self.help

        if help is False:
            help = argparse.SUPPRESS
        elif help is True:
            help = ""

        # most kwargs shouldn't be set at all if None
        kwargs: dict[str, Any] = {
            "choices": self.choices,
            "nargs": self.nargs,
            "metavar": self.metavar,
            # NOTE: if type is not specified, argparse's MetavarTypeHelpFormatter may fail!
            "type": conv,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        if self.extra:
            kwargs |= self.extra

        owner.add_argument(dest=dest, help=_as_plain(help), default=self.default, **kwargs)


# Too many fields to manage: dataclass to the rescue
@dataclasses.dataclass(repr=False, slots=True)
class Opt:
    """Abstract option"""

    names: tuple[str, ...]
    _: dataclasses.KW_ONLY
    conv: TypeConverter[Any] | None = None
    help: str | Markup | bool | None = None
    hard_show_default: bool | str | None = None
    soft_show_default: bool | str = False
    required: bool = False
    choices: Iterable[Any] | None = None
    metavar: str | tuple[str, ...] | None = None
    action: str | type[argparse.Action] | None = None
    nargs: int | Literal["*", "+", "?"] | None = None
    default: Any = None
    const: Any = None
    deprecated: bool = False
    extra: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.names:
            raise ValueError("at least one name is required")

        for name in self.names:
            if not name.startswith("-"):
                raise ValueError(f"Option name {name!r} should start with '-'")

    def __repr__(self) -> str:
        return _repr_class(self, {k: getattr(self, k) for k in self.__dataclass_fields__}, skip_empty=False)

    # (weak) hash is based on names
    def __hash__(self) -> int:
        return hash(self.names)

    def _build(self, owner: SupportsAddArgument, config: Config, *, dest: str | Literal[False], **_rest: Any) -> None:
        help = self.help

        if help is False:
            help = argparse.SUPPRESS
        elif help is True:
            help = ""
        elif help is None:
            pass
        else:
            help = _as_plain(help)

            # str
            if self.hard_show_default is not None:
                show_default = self.hard_show_default
            else:
                show_default = self.soft_show_default if config.show_default is True else False

            if show_default is True:
                help += " (default: %(default)s)"
            elif show_default is False:
                pass
            else:
                help += f" (default: {show_default})"

        conv = self.conv
        if conv and config.catch_typeconv_exceptions and _may_raise_custom_exceptions(conv):
            conv = util.catch_all(conv)

        # most kwargs shouldn't be set at all if None
        kwargs: dict[str, Any] = {
            "action": self.action,
            "choices": self.choices,
            "nargs": self.nargs,
            "const": self.const,
            "metavar": self.metavar,
            "type": conv,
            "required": self.required or None,
            "deprecated": self.deprecated if sys.version_info >= (3, 13) else None,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if self.extra:
            kwargs |= self.extra

        owner.add_argument(*self.names, dest=dest or argparse.SUPPRESS, default=self.default, help=help, **kwargs)

    @property
    def is_hidden(self) -> bool:
        return self.help is False

    def __getitem__(self, section: "Section") -> Self:
        section.include(self)
        return self



class Cnst:
    __slots__ = ("value",)

    def __init__(self, value: Any):
        self.value: Final = value

    def __repr__(self) -> str:
        return _repr_class(self, {"value": self.value}, skip_none=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cnst):
            return NotImplemented
        return bool(self.value == other.value)

    def _build(self, owner: SupportsSetDefaults, config: Config, *, dest: str, **_rest: Any) -> None:
        owner.set_defaults(**{dest: self.value})


class Ctx:
    __slots__ = ()

    def _build(self, owner: SupportsSetDefaults, config: Config, *, dest: str, context: Any) -> None:
        if context is None:
            raise ValueError("context can't be None")
        owner.set_defaults(**{dest: context})


class MixedOpts:
    """Abstract mix of options"""

    __slots__ = ("options",)

    def __init__(self, *options: Opt):
        self.options: Final = options

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MixedOpts):
            return NotImplemented
        return self.options == other.options

    def __repr__(self) -> str:
        return _repr_class(self, {"options": self.options})

    def __getitem__(self, section: "Section") -> Self:
        for option in self.options:
            section.include(option)
        return self


class Action(Opt):
    """Special kind of option with side effects"""

    __slots__ = ()

    def _build(self, owner: SupportsAddArgument, config: Config, *, dest: str | Literal[False], **_rest: Any) -> None:
        if dest is not False:
            raise TypeError(f"Action is used in place of Option {dest!r}")
        return super()._build(owner, config, dest=dest)


class Section:
    """Shows its options in a separate block of a `--help` output"""

    def __init__(self, title: str, *, headline: str | Markup | None = None):
        self.title: Final = title
        self.headline: Final = headline
        self.options: Final[set[Opt]] = set()

    def __repr__(self) -> str:
        return _repr_class(self, self.__dict__)

    def include[T: Opt | MixedOpts](self, option: T) -> T:
        if isinstance(option, (Opt)):
            self.options.add(option)
        else:
            assert isinstance(option, MixedOpts)
            self.options.update(option.options)
        return option

    def _build(self, owner: SupportsAddArgumentGroup, config: Config) -> ArgumentGroupLike:
        return owner.add_argument_group(title=self.title, description=_as_plain(self.headline))

    __call__ = include


class Oneof:
    """Mutually exclusive section. Ensures only one of options present on a command line"""

    def __init__(self, *, required: bool = False):
        self.options: Final[set[Opt]] = set()
        self.required: Final = required

    def __repr__(self) -> str:
        return _repr_class(self, self.__dict__)

    def _build(self, owner: SupportsAddOneofGroup, config: Config) -> SupportsAddArgument:
        return owner.add_mutually_exclusive_group(required=self.required)

    def include[T: Opt | MixedOpts](self, option: T) -> T:
        if isinstance(option, Opt):
            self.options.add(option)
        else:
            assert isinstance(option, MixedOpts)
            self.options.update(option.options)
        return option

    __call__ = include


class ParserLike:
    def __init__(
        self,
        *,
        help: str | Markup | None = None,
        info: str | Markup | None = None,
        usage: str | Markup | None = None,
        epilog: str | Markup | None = None,
        prog: str | None = None,
    ):
        self.help = help
        self.info = info
        self.usage = usage
        self.epilog = epilog
        self.prog = prog

        self.arguments: list[Arg | Cnst | Ctx] | None = None
        self.actions: list[Action] = []
        self.options: dict[str, Opt | MixedOpts | Cnst | Ctx] | None = None
        self.sections: list[Section] = []
        self.oneofs: list[Oneof] = []

        # manually set if required
        self._func: Callable[..., None] | None = None

    def __repr__(self) -> str:
        return _repr_class(self, self.__dict__)

    def _set_params(self, *arguments: Any, **options: Any) -> None:
        """Set arguments and options. Positional parameters are arguments. Keyword parameters are options"""

        for i, argument in enumerate(arguments):
            if not isinstance(argument, (Arg, Cnst, Ctx)):
                raise TypeError(f"parameter {i} should be an Argument | Const | Context")

        for name, option in options.items():
            if not isinstance(option, (Opt, MixedOpts, Cnst, Ctx)):
                raise TypeError(f"parameter {name!r} should be Option | MixedOptions | Const | Context")

        self.arguments = [*arguments]
        self.options = {**options}

    def _build_sections(
        self, parser: ArgumentParserLike, config: Config, *, default_group: ArgumentGroupLike
    ) -> dict[Opt, SupportsAddArgument]:
        sectmap: dict[Opt, ArgumentGroupLike] = {}
        oneofmap: dict[Opt, SupportsAddArgument] = {}

        for section in self.sections:
            if section_dupes := section.options.intersection(sectmap):
                raise KeyError(f"options {section_dupes} are in several sections at once")

            sectmap |= dict.fromkeys(section.options, section._build(parser, config))

        for oneof in self.oneofs:
            if not oneof.options:
                continue

            if oneof_dupes := oneof.options.intersection(oneofmap):
                raise KeyError(f"options {oneof_dupes} are in several oneofs at once")

            groups = list({sectmap.get(option, default_group) for option in oneof.options})
            if len(groups) != 1:
                raise KeyError("all options in oneof should belong to the same section")

            oneofmap |= dict.fromkeys(oneof.options, oneof._build(groups[0], config))

        tgtmap = sectmap | oneofmap
        return tgtmap

    def _build_params(
        self, parser: ArgumentParserLike, config: Config, *, parents: Sequence["ParserLike"], context: Any
    ) -> None:
        if self._func:
            if self.arguments is None or self.options is None:
                raise ValueError("bind() was not called")

        level = len(parents)

        spec = _make_spec(level, self._func, self.arguments or [], self.options or {})
        parser.set_defaults(**{str(level): spec})

        if self.arguments:
            arguments_group = parser.add_argument_group(
                title=config.arguments_title, description=_as_plain(config.arguments_headline)
            )

            for i, argument in enumerate(self.arguments):
                dest = f"{level}[{i}]"
                argument._build(arguments_group, config, dest=dest, context=context)

        default_options_group = parser.add_argument_group(
            title=config.options_title, description=_as_plain(config.options_headline)
        )

        tgtmap = self._build_sections(parser, config, default_group=default_options_group)

        for action in self.actions:
            action._build(tgtmap.pop(action, default_options_group), config, dest=False)

        if self.options:
            for param, item in self.options.items():
                dest = f"{level}.{param}"
                seq = (item,) if not isinstance(item, MixedOpts) else item.options
                for opt in seq:
                    if isinstance(opt, (Cnst, Ctx)):
                        opt._build(parser, config, dest=dest, context=context)
                    else:
                        opt._build(tgtmap.pop(opt, default_options_group), config, dest=dest, context=context)

        if tgtmap:
            raise KeyError(f"unconsumed items in sections: {tgtmap.keys()}")

    def _build_subparser(
        self,
        parent: SupportsAddParser,
        config: Config,
        *,
        parents: Sequence["ParserLike"],
        name: str | tuple[str, ...],
    ) -> ArgumentParserLike:
        basename, aliases = name_and_aliases(name)

        epilog = self.epilog

        if epilog is None and config.propagate_epilog and parents:
            epilog = parents[0].epilog

        return parent.add_parser(
            basename,
            aliases=aliases,
            help=_as_plain(self.help),
            description=_as_plain(self.info if self.info is not None else self.help),
            epilog=_as_plain(epilog),
            usage=_as_plain(self.usage),
            prog=self.prog,
            formatter_class=config.formatter_class,
            add_help=False,
            allow_abbrev=config.allow_abbrev,
            **config.sub_parser_extra_kwargs,
        )

    def _build_root_parser(self, config: Config) -> argparse.ArgumentParser:
        return config.parser_class(
            description=_as_plain(self.info),
            epilog=_as_plain(self.epilog),
            usage=_as_plain(self.usage),
            prog=self.prog,
            formatter_class=config.formatter_class,
            add_help=False,
            allow_abbrev=config.allow_abbrev,
            **config.root_parser_extra_kwargs,
        )

    def append_action(self, action: Action) -> None:
        """Append Action"""
        self.actions.append(action)

    def add_oneof(self, *, required: bool = False) -> "Oneof":
        """Creates and adds new mutually exclusive section"""
        oneof = Oneof(required=required)
        self.oneofs.append(oneof)
        return oneof

    def add_section(self, title: str, *, headline: str | Markup | None = None) -> "Section":
        """Creates and adds new help section"""
        section = Section(title, headline=headline)
        self.sections.append(section)
        return section

    def get_real_arguments(self) -> list[Arg]:
        if not self.arguments:
            return []
        return [arg for arg in self.arguments if isinstance(arg, Arg)]

    def get_real_options(self) -> list[Opt]:
        if not self.options:
            return []
        out: list[Opt] = []
        for item in self.options.values():
            if isinstance(item, Opt):
                out.append(item)
            elif isinstance(item, MixedOpts):
                out.extend(item.options)
        return out

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        pass


class Handler:
    """Represents parsed arguments and options.
    Calling it will invoke the command handler"""

    def __init__(self, func: Callable[..., None] | None, arguments: list[Any], options: dict[str, Any]):
        self.func = func
        self.arguments = arguments
        self.options = options

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Handler):
            return NotImplemented
        return self.func == other.func and self.arguments == other.arguments and self.options == other.options

    def __repr__(self) -> str:
        return _repr_class(self, self.__dict__)

    def __call__(self) -> None:
        if not self.func:
            return
        self.func(*self.arguments, **self.options)

    @classmethod
    def from_ns(cls, ns: argparse.Namespace, spec: HandlerSpec) -> Self:
        vars = ns.__dict__

        args = [vars[name] for name in spec.args]
        kwargs = {k: vars[v] for k, v in spec.opts.items()}

        return cls(spec.func, args, kwargs)

    @classmethod
    def from_spec(cls, func: Callable[..., None] | None, /, *arguments: Any, **options: Any) -> Self:
        return cls(func, list(arguments), options)


class Route:
    """Represents sequence of handers, arguments and options.
    Calling it will invoke the handlers"""

    def __init__(self, handlers: Sequence[Handler], unknown_args: Sequence[str] | None = None):
        self.handlers = handlers
        self.unknown_args = unknown_args

    # unrecognized args are ignored for the comparison
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Route):
            return NotImplemented
        return self.handlers == other.handlers

    def __repr__(self) -> str:
        return _repr_class(self, self.__dict__)

    def __call__(self) -> None:
        for handler in self.handlers:
            handler()

    def __iter__(self) -> Iterator[Handler]:
        yield from self.handlers

    def __len__(self) -> int:
        return len(self.handlers)

    def __getitem__(self, idx: int) -> Handler:
        return self.handlers[idx]

    @property
    def nonempty(self) -> list[Handler]:
        return [h for h in self.handlers if h.func is not None]

    @classmethod
    def from_ns(cls, ns: argparse.Namespace, unknown_args: Sequence[str] | None = None) -> Self:
        specs: list[tuple[int, HandlerSpec]] = []
        for k, v in ns.__dict__.items():
            try:
                idx = int(k)
            except ValueError:
                pass
            else:
                specs.append((idx, v))
        specs.sort()

        handlers = [Handler.from_ns(ns, spec[1]) for spec in specs]
        return cls(handlers, unknown_args=unknown_args)


## More concrete


class Command[**P](ParserLike):
    """Represents the handler with parameters bound to arguments and options"""

    def __init__(
        self,
        func: Callable[P, None],
        *,
        help: str | Markup | None = None,
        info: str | Markup | None = None,
        usage: str | Markup | None = None,
        epilog: str | Markup | None = None,
        prog: str | None = None,
        add_help: bool = True,
    ):
        super().__init__(help=help, info=info, usage=usage, epilog=epilog, prog=prog)
        self._func = func

        if add_help:
            self.append_action(_help_action)

    def _build(
        self,
        parser: ArgumentParserLike,
        config: Config,
        *,
        parents: Sequence["Group"],
        context: Any,
        **kwargs: Any,
    ) -> None:
        self._build_params(parser, config, parents=parents, context=context)

    def bind(self, *arguments: P.args, **options: P.kwargs) -> Self:
        """Bind function parameters to arguments/options"""
        self._set_params(*arguments, **options)
        return self

    def parse(self, input: Sequence[str] | None = None, *, config: Config | None = None, context: Any = None) -> Route:
        """Parse command line. Allows to use the Command as standalone groupless CLI"""

        config = config or Config()
        parser = self._build_root_parser(config)
        self._build(parser, config, parents=[], context=context)

        if config.ignore_unknown_args:
            ns, unknown_args = parser.parse_known_args(input)
            return Route.from_ns(ns, unknown_args=unknown_args)

        ns = parser.parse_args(input)
        return Route.from_ns(ns)


class Group(ParserLike):
    """Represents group of commands. May contain nested groups"""

    def __init__(
        self,
        *,
        help: str | Markup | None = None,
        info: str | Markup | None = None,
        usage: str | Markup | None = None,
        epilog: str | Markup | None = None,
        prog: str | None = None,
        title: str | None = None,
        headline: str | Markup | None = None,
        metavar: str | None = None,
        default_func: DefaultFunc[...] | None = print_group_help,
        add_help: bool = True,
    ):
        super().__init__(help=help, info=info, usage=usage, epilog=epilog, prog=prog)

        self.headline: Final = headline
        self.title: Final = title
        self.metavar: Final = metavar
        self.default_func: Final = default_func
        self.nodes: dict[str | tuple[str, ...], Group | Command[...]] = {}

        if add_help:
            self.append_action(_help_action)

    def _build(self, parser: ArgumentParserLike, config: Config, *, parents: Sequence["Group"], context: Any) -> None:
        self._build_params(parser, config, parents=parents, context=context)
        self._build_default_handler(parser, config, parents=parents)
        self._build_nodes(parser, config, parents=parents, context=context)

    def _build_default_handler(
        self, parser: ArgumentParserLike, config: Config, *, parents: Sequence["ParserLike"]
    ) -> None:
        if not self.default_func:
            return

        default_func = _with_argparser_arg(self.default_func, parser)

        level = len(parents)
        next_level = level + 1
        spec = _make_spec(level, default_func, self.arguments or [], self.options or {})
        parser.set_defaults(**{str(next_level): spec})

    def _build_nodes(
        self, parent: ArgumentParserLike, config: Config, *, parents: Sequence["Group"], context: Any
    ) -> None:
        if not self.nodes:
            return

        sub = parent.add_subparsers(
            title=self.title if self.title is not None else config.commands_title,
            description=_as_plain(self.headline),
            parser_class=config.parser_class,
            metavar=self.metavar,
            required=False if self.default_func else True,
        )
        for name, node in self.nodes.items():
            try:
                parser = node._build_subparser(sub, config, name=name, parents=[*parents, self])
                node._build(parser, config, parents=[*parents, self], context=context)
            except Exception as e:
                e.add_note(f"{'  ' * len(parents)}- {name!r}")
                raise

    def parse(self, input: Sequence[str] | None = None, *, config: Config | None = None, context: Any = None) -> Route:
        """Parse command line"""

        config = config or Config()

        try:
            parser = self._build_root_parser(config)
            self._build(parser, config, parents=[], context=context)
        except Exception as e:
            e.add_note("- Cli")
            raise

        if config.ignore_unknown_args:
            ns, unknown_args = parser.parse_known_args(input)
            return Route.from_ns(ns, unknown_args=unknown_args)

        ns = parser.parse_args(input)
        return Route.from_ns(ns)

    def add_command[**P](
        self,
        name: str | tuple[str, ...],
        func: Callable[P, None],
        *,
        help: str | Markup | None = None,
        info: str | Markup | None = None,
        usage: str | Markup | None = None,
        epilog: str | Markup | None = None,
        add_help: bool = True,
    ) -> Command[P]:
        """Creates and adds new command"""
        cmd = Command(func, help=help, info=info, usage=usage, epilog=epilog, add_help=add_help)
        self.nodes[name] = cmd
        return cmd

    def add_group(
        self,
        name: str | tuple[str, ...],
        *,
        help: str | Markup | None = None,
        info: str | Markup | None = None,
        metavar: str | None = None,
        usage: str | Markup | None = None,
        epilog: str | Markup | None = None,
        title: str | None = None,
        headline: str | Markup | None = None,
        default_func: DefaultFunc[...] | None = print_group_help,
        add_help: bool = True,
    ) -> "Group":
        """Creates and adds new group"""
        group = Group(
            help=help,
            info=info,
            headline=headline,
            title=title,
            metavar=metavar,
            usage=usage,
            epilog=epilog,
            default_func=default_func,
            add_help=add_help,
        )
        self.nodes[name] = group
        return group

    def add_callable_group[**P](
        self,
        name: str | tuple[str, ...],
        func: Callable[P, None],
        *,
        help: str | Markup | None = None,
        info: str | Markup | None = None,
        metavar: str | None = None,
        usage: str | Markup | None = None,
        epilog: str | Markup | None = None,
        title: str | None = None,
        headline: str | Markup | None = None,
        default_func: DefaultFunc[P] | None = print_group_help,
        add_help: bool = True,
    ) -> "CallableGroup[P]":
        """Creates and adds new group with handler and parameters"""
        group = CallableGroup(
            func=func,
            help=help,
            info=info,
            headline=headline,
            title=title,
            metavar=metavar,
            usage=usage,
            epilog=epilog,
            default_func=default_func,
            add_help=add_help,
        )
        self.nodes[name] = group
        return group

    def __setitem__(self, name: str | tuple[str, ...], val: "Group | Command[...]") -> None:
        self.nodes[name] = val


class CallableGroup[**P](Group):
    """Group with with parameters"""

    def __init__(
        self,
        func: Callable[P, None],
        *,
        help: str | Markup | None = None,
        info: str | Markup | None = None,
        usage: str | Markup | None = None,
        epilog: str | Markup | None = None,
        prog: str | None = None,
        title: str | None = None,
        headline: str | Markup | None = None,
        metavar: str | None = None,
        default_func: DefaultFunc[P] | None = print_group_help,
        add_help: bool = True,
    ):
        super().__init__(
            help=help,
            info=info,
            usage=usage,
            epilog=epilog,
            prog=prog,
            title=title,
            headline=headline,
            metavar=metavar,
            default_func=default_func,
            add_help=add_help,
        )
        self._func = func

    def bind(self, *arguments: P.args, **options: P.kwargs) -> Self:
        """Bind function parameters to arguments/options"""
        self._set_params(*arguments, **options)
        return self


def help_action(*, help: str | Markup | bool = "Show help and exit") -> Action:
    return Action(("--help", "-h"), action="help", help=help)


def version_action(version: str, *, help: str | Markup | bool = "Show program's version number and exit") -> Action:
    return Action(("--version",), action="version", help=help, extra={"version": version})


_help_action: Final = help_action()
