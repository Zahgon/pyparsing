
from contextlib import contextmanager
import re
import typing
import unittest


from .core import (
    ParserElement,
    ParseException,
    Keyword,
    __diag__,
    __compat__,
)
from . import core_builtin_exprs


class pyparsing_test:

    class reset_pyparsing_context:

        def __init__(self):
            self._save_context = {}

        def save(self):
            self._save_context["default_whitespace"] = ParserElement.DEFAULT_WHITE_CHARS
            self._save_context["default_keyword_chars"] = Keyword.DEFAULT_KEYWORD_CHARS

            self._save_context["literal_string_class"] = (
                ParserElement._literalStringClass
            )

            self._save_context["verbose_stacktrace"] = ParserElement.verbose_stacktrace

            self._save_context["packrat_enabled"] = ParserElement._packratEnabled
            if ParserElement._packratEnabled:
                self._save_context["packrat_cache_size"] = (
                    ParserElement.packrat_cache.size
                )
            else:
                self._save_context["packrat_cache_size"] = None
            self._save_context["packrat_parse"] = ParserElement._parse
            self._save_context["recursion_enabled"] = (
                ParserElement._left_recursion_enabled
            )

            self._save_context["__diag__"] = {
                name: getattr(__diag__, name) for name in __diag__._all_names
            }

            self._save_context["__compat__"] = {
                "collect_all_And_tokens": __compat__.collect_all_And_tokens
            }

            return self

        def restore(self):
            if (
                ParserElement.DEFAULT_WHITE_CHARS
                != self._save_context["default_whitespace"]
            ):
                ParserElement.set_default_whitespace_chars(
                    self._save_context["default_whitespace"]
                )

            ParserElement.verbose_stacktrace = self._save_context["verbose_stacktrace"]

            Keyword.DEFAULT_KEYWORD_CHARS = self._save_context["default_keyword_chars"]
            ParserElement.inline_literals_using(
                self._save_context["literal_string_class"]
            )

            for name, value in self._save_context["__diag__"].items():
                (__diag__.enable if value else __diag__.disable)(name)

            ParserElement._packratEnabled = False
            if self._save_context["packrat_enabled"]:
                ParserElement.enable_packrat(self._save_context["packrat_cache_size"])
            else:
                ParserElement._parse = self._save_context["packrat_parse"]
            ParserElement._left_recursion_enabled = self._save_context[
                "recursion_enabled"
            ]

            for expr in core_builtin_exprs:
                expr.set_debug(False)

            __compat__.collect_all_And_tokens = self._save_context["__compat__"]

            return self

        def copy(self):
            ret = type(self)()
            ret._save_context.update(self._save_context)
            return ret

        def __enter__(self):
            return self.save()

        def __exit__(self, *args):
            self.restore()

    class TestParseResultsAsserts(unittest.TestCase):

        def assertParseResultsEquals(
            self, result, expected_list=None, expected_dict=None, msg=None
        ):
            pass

        def assertParseAndCheckList(
            self, expr, test_string, expected_list, msg=None, verbose=True
        ):
            pass

        def assertParseAndCheckDict(
            self, expr, test_string, expected_dict, msg=None, verbose=True
        ):
            pass

        def assertRunTestResults(
            self, run_tests_report, expected_parse_results=None, msg=None
        ):
            pass


    @staticmethod
    def with_line_numbers(
        s: str,
        start_line: typing.Optional[int] = None,
        end_line: typing.Optional[int] = None,
        expand_tabs: bool = True,
        eol_mark: str = "|",
        mark_spaces: typing.Optional[str] = None,
        mark_control: typing.Optional[str] = None,
        *,
        indent: typing.Union[str, int] = "",
        base_1: bool = True,
    ) -> str:
        """
        Helpful method for debugging a parser - prints a string with line and column numbers.
        (Line and column numbers are 1-based by default - if debugging a parse action,
        pass base_1=False, to correspond to the loc value passed to the parse action.)

        :param s: string to be printed with line and column numbers
        :param start_line: starting line number in s to print (default=1)
        :param end_line: ending line number in s to print (default=len(s))
        :param expand_tabs: expand tabs to spaces, to match the pyparsing default
        :param eol_mark: string to mark the end of lines, helps visualize trailing spaces
        :param mark_spaces: special character to display in place of spaces
        :param mark_control: convert non-printing control characters to a placeholding
                             character; valid values:

                             - ``"unicode"`` - replaces control chars with Unicode symbols, such as "␍" and "␊"
                             - any single character string - replace control characters with given string
                             - ``None`` (default) - string is displayed as-is


        :param indent: string to indent with line and column numbers; if an int
                       is passed, converted to ``" " * indent``
        :param base_1: whether to label string using base 1; if False, string will be
                       labeled based at 0

        :returns: input string with leading line numbers and column number headers

        .. versionchanged:: 3.2.0
           New ``indent`` and ``base_1`` arguments.
        """
        if expand_tabs:
            s = s.expandtabs()
        if isinstance(indent, int):
            indent = " " * indent
        indent = indent.expandtabs()
        if mark_control is not None:
            mark_control = typing.cast(str, mark_control)
            if mark_control == "unicode":
                transtable_map = {
                    c: u for c, u in zip(range(0, 33), range(0x2400, 0x2433))
                }
                transtable_map[127] = 0x2421
                tbl = str.maketrans(transtable_map)
                eol_mark = ""
            else:
                ord_mark_control = ord(mark_control)
                tbl = str.maketrans(
                    {c: ord_mark_control for c in list(range(0, 32)) + [127]}
                )
            s = s.translate(tbl)
        if mark_spaces is not None and mark_spaces != " ":
            if mark_spaces == "unicode":
                tbl = str.maketrans({9: 0x2409, 32: 0x2423})
                s = s.translate(tbl)
            else:
                s = s.replace(" ", mark_spaces)
        if start_line is None:
            start_line = 0
        if end_line is None:
            end_line = len(s.splitlines())
        end_line = min(end_line, len(s.splitlines()))
        start_line = min(max(0, start_line), end_line)

        if mark_control != "unicode":
            s_lines = s.splitlines()[max(start_line - base_1, 0) : end_line]
        else:
            s_lines = [
                line + "␊"
                for line in s.split("␊")[max(start_line - base_1, 0) : end_line]
            ]
        if not s_lines:
            return ""

        lineno_width = len(str(end_line))
        max_line_len = max(len(line) for line in s_lines)
        lead = f"{indent}{' ' * (lineno_width + 1)}"

        if max_line_len >= 99:
            header0 = (
                lead
                + ("" if base_1 else " ")
                + "".join(
                    f"{' ' * 99}{(i + 1) % 100}"
                    for i in range(max(max_line_len // 100, 1))
                )
                + "\n"
            )
        else:
            header0 = ""

        header1 = (
            ("" if base_1 else " ")
            + lead
            + "".join(f"         {(i + 1) % 10}" for i in range(-(-max_line_len // 10)))
            + "\n"
        )
        digits = "1234567890"
        header2 = (
            lead + ("" if base_1 else "0") + digits * (-(-max_line_len // 10)) + "\n"
        )
        return (
            header0
            + header1
            + header2
            + "\n".join(
                f"{indent}{i:{lineno_width}d}:{line}{eol_mark}"
                for i, line in enumerate(s_lines, start=start_line + base_1)
            )
            + "\n"
        )
