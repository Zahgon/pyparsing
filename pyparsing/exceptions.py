from __future__ import annotations

import copy
import re
import sys
import typing
import warnings
from functools import cached_property

from .warnings import PyparsingDeprecationWarning
from .unicode import pyparsing_unicode as ppu
from .util import (
    _collapse_string_to_ranges,
    col,
    deprecate_argument,
    line,
    lineno,
    replaced_by_pep8,
)


class _ExceptionWordUnicodeSet(
    ppu.Latin1, ppu.LatinA, ppu.LatinB, ppu.Greek, ppu.Cyrillic
):
    pass


_extract_alphanums = _collapse_string_to_ranges(_ExceptionWordUnicodeSet.alphanums)
_exception_word_extractor = re.compile(fr"([{_extract_alphanums}]{{1,16}})|.")


class ParseBaseException(Exception):

    loc: int
    msg: str
    pstr: str
    parser_element: typing.Any  # "ParserElement"
    args: tuple[str, int, typing.Optional[str]]

    __slots__ = (
        "loc",
        "msg",
        "pstr",
        "parser_element",
        "args",
    )

    def __init__(
        self,
        pstr: str,
        loc: int = 0,
        msg: typing.Optional[str] = None,
        elem=None,
    ) -> None:
        if msg is None:
            msg, pstr = pstr, ""

        self.loc = loc
        self.msg = msg
        self.pstr = pstr
        self.parser_element = elem
        self.args = (pstr, loc, msg)

    @staticmethod
    def explain_exception(exc: Exception, depth: int = 16) -> str:
        """
        Method to take an exception and translate the Python internal traceback into a list
        of the pyparsing expressions that caused the exception to be raised.

        Parameters:

        - exc - exception raised during parsing (need not be a ParseException, in support
          of Python exceptions that might be raised in a parse action)
        - depth (default=16) - number of levels back in the stack trace to list expression
          and function names; if None, the full stack trace names will be listed; if 0, only
          the failing input line, marker, and exception string will be shown

        Returns a multi-line string listing the ParserElements and/or function names in the
        exception's stack trace.
        """
        import inspect
        from .core import ParserElement

        if depth is None:
            depth = sys.getrecursionlimit()
        ret: list[str] = []
        if isinstance(exc, ParseBaseException):
            ret.append(exc.line)
            ret.append(f"{'^':>{exc.column}}")
        ret.append(f"{type(exc).__name__}: {exc}")

        if depth <= 0 or exc.__traceback__ is None:
            return "\n".join(ret)

        callers = inspect.getinnerframes(exc.__traceback__, context=depth)
        seen: set[int] = set()
        for ff in callers[-depth:]:
            frm = ff[0]

            f_self = frm.f_locals.get("self", None)
            if isinstance(f_self, ParserElement):
                if not frm.f_code.co_name.startswith(("parseImpl", "_parseNoCache")):
                    continue
                if id(f_self) in seen:
                    continue
                seen.add(id(f_self))

                self_type = type(f_self)
                ret.append(f"{self_type.__module__}.{self_type.__name__} - {f_self}")

            elif f_self is not None:
                self_type = type(f_self)
                ret.append(f"{self_type.__module__}.{self_type.__name__}")

            else:
                code = frm.f_code
                if code.co_name in ("wrapper", "<module>"):
                    continue

                ret.append(code.co_name)

            depth -= 1
            if not depth:
                break

        return "\n".join(ret)

    @classmethod
    def _from_exception(cls, pe) -> ParseBaseException:
        pass

    @cached_property
    def line(self) -> str:
        """
        Return the line of text where the exception occurred.
        """
        return line(self.loc, self.pstr)

    @cached_property
    def lineno(self) -> int:
        pass

    @cached_property
    def col(self) -> int:
        """
        Return the 1-based column on the line of text where the exception occurred.
        """
        return col(self.loc, self.pstr)

    @cached_property
    def column(self) -> int:
        pass




    def copy(self):
        return copy.copy(self)

    def formatted_message(self) -> str:
        pass

    def __str__(self) -> str:
        """
        .. versionchanged:: 3.2.0
           Now uses :meth:`formatted_message` to format message.
        """
        try:
            return self.formatted_message()
        except Exception as ex:
            return (
                f"{type(self).__name__}: {self.msg}"
                f" ({type(ex).__name__}: {ex} while formatting message)"
            )

    def __repr__(self):
        return str(self)

    def mark_input_line(
        self, marker_string: typing.Optional[str] = None, **kwargs
    ) -> str:
        pass

    def explain(self, depth: int = 16) -> str:
        """
        Method to translate the Python internal traceback into a list
        of the pyparsing expressions that caused the exception to be raised.

        Parameters:

        - depth (default=16) - number of levels back in the stack trace to list expression
          and function names; if None, the full stack trace names will be listed; if 0, only
          the failing input line, marker, and exception string will be shown

        Returns a multi-line string listing the ParserElements and/or function names in the
        exception's stack trace.

        Example:

        .. testcode::

            # an expression to parse 3 integers
            expr = pp.Word(pp.nums) * 3
            try:
                # a failing parse - the third integer is prefixed with "A"
                expr.parse_string("123 456 A789")
            except pp.ParseException as pe:
                print(pe.explain(depth=0))

        prints:

        .. testoutput::

            123 456 A789
                    ^
            ParseException: Expected W:(0-9), found 'A789'  (at char 8), (line:1, col:9)

        Note: the diagnostic output will include string representations of the expressions
        that failed to parse. These representations will be more helpful if you use `set_name` to
        give identifiable names to your expressions. Otherwise they will use the default string
        forms, which may be cryptic to read.

        Note: pyparsing's default truncation of exception tracebacks may also truncate the
        stack of expressions that are displayed in the ``explain`` output. To get the full listing
        of parser expressions, you may have to set ``ParserElement.verbose_stacktrace = True``
        """
        return self.explain_exception(self, depth)

    markInputline = replaced_by_pep8("markInputline", mark_input_line)


class ParseException(ParseBaseException):
    pass


class ParseFatalException(ParseBaseException):
    pass


class ParseSyntaxException(ParseFatalException):
    pass


class RecursiveGrammarException(Exception):

    def __init__(self, parseElementList) -> None:
        self.parseElementTrace = parseElementList

    def __str__(self) -> str:
        return f"RecursiveGrammarException: {self.parseElementTrace}"
