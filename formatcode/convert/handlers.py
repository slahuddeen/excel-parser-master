# coding: utf-8

from __future__ import division, print_function, unicode_literals

from abc import ABC
from decimal import Decimal
from fractions import Fraction

from sigfig import round
from six import text_type

from formatcode.convert.errors import IllegalPartToken
from formatcode.convert.mask import Mask
from formatcode.convert.utils import split_tokens
from formatcode.lexer.tokens import (AmPmToken, AsteriskSymbol, AtSymbol, ColorToken, CommaDelimiter, DigitToken,
                                     DotDelimiter, EToken, LocaleCurrencyToken, PercentageSymbol, SlashSymbol,
                                     StringSymbol, UnderscoreSymbol, ForceNumberToken, QToken)


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
        # Is this the [m] formatter with a number?
        if self.fc.format_string == '[m];-[m]' and isinstance(v, float) and v >= 0 and v < 1:            
            # Find number of minutes.
            return f'[{int(v * 1440)}]'

        # Apply general formatting.
        return str(v)


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
    zero_mask = None
    extension_mask = None

    def format(self, value):
        
        if not isinstance(value, str):
            value = str(value)
        original_value = value

        if len(self.right_mask.tokens) == 0:
            value = round(value, decimals=0, type=str)

        if self.fc.neg_part.tokens:
            value = value.strip('-')
       
        if value == '0' and self.part.fc.else_part.tokens:           
            new_value_array = []
            next_value = iter(self.zero_mask.tokens)
            for index, token in enumerate(self.zero_mask.tokens):
                if token.value == '?' and next(next_value).value == '?' and len(new_value_array) < len(self.zero_mask.tokens):
                    new_value_array.append('  ')
                elif token.value == '#' or token.value == '?':
                    pass
                else:
                    new_value_array.append(token.value)
        elif self.part.fc.pos_part is not None:
            left_value = value.split(".")[0]
            left_token_count: int = len(left_value)
            
            if [token for token in self.left_mask.tokens if token.value == ',']:
                left_value_array = list('{:,}'.format(int(left_value)))
                left_value_array_static = list('{:,}'.format(int(left_value)))
            else:
                left_value_array = list(left_value)
                left_value_array_static =  list(left_value)
            
            new_left_value_array = []
            counter:int = len(left_value_array) - 1
            pos_counter:int = 0
            for index, token in reversed(list(enumerate(self.left_mask.tokens))):
                if token.value == '  ' or token.value == ' )' or token.value == ' -':
                    token.value = ' '
                if token.type == 1 and token.value:
                    for char in left_value_array_static:
                        try:
                            new_left_value_array.append(left_value_array.pop())
                        except:
                            pass
                        counter -= 1
                    if index == len(self.left_mask.tokens) - 1:
                        new_left_value_array.insert(0, token.value[::-1])
                    else:
                        new_left_value_array.append(token.value[::-1])
                elif token.type == 2:
                    if len(left_value_array) == 0 and token.value != '#' and counter >= 0:
                        new_left_value_array.append(token.value)
                    elif counter >= 0 and token.value != '?' and left_value != '0':
                        new_left_value_array.append(left_value_array.pop())
                        counter -= 1
                    elif left_value == '0' and [token for token in self.left_mask.tokens if token.value == '0'] and token.value == '0':
                        try:
                            new_left_value_array.append(left_value_array.pop())
                        except:
                            pass
                        counter -= 1
                    elif token.value == '0' and len(value.split(".")[0]) < len([token for token in self.left_mask.tokens if "0" in token.value]):
                        new_left_value_array.append(token.value)
                        counter -= 1
                    elif token.value == '?':
                        new_left_value_array.append(' ')
                        counter -= 1

            
            for char in left_value_array:
                if counter >= 0:
                    if self.left_mask.tokens != []:
                        if not '0' in self.left_mask.tokens and float(''.join([s for s in left_value.strip('-') .split() if s.isdigit()])) == 0:
                            pass
                        else:
                            new_left_value_array.append(left_value_array[counter])
                            counter -= 1
                    else:
                        new_left_value_array.append(left_value_array[counter])
                        counter -= 1

            new_left_value = ''.join(new_left_value_array)[::-1]

            # Right part
            new_value_array = [new_left_value]
            right_token_count: int = 0
            if len(self.right_mask.tokens) > 0:
                try:
                    right_value = value.split(".")[1]
                except:
                    right_value = ''
                last_token = [token for token in reversed(self.right_mask.tokens) if token.type == 2]

                for index, token in enumerate(self.right_mask.tokens):
                    right_token_count += 1
                    if token.type == 2 and right_token_count > len(right_value):
                        right_value = round(value, decimals=right_token_count, type=str).split(".")[1]
                    if token.type == 1 and token.value != '  ':
                        if '-' not in original_value:
                            right_value += token.value.strip(')')
                        else:
                            right_value += token.value
                    else:
                        if token.value == '  '  or token.value == ' )' or token.value == ' -':
                            right_value = right_value + '  '
                        else:
                            right_value = round(value, decimals=right_token_count, type=str).split(".")[1]
                new_value_array.append('.')
                new_value_array.append(right_value)

        if self.extension_mask.tokens != []:
            if '.' in original_value:
                fraction = str(Fraction(float( "0." + original_value.split(".")[1])).limit_denominator())               
            else:
                fraction = ''
            for index, token in enumerate(self.extension_mask):
                if token.value == '?' and len(fraction) < len(self.extension_mask) - 1:
                    new_value_array.append(' ')
                elif token.value == '/' and '.' in original_value:
                    new_value_array.append(fraction)
            if not '.' in original_value:
                new_value_array.append('   ')

        try:
            if float(''.join([s for s in ''.join(new_value_array).strip('-').split() if s.isdigit() or s == '.'])) == 0:
                if '-0' in ''.join(new_value_array): 
                    for index, token in enumerate(new_value_array):
                        new_value_array.pop(index)
                        token = token.removeprefix('-')
                        new_value_array.insert(index, token)
        except ValueError:
            pass

        token_count: int = 0
        if self.part.currency is not None and self.part.currency != '':
            if len([token for token in self.part.tokens if isinstance(token, LocaleCurrencyToken)]) == 0:
                # find out where the currency is ment to go
                for token in self.part.tokens:
                    
                    if isinstance(token, LocaleCurrencyToken):
                        if token_count == len(self.part.tokens) - 2:
                            return ''.join(new_value_array.append(self.part.currency))
                        if token_count == 1:
                            return ''.join(new_value_array.insert(0, self.part.currency))
                    token_count += 1

        return ''.join(new_value_array)


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
        for token in tokens:
            if isinstance(token, DigitToken):
                mask.add(token.value, mask.PH)
                digit_counter = digit_counter % 3 + 1
            elif isinstance(token, (StringSymbol, PercentageSymbol)):
                mask.add(token.value, mask.STRING)
            elif isinstance(token, LocaleCurrencyToken) and self.part.currency:
                mask.add(self.part.currency, mask.STRING)
            elif isinstance(token, CommaDelimiter):
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
            elif isinstance(token, AtSymbol):
                pass
            else:
                IllegalPartToken(self.tokens)
        return mask

    def prepare_zero_mask(self, tokens):
        mask = Mask()

        if tokens is None:
            return None
        digit_counter = 0
        for token in tokens:
            if isinstance(token, DigitToken):
                mask.add(token.value, mask.PH)
                digit_counter = digit_counter % 3 + 1
            elif isinstance(token, (StringSymbol, PercentageSymbol)):
                mask.add(token.value, mask.STRING)
            elif isinstance(token, LocaleCurrencyToken) and self.part.currency:
                mask.add(self.part.currency, mask.STRING)
            elif isinstance(token, CommaDelimiter):
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
            elif isinstance(token, AtSymbol):
                pass
            else:
                IllegalPartToken(self.tokens)
        return mask

    def prepare_right_masks(self, tokens):
        current_mask = mask = Mask()
        extension_mask = Mask()
        next_token = iter(tokens)
        for token in tokens:
            if isinstance(token, EToken):
                current_mask = extension_mask
                current_mask.add(token.value, current_mask.E)
            elif isinstance(token, SlashSymbol) and next(next_token).value == '?':
                current_mask = extension_mask
                current_mask.add('/', current_mask.SLASH)
            elif isinstance(token, QToken):
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
            elif isinstance(token, ForceNumberToken):                
                current_mask.add(token.value, current_mask.STRING)
            else:
                IllegalPartToken(self.tokens)
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
        self.zero_mask = self.prepare_zero_mask(self.part.fc.else_part.tokens)


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

