# coding: utf-8

from __future__ import division, print_function, unicode_literals

from abc import ABC
from decimal import Decimal

from six import text_type

from formatcode.convert.errors import IllegalPartToken
from formatcode.convert.mask import Mask
from formatcode.convert.utils import split_tokens
from formatcode.lexer.tokens import (AmPmToken, AsteriskSymbol, AtSymbol, ColorToken, CommaDelimiter, DigitToken,
                                     DotDelimiter, EToken, LocaleCurrencyToken, PercentageSymbol, SlashSymbol,
                                     StringSymbol, UnderscoreSymbol)


class BaseHandler(ABC):
    def __init__(self, part):
        """
        :type part: formatcode.convert.parts.FormatPart
        """
        self.part = part
        self.fc = self.part.fc
        self.tokens = self.part.tokens

    def configure(self):
        pass

    def format(self, v):
        return v


class GeneralHandler(BaseHandler):
    remove_sign = False

    def configure(self):
        if self.fc.neg_part == self.part:
            self.remove_sign = True

    def format(self, v):
        if isinstance(v, Decimal):
            if self.remove_sign:
                v = abs(v)
            return text_type(v)
        else:
            return v


class DigitHandler(BaseHandler):
    by_thousand = False
    round_base = None
    fraction_divisor = None
    fraction_divisor_size = None
    e_base = None
    divisor = 1.0
    left_mask = None
    right_mask = None
    extension_mask = None

    def split_format(self):
        if DotDelimiter in self.part.unique_tokens:
            return split_tokens(self.tokens, DotDelimiter)
        elif SlashSymbol in self.part.unique_tokens:
            index = self.part.token_types.index(SlashSymbol)
            left = self.tokens[:index]
            right = self.tokens[index:]

            while left:
                token = left[-1]
                if isinstance(token, StringSymbol) and ' ' in token.value:
                    break
                else:
                    right.insert(0, left.pop())
            return left, right
        elif EToken in self.part.unique_tokens:
            index = self.part.token_types.index(EToken)
            left = self.tokens[:index]
            right = self.tokens[index:]

            if len(right) == 1 or not isinstance(right[1], DigitToken):
                raise IllegalPartToken(self.tokens)
            return left, right
        else:
            return self.tokens, []

    def get_last_digit_token_idx(self, tokens):
        for idx, token in enumerate(reversed(tokens), 1):
            if isinstance(token, DigitToken):
                return len(tokens) - idx
        else:
            return 0

    def prepare_fraction_attributes(self, tokens):
        if tokens:
            n = 0
            has_fraction = False

            for token in tokens:
                if isinstance(token, DigitToken):
                    if self.fraction_divisor is not None:
                        raise IllegalPartToken(self.tokens)
                    n += 1
                elif isinstance(token, SlashSymbol):
                    n = 0
                    has_fraction = True

                    if token.value is not None:
                        self.fraction_divisor = token.value
                elif isinstance(token, EToken):
                    break

            if has_fraction:
                if self.fraction_divisor is None:
                    self.fraction_divisor_size = n
            else:
                self.round_base = n
        else:
            self.round_base = 0

    def prepare_left_mask(self, tokens):
        mask = Mask()

        digit_counter = 0
        for token in reversed(tokens):
            if isinstance(token, DigitToken):
                mask.add(token.value, mask.PH)
                digit_counter = digit_counter % 3 + 1
            elif isinstance(token, (StringSymbol, PercentageSymbol)):
                mask.add(token.value, mask.STRING)
            elif isinstance(token, LocaleCurrencyToken) and self.part.currency:
                mask.add(self.part.currency, mask.STRING)
            elif isinstance(token, CommaDelimiter):
                if digit_counter == 3:
                    mask.add(token.value, mask.COMMA)
            elif isinstance(token, UnderscoreSymbol):
                mask.add(' ', mask.STRING)
            elif isinstance(token, AsteriskSymbol):
                line = ''.join([token.value] * self.fc.asterisk_repeat_count)
                if line:
                    mask.add(line, mask.STRING)
            elif isinstance(token, AmPmToken):
                mask.add(token.value, mask.AM_PM)
            elif isinstance(token, ColorToken):
                pass
            else:
                raise IllegalPartToken(self.tokens)
        return mask

    def prepare_right_masks(self, tokens):
        current_mask = mask = Mask()
        extension_mask = Mask()

        for token in tokens:
            if isinstance(token, EToken):
                current_mask = extension_mask
                current_mask.add(token.value, current_mask.E)
            elif isinstance(token, SlashSymbol):
                current_mask = extension_mask
                current_mask.add(token.value, current_mask.SLASH)
            elif isinstance(token, DigitToken):
                current_mask.add(token.value, current_mask.PH)
            elif isinstance(token, (StringSymbol, PercentageSymbol)):
                current_mask.add(token.value, current_mask.STRING)
            elif isinstance(token, LocaleCurrencyToken) and self.part.currency:
                current_mask.add(self.part.currency, current_mask.STRING)
            elif isinstance(token, UnderscoreSymbol):
                current_mask.add(' ', current_mask.STRING)
            elif isinstance(token, AsteriskSymbol):
                line = ''.join([token.value] * self.fc.asterisk_repeat_count)
                if line:
                    current_mask.add(line, current_mask.STRING)
            elif isinstance(token, AmPmToken):
                current_mask.add(token.value, current_mask.AM_PM)
            elif isinstance(token, (ColorToken, CommaDelimiter)):
                pass
            else:
                raise IllegalPartToken(self.tokens)
        return mask, extension_mask

    def configure(self):
        left, right = self.split_format()

        if PercentageSymbol in self.part.unique_tokens:
            n = self.part.token_types.count(PercentageSymbol)
            self.divisor /= (100 ** n)

        if CommaDelimiter in self.part.unique_tokens:
            if SlashSymbol not in self.part.unique_tokens:
                if EToken in self.part.unique_tokens:
                    token_types = [t.__class__ for t in left]
                    last_digit_token_idx = self.get_last_digit_token_idx(left)
                else:
                    token_types = self.part.token_types
                    last_digit_token_idx = self.get_last_digit_token_idx(self.tokens)

                for token_type in token_types[last_digit_token_idx + 1:]:
                    if token_type == CommaDelimiter:
                        self.divisor *= 1000
                    else:
                        break
                self.by_thousand = CommaDelimiter in token_types[:last_digit_token_idx]
            else:
                self.by_thousand = True

        if EToken in self.part.token_types:
            self.e_base = sum(isinstance(t, DigitToken) for t in left)

        self.prepare_fraction_attributes(right)
        self.left_mask = self.prepare_left_mask(left)
        self.right_mask, self.extension_mask = self.prepare_right_masks(right)


class StringHandler(BaseHandler):
    def format(self, v):
        line = []
        for token in self.tokens:
            if isinstance(token, AtSymbol):
                line.append(v)
            elif isinstance(token, LocaleCurrencyToken):
                line.append(self.part.currency)
            else:
                line.append(token.value)
        return ''.join(line)


class DateHandler(BaseHandler):
    pass


class TimeDeltaHandler(BaseHandler):
    pass


class EmptyHandler(BaseHandler):
    def format(self, v):
        return self.part.currency


class UnknownHandler(BaseHandler):
    def format(self, v):
        if self.fc.str_part == self.part:
            return v
        else:
            return '###'
