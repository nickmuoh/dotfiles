"""Vendored command parser from ReceiptAnalyzerPipeline/anarcpt/cli.py."""

import re
from argparse import Action
from argparse import ArgumentParser as BaseArgParser
from enum import Enum
from functools import wraps
from inspect import signature
from typing import Any, Callable, Generic, NoReturn, Optional, Sequence, TypeVar

F = TypeVar("F")
ArgParseCallable = Callable[..., object]

TERM_CODE_REGEX = re.compile(r"\[\d{1,2}m")
TERM_COLOR_CODE_REGEX = re.compile(r"(.{2})(?=\[\d{1,2}m)")


class copy_signature(Generic[F]):  # noqa: N801
    def __init__(self, target: F) -> None: ...

    def __call__(self, wrapped: Callable[..., Any]) -> F:
        return wrapped  # type: ignore[return-value]


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class TermColors(StrEnum):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


CLIArgument = copy_signature(BaseArgParser.add_argument)


class ArgumentParser(BaseArgParser):
    @staticmethod
    def _strip_termcodes(msg: str) -> str:
        stripped_msg = TERM_COLOR_CODE_REGEX.sub("", msg)
        return TERM_CODE_REGEX.sub(" ", stripped_msg)

    @staticmethod
    def cast_as(type_: Callable[..., Any]):
        class CastAction(Action):
            def __call__(self, parser, namespace, values, option_string=None):
                del parser, option_string
                setattr(namespace, self.dest, type_(values))

        return CastAction

    def print_message(self, message: str, is_colored: bool = True) -> None:
        if is_colored:
            formatted = f"{TermColors.OKBLUE}({self.prog}){TermColors.ENDC} {message}\n"
        else:
            formatted = self._strip_termcodes(f"({self.prog}) {message}\n")
        self._print_message(formatted)

    def print_error(self, message: str, is_colored: bool = False) -> NoReturn:
        if is_colored:
            formatted = (
                f"{TermColors.FAIL}{self.prog}: error: {TermColors.ENDC} {message}\n"
            )
        else:
            formatted = self._strip_termcodes(f"{self.prog}: error: {message}\n")
        self.exit(2, formatted)

    def enable_subcommands(self) -> None:
        self.sub_parser = self.add_subparsers(
            dest="command", title="available commands", metavar="command [options ...]"
        )

    def command(self, *arguments, help: str = "⎼", parents: Optional[Sequence] = None):
        parents_ = [] if parents is None else parents
        if not hasattr(self, "sub_parser") or getattr(self, "sub_parser", None) is None:
            raise AttributeError(
                'Sub parser not found! Did you forget to call ".enable_subcommands()" method?'
            )

        def decorator(func: ArgParseCallable):
            group_store: dict[object, Any] = {}
            parameter_names = set(signature(func).parameters)
            func_name = func.__name__.replace("_", "-")
            cmd_parser = self.sub_parser.add_parser(
                func_name, description=func.__doc__, help=help, parents=parents_
            )

            @wraps(func)
            def wrapper(kwargs):
                command_arguments = {
                    name: value
                    for name, value in vars(kwargs).items()
                    if name in parameter_names
                }
                return func(**command_arguments)

            for args in arguments:
                cmd_args, cmd_kwargs = args
                cmd_kwargs = cmd_kwargs.copy()
                if "exclusive_group" in cmd_kwargs:
                    group_key = cmd_kwargs.pop("exclusive_group")
                    is_group_required = cmd_kwargs.pop("group_required", False)
                    if group_key not in group_store:
                        group_store[group_key] = (
                            cmd_parser.add_mutually_exclusive_group(
                                required=is_group_required
                            )
                        )
                    group_store[group_key].add_argument(*cmd_args, **cmd_kwargs)
                else:
                    cmd_parser.add_argument(*cmd_args, **cmd_kwargs)
                cmd_parser.set_defaults(func=wrapper)
            return wrapper

        return decorator

    @copy_signature(BaseArgParser.add_argument)
    def argument(self, *args, **kwargs):
        return args, kwargs

    def bind(self, argument):
        args, kwargs = argument
        kwargs_ = kwargs.copy()

        def decorator(func: ArgParseCallable):
            kwargs_.update(
                {"dest": func.__name__, "action": "store_const", "const": func}
            )
            self.add_argument(*args, **kwargs_)
            return func

        return decorator
