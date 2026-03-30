import argparse as ap
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
    NoReturn,
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
    TypeConverter,
)
from .conv import PathConv
from .exc import ParseAgain

# TODO:
# if section has a headline, it's not auto-purged from the help.
# Ok for user sections, bad for the default options/arguments sections

# Using ellipsis as a missing sentinel
type Missing = EllipsisType
MISSING: Final = ...


class Markup(Protocol):
    def plain(self) -> str: ...

    def __str__(self) -> str: ...


class ActionHandler[T](Protocol):
    def __call__(
        self,
        *,
        context: Any,
        parser: ap.ArgumentParser,
        # namespace: ap.Namespace,
        value: T,
        option_string: str | None = None,
        config: "Config",
        **kwargs: Any,
    ) -> None: ...


# TODO: narrow context type ?
class ConstLoader[T](Protocol):
    def __call__(self, *, context: Any) -> T | Missing: ...


class DefaultFunc[**P](Protocol):
    def __call__(self, parser: ap.ArgumentParser, /, *args: P.args, **kwargs: P.kwargs) -> None: ...


class HandlerSpec(NamedTuple):
    func: Callable[..., None] | None
    args: list[str]  # [arg_key]
    opts: dict[str, str]  # {opt_name: opt_key}


def _make_spec(
    level: int,
    func: Callable[..., None] | None,
    args: Sequence["Arg | ConstOpt | CtxOpt"],
    options: Mapping[str, "Opt | MixedOpts | ConstOpt | CtxOpt"],
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


def iter_impossible_option_names() -> Iterator[str]:
    i = 0
    while True:
        i += 1
        yield f"--\U000f0000{i}"


_impossible_option_names = iter_impossible_option_names()


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


def _may_raise_unhandled_exceptions(conv: TypeConverter[Any]) -> bool:
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
        return f"[{', '.join([str(item) for item in val])}]"
    return str(val)


def _with_argparser_arg[**P](
    f: Callable[Concatenate[ap.ArgumentParser, P], None], argparser: ap.ArgumentParser
) -> Callable[P, None]:
    def _wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        f(argparser, *args, **kwargs)

    return _wrapper


# took the idea from mypy. nice and simple.
# if there are newlines in text, emit as is (with indent)
# otherwise use default wrapping HelpFormatter.
# A few private methods are overridden. Not nice, but they are unlikely
# to change - nobody wants to broke mypy )
class HelpFormatter(ap.HelpFormatter):
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
    def _get_help_string(self, action: ap.Action) -> str | None:
        help = action.help

        if help is not None and "%(default)s" in help and action.default is not ap.SUPPRESS:
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
    parser_class: type[ap.ArgumentParser] = ap.ArgumentParser
    """Argparge parser class to use"""
    formatter_class: type[ap.HelpFormatter] = HelpFormatter
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
    inject: Mapping[str, Any] | None = None

    def __repr__(self) -> str:
        return _repr_class(self, {k: getattr(self, k) for k in self.__dataclass_fields__}, skip_empty=False)

    # (weak) hash is based on a metavar
    def __hash__(self) -> int:
        return hash(self.metavar)

    def _compose_settings(self, config: Config) -> dict[str, Any]:
        conv = self.conv
        if conv and config.catch_typeconv_exceptions and _may_raise_unhandled_exceptions(conv):
            conv = util.catch_all(conv)

        help = self.help

        if help is False:
            help = ap.SUPPRESS
        elif help is True:
            help = ""

        # these kwargs shouldn't be set at all if None
        out: dict[str, Any] = {
            "choices": self.choices,
            "nargs": self.nargs,
            "metavar": self.metavar,
            # NOTE: if type is not specified, argparse's MetavarTypeHelpFormatter may fail!
            "type": conv,
        }
        out = {k: v for k, v in out.items() if v is not None}
        if self.extra:
            out |= self.extra

        out["help"] = _as_plain(help)
        out["default"] = self.default

        return out

    def _build(self, owner: SupportsAddArgument, config: Config, *, dest: str, context: Any, **kwargs: Any) -> None:
        settings = self._compose_settings(config)
        action = owner.add_argument(dest=dest, **settings)
        if self.inject:
            for k, v in self.inject.items():
                setattr(action, k, v)

    def with_injected(self, **kwargs: Any) -> Self:
        """Return a copy of option with attributes to be injected into the action"""
        return dataclasses.replace(self, inject=kwargs)


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
    action: type[ap.Action] | str | None = None
    nargs: int | Literal["*", "+", "?"] | None = None
    default: Any = None
    const: Any = None
    deprecated: bool = False
    extra: Mapping[str, Any] | None = None
    inject: Mapping[str, Any] | None = None

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

    def _compose_settings(self, config: Config) -> dict[str, Any]:
        help = self.help

        if help is False:
            help = ap.SUPPRESS
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
        if conv and config.catch_typeconv_exceptions and _may_raise_unhandled_exceptions(conv):
            conv = util.catch_all(conv)

        # these kwargs shouldn't be set at all if None
        out: dict[str, Any] = {
            "action": self.action,
            "choices": self.choices,
            "nargs": self.nargs,
            "const": self.const,
            "metavar": self.metavar,
            "type": conv,
            "required": self.required or None,
            "deprecated": self.deprecated if sys.version_info >= (3, 13) else None,
        }
        out = {k: v for k, v in out.items() if v is not None}

        if self.extra:
            out |= self.extra

        out["default"] = self.default
        out["help"] = help

        return out

    def _build(self, owner: SupportsAddArgument, config: Config, *, dest: str, context: Any, **kwargs: Any) -> None:
        settings = self._compose_settings(config)
        action = owner.add_argument(*self.names, dest=dest, **settings)
        if self.inject:
            for k, v in self.inject.items():
                setattr(action, k, v)

    @property
    def is_hidden(self) -> bool:
        return self.help is False

    def __getitem__(self, section: "Section") -> Self:
        section.include(self)
        return self

    def with_injected(self, **kwargs: Any) -> Self:
        """Return a copy of option with attributes to be injected into the action"""
        return dataclasses.replace(self, inject=kwargs)


# We want repeated options to replace default values like a normal options.
# With the stock argparse there is no way to get rid of default, it always augmented.
# This little hack tracks the state of repeated options to know when to replace and when
# to append.
def _set_repeated_items(ns: ap.Namespace, dest: str, value: Any, *, extend: bool) -> None:
    seen_repeated_option: set[str] = getattr(ns, "_seen_repeated_options", set())
    if dest not in seen_repeated_option:
        seen_repeated_option.add(dest)
        setattr(ns, "_seen_repeated_options", seen_repeated_option)
        items: list[Any] = []
    else:
        items = getattr(ns, dest)[:]

    if extend:
        items.extend(value)
    else:
        items.append(value)
    setattr(ns, dest, items)


# Subclassing stock actions to change the default handling.
# They are private but looking stable.
# In case of future incompabilitity, it's easy to do a full reimplementation.


class AppendAction(ap._AppendAction):
    def __call__(
        self, parser: ap.ArgumentParser, namespace: ap.Namespace, values: Any, *args: Any, **kwargs: Any
    ) -> None:
        _set_repeated_items(namespace, self.dest, values, extend=False)


class AppendConstAction(ap._AppendConstAction):
    def __call__(self, parser: ap.ArgumentParser, namespace: ap.Namespace, *args: Any, **kwargs: Any) -> None:
        _set_repeated_items(namespace, self.dest, self.const, extend=False)


class ExtendAction(ap._AppendAction):
    def __call__(
        self, parser: ap.ArgumentParser, namespace: ap.Namespace, values: Any, *args: Any, **kwargs: Any
    ) -> None:
        _set_repeated_items(namespace, self.dest, values, extend=True)


class LoadConstAction(ap.Action):
    """Custom action returning dynamic default"""

    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str,
        option: "ConstOpt",
        context: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(option_strings, dest=dest, nargs=0, help=ap.SUPPRESS, **kwargs)
        self.option: Final = option
        self.context: Final = context

    # we try to load dynamic value
    # if value is missing, fallback to default
    # if still missing, suppress.
    # assuming parser-level default or next option will take priority
    @property
    def default(self) -> Any:
        value = self.option.default
        if self.option.load:
            res = self.option.load(context=self.context)
            if res is not MISSING:
                value = res
        if value is MISSING:
            return ap.SUPPRESS
        return value

    @default.setter
    def default(self, val: Any) -> None:
        pass


class CallableAction(ap.Action):
    """Action which delegates the very action to the user-defined handler"""

    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str,
        *args: Any,
        handler: ActionHandler[Any],
        context: Any,
        config: Config,
        **kwargs: Any,
    ) -> None:
        super().__init__(option_strings, dest, *args, **kwargs)
        self.handler = handler
        self.context = context
        self.config = config

    def __call__(
        self,
        parser: ap.ArgumentParser,
        namespace: ap.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        self.handler(
            context=self.context,
            parser=parser,
            value=values,
            option_string=option_string,
            config=self.config,
        )


class CtxOpt:
    """Astract Context option"""

    __slots__ = ()

    def _build(self, owner: ArgumentGroupLike, config: Config, *, dest: str, context: Any, **kwargs: Any) -> None:
        if context is None:
            raise ValueError("context can't be None")
        owner.set_defaults(**{dest: context})


class ConstOpt:
    """Astract (loadable) const option"""

    __slots__ = ("default", "load")

    def __init__(self, value: Any = None, load: ConstLoader[Any] | None = None):
        self.default: Final = value
        self.load: Final = load

    def __repr__(self) -> str:
        return _repr_class(self, {"default": self.default, "load": self.load}, skip_none=False, skip_empty=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ConstOpt):
            return NotImplemented
        return bool(self.load == other.load and self.load == other.load)

    def _build(self, owner: ArgumentGroupLike, config: Config, *, dest: str, context: Any, **kwargs: Any) -> None:
        # this set_default is for the case when we're a single option and load had failed.
        # If load was ok, it's value will win.
        # If load was not ok, next option default will win
        owner.set_defaults(**{dest: self.default})
        owner.add_argument(
            next(_impossible_option_names), action=LoadConstAction, dest=dest, context=context, option=self
        )


class MixedOpts:
    """Abstract mix of options"""

    __slots__ = ("options",)

    def __init__(self, *options: Opt | ConstOpt):
        _head, *_rest = options
        # Consts are working via setting default so only head is in effect.
        # This limitation is to avoid confusion.
        if any(isinstance(opt, ConstOpt) for opt in _rest):
            raise TypeError("Const may be only a first option of mix")

        self.options: Final = options

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MixedOpts):
            return NotImplemented
        return self.options == other.options

    def __repr__(self) -> str:
        return _repr_class(self, {"options": self.options})

    def __getitem__(self, section: "Section") -> Self:
        for option in self._real_options:
            section.include(option)
        return self

    @property
    def _real_options(self) -> list[Opt]:
        return [opt for opt in self.options if isinstance(opt, Opt)]

    @classmethod
    def _from_items(cls, *items: "Opt | ConstOpt | MixedOpts") -> Self:
        opts: list[Opt | ConstOpt] = []
        for item in items:
            if isinstance(item, MixedOpts):
                opts.extend(item.options)
            else:
                opts.append(item)
        return cls(*opts)


@dataclasses.dataclass(slots=True, repr=False)
class Action[T](Opt):
    """Special kind of option with side effects"""

    handler: ActionHandler[T]

    def __hash__(self) -> int:
        return hash(self.names)

    def _build(self, owner: SupportsAddArgument, config: Config, *, context: Any, **kwargs: Any) -> None:
        dest = kwargs.get("dest")
        if dest:
            raise TypeError(f"Action is used in place of Option {dest!r}")

        assert self.action is None

        settings = self._compose_settings(config)
        settings["default"] = ap.SUPPRESS

        action = owner.add_argument(
            *self.names,
            dest=ap.SUPPRESS,
            action=CallableAction,
            handler=self.handler,
            config=config,
            context=context,
            **settings,
        )
        if self.inject:
            for k, v in self.inject.items():
                setattr(action, k, v)


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
            self.options.update(option._real_options)
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
            self.options.update(option._real_options)
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

        self.arguments: list[Arg | ConstOpt | CtxOpt] | None = None
        self.actions: list[Action[Any]] = []
        self.options: dict[str, Opt | MixedOpts | ConstOpt | CtxOpt] | None = None
        self.sections: list[Section] = []
        self.oneofs: list[Oneof] = []

        # manually set if required
        self._func: Callable[..., None] | None = None

    def __repr__(self) -> str:
        return _repr_class(self, self.__dict__)

    def _set_params(self, *arguments: Any, **options: Any) -> None:
        """Set arguments and options. Positional parameters are arguments. Keyword parameters are options"""

        for i, argument in enumerate(arguments):
            if not isinstance(argument, (Arg, ConstOpt, CtxOpt)):
                raise TypeError(f"parameter {i} should be an Argument | Const | Load | Context")

        for name, option in options.items():
            if not isinstance(option, (Opt, MixedOpts, ConstOpt, CtxOpt)):
                raise TypeError(f"parameter {name!r} should be Option | MixedOptions | Const | Load | Context")

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
            action._build(tgtmap.pop(action, default_options_group), config, context=context)

        if self.options:
            for param, item in self.options.items():
                dest = f"{level}.{param}"
                seq = (item,) if not isinstance(item, MixedOpts) else item.options
                for opt in seq:
                    if isinstance(opt, (ConstOpt, CtxOpt)):
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

    def _create_root_parser(self, config: Config) -> ap.ArgumentParser:
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

    def append_action(self, action: Action[Any]) -> None:
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
                out.extend(item._real_options)
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
    def from_ns(cls, ns: ap.Namespace, spec: HandlerSpec) -> Self:
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
    def from_ns(cls, ns: ap.Namespace, unknown_args: Sequence[str] | None = None) -> Self:
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

    def build_parser(self, *, config: Config, context: Any = None) -> ap.ArgumentParser:
        """Build ArgumentParser"""
        parser = self._create_root_parser(config)
        self._build(parser, config, parents=[], context=context)
        return parser

    def parse(self, input: Sequence[str] | None = None, *, config: Config | None = None, context: Any = None) -> Route:
        """Parse command line. Allows to use the Command as standalone groupless CLI"""

        config = config or Config()
        parser = self.build_parser(config=config, context=context)
        unknown_args: list[str] | None = None

        while True:
            try:
                if config.ignore_unknown_args:
                    ns, unknown_args = parser.parse_known_args(input)
                else:
                    ns = parser.parse_args(input)
                break
            except ParseAgain:
                continue

        return Route.from_ns(ns, unknown_args=unknown_args)


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

        ap_parser: ap.ArgumentParser = parser  # type: ignore # ty: ignore[invalid-assignment]
        default_func = _with_argparser_arg(self.default_func, ap_parser)

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

    def build_parser(self, *, config: Config, context: Any = None) -> ap.ArgumentParser:
        """Build ArgumentParser"""
        parser = self._create_root_parser(config)
        self._build(parser, config, parents=[], context=context)
        return parser

    def parse(self, input: Sequence[str] | None = None, *, config: Config | None = None, context: Any = None) -> Route:
        """Parse command line"""

        config = config or Config()

        try:
            parser = self.build_parser(config=config, context=context)
        except Exception as e:
            e.add_note("- Cli")
            raise

        unknown_args: list[str] | None = None

        while True:
            try:
                if config.ignore_unknown_args:
                    ns, unknown_args = parser.parse_known_args(input)
                else:
                    ns = parser.parse_args(input)
                break
            except ParseAgain:
                continue

        return Route.from_ns(ns, unknown_args=unknown_args)

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


def _help_action_handler(*, parser: ap.ArgumentParser, **kwargs: Any) -> NoReturn:
    parser.print_help()
    parser.exit(0)


# it really belongs to the acts.py, but we need it here and circular imports are bad
def help_action(
    *, help: str | Markup | bool = "Show help and exit", names: tuple[str, ...] = ("--help", "-h")
) -> Action[None]:
    return Action(names, help=help, nargs=0, handler=_help_action_handler)


_help_action: Final = help_action()
