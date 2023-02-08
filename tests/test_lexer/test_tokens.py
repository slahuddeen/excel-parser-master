# coding: utf-8

from __future__ import division, print_function, unicode_literals

import pytest
from six.moves import range

from formatcode.lexer.tokens import (AmPmToken, AsteriskSymbol, AtSymbol, BlockDelimiter, ColorToken, CommaDelimiter,
                                     ConditionToken, DateTimeToken, DotDelimiter, EToken, GeneralToken, HashToken,
                                     LocaleCurrencyToken, PercentageSymbol, QToken, SlashSymbol, StringSymbol,
                                     TimeDeltaToken, UnderscoreSymbol, ZeroToken)


def test_general_token():
    assert GeneralToken.match('General') == len('General')
    assert GeneralToken.match('1') is None

    assert GeneralToken('General').cleaned_data == 'General'


def test_slash_token():
    assert SlashSymbol.match('/') == 1
    assert SlashSymbol.match('1') is None

    assert SlashSymbol('/').value is None

    assert SlashSymbol.match('/1234') == 5
    assert SlashSymbol('/1234').value == 1234


def test_block_delimiter():
    assert BlockDelimiter.match(';') == 1
    assert BlockDelimiter.match('1') is None

    assert BlockDelimiter(';').cleaned_data == ';'


def test_zero():
    assert ZeroToken.match('0') == 1
    assert ZeroToken.match('1') is None

    assert ZeroToken('0').cleaned_data == '0'


def test_q():
    assert QToken.match('?') == 1
    assert QToken.match('1') is None

    assert QToken('?').cleaned_data == '?'


def test_hash():
    assert HashToken.match('#') == 1
    assert HashToken.match('1') is None

    assert HashToken('#').cleaned_data == '#'


def test_comma():
    assert CommaDelimiter.match(',') == 1
    assert CommaDelimiter.match('1') is None

    assert CommaDelimiter(',').cleaned_data == ','


def test_fraction():
    assert DotDelimiter.match('.') == 1
    assert DotDelimiter.match('1') is None

    assert DotDelimiter('.').cleaned_data == '.'


def test_percentage():
    assert PercentageSymbol.match('%') == 1
    assert PercentageSymbol.match('1') is None

    assert PercentageSymbol('%').cleaned_data == '%'


def test_at():
    assert AtSymbol.match('@') == 1
    assert AtSymbol.match('1') is None

    assert AtSymbol('@').cleaned_data == '@'


def test_asterisk():
    assert AsteriskSymbol.match('*0') == 2
    assert AsteriskSymbol.match('1') is None

    assert AsteriskSymbol('*0').value == '0'


def test_underscore():
    assert UnderscoreSymbol.match('_') == 1
    assert UnderscoreSymbol.match('1') is None

    assert UnderscoreSymbol('_').cleaned_data == '_'


@pytest.mark.parametrize('line', ['$', '+', '-', '(', ')', ':', '!', '^',
                                  '&', "'", '~', '{', '}', '<', '>', '=', ' '])
def test_string_without_escape(line):
    assert StringSymbol.match(line) == 1
    assert StringSymbol(line).value == line


@pytest.mark.parametrize('line', [r'\%s' % chr(i) for i in range(33, 256)])
def test_string_with_escape(line):
    assert StringSymbol.match(line) == 2
    assert StringSymbol(line).value == line[1]


def test_string_with_quote():
    assert StringSymbol.match('"hello"') == 7
    assert StringSymbol('"hello"').value == 'hello'

    assert StringSymbol.match('"bye"') == 5
    assert StringSymbol('"bye"').value == 'bye'

    assert StringSymbol.match('"12345"') == 7
    assert StringSymbol('"12345"').value == '12345'
    assert StringSymbol.match('"') is None


@pytest.mark.parametrize('letter', ['E', 'e'])
@pytest.mark.parametrize('sign', ['-', '+'])
def test_scientific_notation(letter, sign):
    line = letter + sign
    assert EToken.match(line) == len(line)

    token = EToken(line)
    assert token.value == sign

    assert EToken.match(line + 'test') == len(line)
    assert EToken.match('test' + line) is None


@pytest.mark.parametrize('line', ['Black', 'Green', 'White', 'Blue', 'Magenta', 'Yellow', 'Cyan', 'Red',
                                  'Color1', 'Color14', 'Color39', 'Color56'])
def test_color(line):
    assert ColorToken.match('[%s]' % line) == len(line) + 2
    assert ColorToken('[%s]' % line).value == line

    assert ColorToken.match(line) is None
    assert ColorToken.match('[' + line) is None
    assert ColorToken.match(line + ']') is None


@pytest.mark.parametrize('op', ['<', '>', '=', '<>', '<=', '>='])
@pytest.mark.parametrize('value', [1, 123, 12345, 123.45, 0.1234])
@pytest.mark.parametrize('sign', ['-', '', '+'])
def test_condition(op, value, sign):
    signed_value = (value * -1) if sign == '-' else value
    assert ConditionToken.match('[%s%s%s]' % (op, sign, value)) == len(op) + len(str(value)) + 2 + len(sign)

    token = ConditionToken('[%s%s%s]' % (op, sign, value))
    assert token.op == op
    assert token.value == signed_value

    assert ConditionToken.match('[%s]' % signed_value) is None
    assert ConditionToken.match('%s' % signed_value) is None


@pytest.mark.parametrize('line', ['yy', 'yyyy', 'm', 'mm', 'mmm', 'mmmm', 'mmmmm',
                                  'd', 'dd', 'ddd', 'dddd', 'h', 'hh', 's', 'ss'])
def test_date(line):
    assert DateTimeToken.match(line) == len(line)
    assert DateTimeToken(line).value == line
    assert DateTimeToken.match('[%s]' % line) is None


@pytest.mark.parametrize('line', ['h', 'm', 's'])
@pytest.mark.parametrize('count', [1, 2, 4, 8])
def test_timedelta(line, count):
    line = ''.join([line] * count)

    assert TimeDeltaToken.match(line) is None
    assert TimeDeltaToken.match('[%s]' % line) == len(line) + 2
    assert TimeDeltaToken('[%s]' % line).value == line


@pytest.mark.parametrize('line', ['AM/PM', 'A/P'])
def test_am_pm(line):
    assert AmPmToken.match(line) == len(line)
    assert AmPmToken(line).value == line


def test_locale_currency():
    assert LocaleCurrencyToken.match('[$USD-409]') == 10
    token = LocaleCurrencyToken('[$USD-409]')
    assert token.curr == 'USD'
    assert token.language_id == 1033
    assert token.calendar_type == 0
    assert token.number_system == 0

    assert LocaleCurrencyToken.match('[$USD]') == 6
    token = LocaleCurrencyToken('[$USD]')
    assert token.curr == 'USD'
    assert token.language_id is None
    assert token.calendar_type is None
    assert token.number_system is None

    assert LocaleCurrencyToken.match('[$-409]') == 7
    assert LocaleCurrencyToken.match('[$-f409]') == 8

    assert LocaleCurrencyToken.match('[$-ffffffff]') == 12
    token = LocaleCurrencyToken('[$-ffffffff]')
    assert token.curr == ''
    assert token.language_id == 65535
    assert token.calendar_type == 255
    assert token.number_system == 255

    assert LocaleCurrencyToken.match('[$$-ffffffff]') == 13

    assert LocaleCurrencyToken.match('[$$-fffffffff]') is None
    assert LocaleCurrencyToken.match('[-fffffffff]') is None
