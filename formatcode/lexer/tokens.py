# coding: utf-8

from __future__ import division, print_function, unicode_literals

import re

from six import add_metaclass

from formatcode.base.utils import cached_property, Singleton
from formatcode.lexer import locals


class Token(object):
    def __init__(self, value):
        self.cleaned_data = self.clean(value)

    @classmethod
    def match(cls, line):
        raise NotImplementedError

    def clean(self, value):
        return value


@add_metaclass(Singleton)
class SingleSymbolToken(Token):
    symbol = None

    @classmethod
    def match(cls, line):
        if line.startswith(cls.symbol):
            return len(cls.symbol)

    @property
    def value(self):
        return self.symbol


class GeneralToken(SingleSymbolToken):
    symbol = locals.GENERAL


class BlockDelimiter(SingleSymbolToken):
    symbol = locals.BLOCK_DELIMITER


class DigitToken(SingleSymbolToken):
    pass


class ZeroToken(DigitToken):
    symbol = locals.ZERO


class QToken(DigitToken):
    symbol = locals.QUESTION


class HashToken(DigitToken):
    symbol = locals.HASH


class CommaDelimiter(SingleSymbolToken):
    symbol = locals.COMMA


class DotDelimiter(SingleSymbolToken):
    symbol = locals.DOT


class PercentageSymbol(SingleSymbolToken):
    symbol = locals.PERCENT


class AtSymbol(SingleSymbolToken):
    symbol = locals.AT


class UnderscoreSymbol(SingleSymbolToken):
    symbol = locals.UNDERSCORE


class RegexpToken(Token):
    regexp = None

    @classmethod
    def match(cls, line):
        m = cls.regexp.search(line)
        if m:
            return m.end()

    def clean(self, value):
        return self.regexp.search(value).groupdict()

    def __getattr__(self, item):
        return self.cleaned_data[item]


class SlashSymbol(RegexpToken):
    regexp = re.compile(r'(?P<value>(?<=^/)[0-9]*)')

    def clean(self, value):
        m = super(SlashSymbol, self).clean(value)
        m['value'] = int(m['value']) if m['value'] else None
        return m


class AsteriskSymbol(RegexpToken):
    regexp = re.compile(r'(?P<value>(?<=^\*).)')


class StringSymbol(RegexpToken):
    regexp = re.compile(r'(?P<value>(^[$+\-():!^&\'~{}<>= ]|(?<=^\\).|^"[^"]*"))')

    def clean(self, value):
        m = super(StringSymbol, self).clean(value)
        if m['value'].startswith('"') and len(m['value']) > 1:
            m['value'] = m['value'].strip('"')
        return m


class EToken(RegexpToken):
    regexp = re.compile(r'(?P<value>(?<=^[Ee])[+-])')


class ColorToken(RegexpToken):
    regexp = re.compile(r'^\[(?P<value>(Black|Green|White|Blue|Magenta|Yellow|Cyan|Red|'
                        r'Color([1-9]|[1-4][0-9]|5[0-6])))]')


class ConditionToken(RegexpToken):
    regexp = re.compile(r'^\[(?P<op>(<|>|>=|<=|=|<>))(?P<value>([-+]?[0-9]+(\.[0-9]+)?))]')

    def clean(self, value):
        m = super(ConditionToken, self).clean(value)
        m['value'] = float(m['value'])
        return m


class DateTimeToken(RegexpToken):
    regexp = re.compile(r'^(?P<value>((yy){1,2}|m{1,5}|d{1,4}|h{1,2}|s{1,2}))')


class TimeDeltaToken(RegexpToken):
    regexp = re.compile(r'^\[(?P<value>[hms]+)]')


class AmPmToken(RegexpToken):
    regexp = re.compile(r'^(?P<value>(AM/PM|A/P))')


class LocaleCurrencyToken(RegexpToken):
    regexp = re.compile(r'^\[\$(?P<curr>[^-]*)(-(?P<info>[0-9A-Fa-f]{1,8}))?]')

    def clean(self, value):
        m = super(LocaleCurrencyToken, self).clean(value)
        if m['info']:
            m['info'] = int(m['info'], 16)
        return m

    @cached_property
    def language_id(self):
        info = self.cleaned_data['info']
        return info & 0xffff if info is not None else None

    @cached_property
    def calendar_type(self):
        info = self.cleaned_data['info']
        return info >> 16 & 0xff if info is not None else None

    @cached_property
    def number_system(self):
        info = self.cleaned_data['info']
        return info >> 24 & 0xff if info is not None else None
