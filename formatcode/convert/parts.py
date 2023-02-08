# coding: utf-8

from __future__ import division, print_function, unicode_literals

from abc import ABC, abstractmethod
from decimal import Decimal
from operator import eq, ge, gt, le, lt, ne

from six import iteritems

from formatcode.base.utils import cached_property, is_digit
from formatcode.convert.errors import (ConditionError, DateDigitError, DuplicateFractionFormat, GeneralFormatError,
                                       IllegalPartToken)
from formatcode.convert.handlers import (DateHandler, DigitHandler, EmptyHandler, GeneralHandler, StringHandler,
                                         TimeDeltaHandler, UnknownHandler)
from formatcode.lexer.tokens import (AtSymbol, ColorToken, ConditionToken, DateTimeToken, DigitToken, DotDelimiter,
                                     EToken, GeneralToken, LocaleCurrencyToken, SlashSymbol, StringSymbol,
                                     TimeDeltaToken)

common_tokens = {ColorToken, LocaleCurrencyToken}


class FormatPart(ABC):
    color = None
    currency = ''
    language_id = None
    calendar_type = None
    number_system = None

    def __init__(self, fc, tokens=None):
        """
        :type fc: formatcode.convert.fc.FormatCode
        :type tokens: list[formatcode.lexer.tokens.Token]
        """
        self.tokens = tokens
        self.fc = fc

        self.token_types = [t.__class__ for t in self.tokens or []]
        self.unique_tokens = set(self.token_types) - common_tokens

        if ColorToken in self.token_types:
            self.color = self.get_token_by_type(ColorToken).value

        if LocaleCurrencyToken in self.token_types:
            token = self.get_token_by_type(LocaleCurrencyToken)
            self.currency = token.curr
            self.language_id = token.language_id
            self.calendar_type = token.calendar_type
            self.number_system = token.number_system

        self.validate()

        self.handler = self.handler_class(part=self)

    @abstractmethod
    def get_handler(self):
        pass

    @abstractmethod
    def get_checker(self):
        pass

    def get_token_by_type(self, token_type):
        return self.tokens[self.token_types.index(token_type)]

    @cached_property
    def checker(self):
        return self.get_checker()

    def check_value(self, v):
        return self.checker(v)

    def validate(self):
        if GeneralToken in self.unique_tokens and len(self.unique_tokens) > 1:
            raise GeneralFormatError(self.tokens)

    @property
    def handler_class(self):
        if self.tokens is None:
            return UnknownHandler
        elif self.tokens:
            if GeneralToken in self.unique_tokens:
                return GeneralHandler
            else:
                return self.get_handler()
        else:
            return EmptyHandler

    def format(self, value):
        return self.handler.format(value)


class DigitPart(FormatPart):
    handlers = {
        TimeDeltaToken: TimeDeltaHandler,
        DateTimeToken: DateHandler
    }

    def validate(self):
        super(DigitPart, self).validate()

        if DateTimeToken in self.unique_tokens \
                and TimeDeltaToken not in self.unique_tokens \
                and any(isinstance(t, DigitToken) for t in self.tokens):
            raise DateDigitError(self.tokens)

        if DotDelimiter in self.unique_tokens and SlashSymbol in self.unique_tokens:
            raise DuplicateFractionFormat(self.tokens)

        if SlashSymbol in self.unique_tokens:
            if DotDelimiter in self.unique_tokens or EToken in self.unique_tokens:
                raise DuplicateFractionFormat(self.tokens)

        if AtSymbol in self.unique_tokens:
            raise IllegalPartToken(self.tokens)

        if TimeDeltaToken in self.unique_tokens and SlashSymbol in self.unique_tokens:
            raise IllegalPartToken(self.tokens)

    def get_handler(self):
        for token_type, handler in iteritems(self.handlers):
            if token_type in self.unique_tokens:
                return handler
        else:
            return DigitHandler

    def check_value(self, v):
        return isinstance(v, Decimal) and self.checker(v)

    def format(self, value):
        return self.handler.format(value)


class ConditionFreePart(FormatPart):
    def validate(self):
        super(ConditionFreePart, self).validate()

        if ConditionToken in self.unique_tokens:
            raise ConditionError(self.tokens)


class ConditionPart(DigitPart):
    functions = {
        '<': lt,
        '<=': le,
        '=': eq,
        '<>': ne,
        '>=': ge,
        '>': gt,
    }

    @cached_property
    def checker(self):
        return self.get_condition_checker() or self.get_checker()

    def get_condition_checker(self):
        if ConditionToken in self.unique_tokens:
            token = self.get_token_by_type(ConditionToken)
            return lambda v: self.functions[token.op](v, token.value)


class PositivePart(ConditionPart):
    def get_checker(self):
        if self.fc.else_part.tokens is None:
            return lambda v: v >= 0
        else:
            return lambda v: v > 0


class NegativePart(ConditionPart):
    def get_checker(self):
        return lambda v: v < 0


class ZeroPart(ConditionFreePart, DigitPart):
    def get_checker(self):
        return lambda v: v == 0


class StringPart(ConditionFreePart):
    def validate(self):
        super(StringPart, self).validate()

        if self.unique_tokens - {StringSymbol, AtSymbol}:
            raise IllegalPartToken(self.tokens)

    def get_checker(self):
        return lambda v: not is_digit(v)

    def get_handler(self):
        return StringHandler
