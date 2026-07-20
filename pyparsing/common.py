from .core import *
from .helpers import DelimitedList, any_open_tag, any_close_tag
from datetime import datetime, timedelta
import sys

PY_310_OR_LATER = sys.version_info >= (3, 10)


class pyparsing_common:

    @staticmethod
    def convert_to_integer(_, __, t) -> list[int]:
        pass

    @staticmethod
    def convert_to_float(_, __, t) -> list[float]:
        pass

    integer = (
        Word(nums)
        .set_name("integer")
        .set_parse_action(
            convert_to_integer
            if PY_310_OR_LATER
            else token_map(int)
        )
    )
    """expression that parses an unsigned integer, converts to an int"""

    hex_integer = (
        Word(hexnums).set_name("hex integer").set_parse_action(token_map(int, 16))
    )
    """expression that parses a hexadecimal integer, converts to an int"""

    signed_integer = (
        Regex(r"[+-]?\d+")
        .set_name("signed integer")
        .set_parse_action(
            convert_to_integer
            if PY_310_OR_LATER
            else token_map(int)
        )
    )
    """expression that parses an integer with optional leading sign, converts to an int"""

    fraction = (
        signed_integer().set_parse_action(
            convert_to_float
            if PY_310_OR_LATER
            else token_map(float)
        )
        + "/"
        + signed_integer().set_parse_action(
            convert_to_float
            if PY_310_OR_LATER
            else token_map(float)
        )
    ).set_name("fraction")
    """fractional expression of an integer divided by an integer, converts to a float"""
    fraction.add_parse_action(lambda tt: tt[0] / tt[-1])

    mixed_integer = (
        fraction | signed_integer + Opt(Opt("-").suppress() + fraction)
    ).set_name("fraction or mixed integer-fraction")
    """mixed integer of the form 'integer - fraction', with optional leading integer, converts to a float"""
    mixed_integer.add_parse_action(sum)

    real = (
        Regex(r"[+-]?(?:\d+\.\d*|\.\d+)")
        .set_name("real number")
        .set_parse_action(
            convert_to_float
            if PY_310_OR_LATER
            else token_map(float)
        )
    )
    """expression that parses a floating point number, converts to a float"""

    sci_real = (
        Regex(r"[+-]?(?:\d+(?:[eE][+-]?\d+)|(?:\d+\.\d*|\.\d+)(?:[eE][+-]?\d+)?)")
        .set_name("real number with scientific notation")
        .set_parse_action(
            convert_to_float
            if PY_310_OR_LATER
            else token_map(float)
        )
    )
    """expression that parses a floating point number with optional
    scientific notation, converts to a float"""

    number = (sci_real | real | signed_integer).set_name("number").streamline()
    """any numeric expression, converts to the corresponding Python type"""

    fnumber = (
        Regex(r"[+-]?\d+\.?\d*(?:[eE][+-]?\d+)?")
        .set_name("fnumber")
        .set_parse_action(
            convert_to_float
            if PY_310_OR_LATER
            else token_map(float)
        )
    )
    """any int or real number, always converts to a float"""

    ieee_float = (
        Regex(r"(?i:[+-]?(?:(?:\d+\.?\d*(?:e[+-]?\d+)?)|nan|inf(?:inity)?))")
        .set_name("ieee_float")
        .set_parse_action(
            convert_to_float
            if PY_310_OR_LATER
            else token_map(float)
        )
    )
    """any floating-point literal (int, real number, infinity, or NaN), converts to a float"""

    identifier = Word(identchars, identbodychars).set_name("identifier")
    """typical code identifier (leading alpha or '_', followed by 0 or more alphas, nums, or '_')"""

    ipv4_address = Regex(
        r"(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})(?:\.(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}"
    ).set_name("IPv4 address")
    "IPv4 address (``0.0.0.0 - 255.255.255.255``)"

    _ipv6_part = Regex(r"[0-9a-fA-F]{1,4}").set_name("hex_integer")
    _full_ipv6_address = (_ipv6_part + (":" + _ipv6_part) * 7).set_name(
        "full IPv6 address"
    )
    _short_ipv6_address = (
        Opt(_ipv6_part + (":" + _ipv6_part) * (0, 6))
        + "::"
        + Opt(_ipv6_part + (":" + _ipv6_part) * (0, 6))
    ).set_name("short IPv6 address")
    _short_ipv6_address.add_condition(
        lambda t: sum(1 for tt in t if pyparsing_common._ipv6_part.matches(tt)) < 8
    )
    _mixed_ipv6_address = ("::ffff:" + ipv4_address).set_name("mixed IPv6 address")
    ipv6_address = Combine(
        (_full_ipv6_address | _mixed_ipv6_address | _short_ipv6_address).set_name(
            "IPv6 address"
        )
    ).set_name("IPv6 address")
    "IPv6 address (long, short, or mixed form)"

    mac_address = Regex(
        r"[0-9a-fA-F]{2}([:.-])[0-9a-fA-F]{2}(?:\1[0-9a-fA-F]{2}){4}"
    ).set_name("MAC address")
    "MAC address xx:xx:xx:xx:xx (may also have '-' or '.' delimiters)"

    @staticmethod
    def convert_to_date(fmt: str = "%Y-%m-%d"):
        """
        Helper to create a parse action for converting parsed date string to Python datetime.date

        Params -
        - fmt - format to be passed to datetime.strptime (default= ``"%Y-%m-%d"``)

        Example:

        .. testcode::

            date_expr = pyparsing_common.iso8601_date.copy()
            date_expr.set_parse_action(pyparsing_common.convert_to_date())
            print(date_expr.parse_string("1999-12-31"))

        prints:

        .. testoutput::

            [datetime.date(1999, 12, 31)]
        """


        return cvt_fn

    @staticmethod
    def convert_to_datetime(fmt: str = "%Y-%m-%dT%H:%M:%S.%f"):
        pass

    iso8601_date = Regex(
        r"(?P<year>\d{4})(?:-(?P<month>\d\d)(?:-(?P<day>\d\d))?)?"
    ).set_name("ISO8601 date")
    "ISO8601 date (``yyyy-mm-dd``)"

    iso8601_datetime = Regex(
        r"(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d)[T ](?P<hour>\d\d):(?P<minute>\d\d)(:(?P<second>\d\d(\.\d*)?)?)?(?P<tz>Z|[+-]\d\d:?\d\d)?"
    ).set_name("ISO8601 datetime")
    "ISO8601 datetime (``yyyy-mm-ddThh:mm:ss.s(Z|+-00:00)``) - trailing seconds, milliseconds, and timezone optional; accepts separating ``'T'`` or ``' '``"

    @staticmethod
    def as_datetime(s, l, t):
        pass

    if PY_310_OR_LATER:
        iso8601_date_validated = iso8601_date().add_parse_action(as_datetime)
        "Validated ISO8601 date strings, raising :class:`ParseException` for invalid date values."

        iso8601_datetime_validated = iso8601_datetime().add_parse_action(as_datetime)
        "Validated ISO8601 date and time strings, raising :class:`ParseException` for invalid date/time values."

    uuid = Regex(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}").set_name(
        "UUID"
    )
    "UUID (``xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx``)"

    _html_stripper = any_open_tag.suppress() | any_close_tag.suppress()

    @staticmethod
    def strip_html_tags(s: str, l: int, tokens: ParseResults):
        pass

    _commasepitem = (
        Combine(
            OneOrMore(
                ~Literal(",")
                + ~LineEnd()
                + Word(printables, exclude_chars=",")
                + Opt(White(" \t") + ~FollowedBy(LineEnd() | ","))
            )
        )
        .streamline()
        .set_name("commaItem")
    )
    comma_separated_list = DelimitedList(
        Opt(quoted_string.copy() | _commasepitem, default="")
    ).set_name("comma separated list")
    """Predefined expression of 1 or more printable words or quoted strings, separated by commas."""

    @staticmethod
    def upcase_tokens(s, l, t):
        pass

    @staticmethod
    def downcase_tokens(s, l, t):
        pass

    url = Regex(
        r"(?P<url>"
        r"(?:(?:(?P<scheme>https?|ftp):)?\/\/)"
        r"(?:(?P<auth>\S+(?::\S*)?)@)?"
        r"(?P<host>"
        r"(?!(?:10|127)(?:\.\d{1,3}){3})"
        r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
        r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
        r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
        r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
        r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
        r"|"
        r"(?:"
        r"(?:"
        r"[a-z0-9\u00a1-\uffff]"
        r"[a-z0-9\u00a1-\uffff_-]{0,62}"
        r")?"
        r"[a-z0-9\u00a1-\uffff]\."
        r")+"
        r"(?:[a-z\u00a1-\uffff]{2,}\.?)"
        r")"
        r"(:(?P<port>\d{2,5}))?"
        r"(?P<path>\/[^?# ]*)?"
        r"(\?(?P<query>[^#]*))?"
        r"(#(?P<fragment>\S*))?"
        r")"
    ).set_name("url")
    """
    URL (http/https/ftp scheme)
    
    .. versionchanged:: 3.1.0
       ``url`` named group added
    """

    convertToInteger = staticmethod(replaced_by_pep8("convertToInteger", convert_to_integer))
    convertToFloat = staticmethod(replaced_by_pep8("convertToFloat", convert_to_float))
    convertToDate = staticmethod(replaced_by_pep8("convertToDate", convert_to_date))
    convertToDatetime = staticmethod(replaced_by_pep8("convertToDatetime", convert_to_datetime))
    stripHTMLTags = staticmethod(replaced_by_pep8("stripHTMLTags", strip_html_tags))
    upcaseTokens = staticmethod(replaced_by_pep8("upcaseTokens", upcase_tokens))
    downcaseTokens = staticmethod(replaced_by_pep8("downcaseTokens", downcase_tokens))


_builtin_exprs = [
    v for v in vars(pyparsing_common).values() if isinstance(v, ParserElement)
]
