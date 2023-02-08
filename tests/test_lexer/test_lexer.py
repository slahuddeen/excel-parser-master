# coding: utf-8

from __future__ import division, print_function, unicode_literals

import pytest

from formatcode.lexer.lexer import DuplicateUniqueToken, MatchError, to_tokens_line
from formatcode.lexer.tokens import (AmPmToken, AsteriskSymbol, AtSymbol, BlockDelimiter, ColorToken, CommaDelimiter,
                                     ConditionToken, DateTimeToken, DotDelimiter, EToken, GeneralToken, HashToken,
                                     LocaleCurrencyToken, PercentageSymbol, QToken, SlashSymbol, StringSymbol,
                                     TimeDeltaToken, UnderscoreSymbol, ZeroToken)

examples = (
    ('General', [GeneralToken]),
    ('####.#', [HashToken] * 4 + [DotDelimiter] + [HashToken]),
    ('#.000', [HashToken] + [DotDelimiter] + [ZeroToken] * 3),
    ('0.#', [ZeroToken, DotDelimiter, HashToken]),
    ('#.0#', [HashToken, DotDelimiter, ZeroToken, HashToken]),
    ('???.???', [QToken] * 3 + [DotDelimiter] + [QToken] * 3),
    ('#" "???/???', [HashToken, StringSymbol] + [QToken] * 3 + [SlashSymbol] + [QToken] * 3),
    ('#" "???/100', [HashToken, StringSymbol] + [QToken] * 3 + [SlashSymbol]),
    ('#,###', [HashToken, CommaDelimiter] + [HashToken] * 3),
    ('#,', [HashToken, CommaDelimiter]),
    ('0.0', [ZeroToken, DotDelimiter, ZeroToken]),
    ('[Red]0.0;[Blue]#.#', [ColorToken, ZeroToken, DotDelimiter, ZeroToken, BlockDelimiter,
                            ColorToken, HashToken, DotDelimiter, HashToken]),
    ('[<100]0.0;[>=100]#.#', [ConditionToken, ZeroToken, DotDelimiter, ZeroToken, BlockDelimiter,
                              ConditionToken, HashToken, DotDelimiter, HashToken]),
    ('[Red][<100]0.0;[Blue][>=100]#.#', [ColorToken, ConditionToken, ZeroToken, DotDelimiter, ZeroToken, BlockDelimiter,
                                         ColorToken, ConditionToken, HashToken, DotDelimiter, HashToken]),
    ('[$$-409][Red][<100]0.0;[Blue][>=100]#.#\\ [$$-409]', [LocaleCurrencyToken, ColorToken, ConditionToken, ZeroToken,
                                                            DotDelimiter, ZeroToken, BlockDelimiter,
                                                            ColorToken, ConditionToken, HashToken, DotDelimiter,
                                                            HashToken, StringSymbol, LocaleCurrencyToken]),
    ('[$$-409]0.0;#.#\\ [$$-409]', [LocaleCurrencyToken, ZeroToken, DotDelimiter, ZeroToken, BlockDelimiter,
                                    HashToken, DotDelimiter, HashToken, StringSymbol, LocaleCurrencyToken]),
    ('-* 0.0', [StringSymbol, AsteriskSymbol, ZeroToken, DotDelimiter, ZeroToken]),
    ('_ 0.0', [UnderscoreSymbol, StringSymbol, ZeroToken, DotDelimiter, ZeroToken]),
    ('0.0', [ZeroToken, DotDelimiter, ZeroToken]),
    ('0.0E-000', [ZeroToken, DotDelimiter, ZeroToken, EToken] + [ZeroToken] * 3),
    ('0.0E+00', [ZeroToken, DotDelimiter, ZeroToken, EToken] + [ZeroToken] * 2),
    ('0.0e-?', [ZeroToken, DotDelimiter, ZeroToken, EToken, QToken]),
    ('0.0e+000%', [ZeroToken, DotDelimiter, ZeroToken, EToken] + [ZeroToken] * 3 + [PercentageSymbol]),
    ('0.0%', [ZeroToken, DotDelimiter, ZeroToken, PercentageSymbol]),
    ('00000', [ZeroToken] * 5),
    ('"000"#', [StringSymbol, HashToken]),
    ('\\0#', [StringSymbol, HashToken]),
    ('"000"@', [StringSymbol, AtSymbol]),
    ('"0"#', [StringSymbol, HashToken]),
    ('yy', [DateTimeToken]),
    ('m', [DateTimeToken]),
    ('mmm', [DateTimeToken]),
    ('mmmm', [DateTimeToken]),
    ('mmmmm', [DateTimeToken]),
    ('d', [DateTimeToken]),
    ('dd', [DateTimeToken]),
    ('ddd', [DateTimeToken]),
    ('dddd', [DateTimeToken]),
    ('h', [DateTimeToken]),
    ('hh', [DateTimeToken]),
    ('h:m', [DateTimeToken, StringSymbol, DateTimeToken]),
    ('hmm', [DateTimeToken] * 2),
    ('s', [DateTimeToken]),
    ('ss', [DateTimeToken]),
    ('h AM/PM', [DateTimeToken, StringSymbol, AmPmToken]),
    ('h:mm AM/PM', [DateTimeToken, StringSymbol] * 2 + [AmPmToken]),
    ('h:mm:ss A/P', [DateTimeToken, StringSymbol] * 3 + [AmPmToken]),
    ('[h]:mm', [TimeDeltaToken, StringSymbol, DateTimeToken]),
    ('[mm]:ss', [TimeDeltaToken, StringSymbol, DateTimeToken]),
    ('[ss].00', [TimeDeltaToken, DotDelimiter] + [ZeroToken] * 2),
    ('# 00;0 00', [HashToken, StringSymbol, ZeroToken, ZeroToken, BlockDelimiter,
                   ZeroToken, StringSymbol, ZeroToken, ZeroToken]),
)


def to_classes(tokens_list):
    return list(map(lambda x: x.__class__, tokens_list))


@pytest.mark.parametrize(['code', 'result'], examples)
def test_to_tokens_line(code, result):
    assert to_classes(to_tokens_line(code)) == result


def test_to_tokens_line_with_error():
    with pytest.raises(MatchError):
        to_tokens_line('"0.0')
    with pytest.raises(DuplicateUniqueToken):
        to_tokens_line('[Red][Red]0.0')
    with pytest.raises(DuplicateUniqueToken):
        to_tokens_line('[>=0][<0]0.0')
    with pytest.raises(DuplicateUniqueToken):
        to_tokens_line('[ss][mm]')
    with pytest.raises(DuplicateUniqueToken):
        to_tokens_line('[$$-409][$$-409]0.0')
