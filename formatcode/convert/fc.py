# coding: utf-8

from __future__ import division, print_function, unicode_literals
from sys import platform
from six.moves import zip_longest

from formatcode.convert.errors import PartsCountError
from formatcode.convert.parts import NegativePart, PositivePart, StringPart, ZeroPart
from formatcode.convert.utils import split_tokens
from formatcode.base.utils import is_general
from formatcode.lexer.lexer import to_tokens_line
from formatcode.lexer.tokens import BlockDelimiter
from datetime import datetime
from formatcode.lexer.tokens import DateTimeToken
from formatcode.lexer.tokens import SlashSymbol
from formatcode.lexer.tokens import StringSymbol
from formatcode.lexer.tokens import AmPmToken
from formatcode.lexer.tokens import LocaleCurrencyToken

parts_types = (PositivePart, NegativePart, ZeroPart, StringPart)


class FormatCode(object):
    def __init__(self, line, asterisk_repeat_count=0):
        self.asterisk_repeat_count = asterisk_repeat_count
        if ";" not in line and not is_general(line):
            line = line + ";-" + line

        self.format_string = line
        tokens = to_tokens_line(line)
        self.parts = self.parts_from_tokens(tokens)
        self.pos_part, self.neg_part, self.else_part, self.str_part = self.parts

        for part in self.parts:
            part.handler.configure()

    def parts_from_tokens(self, tokens):
        """
        :param list tokens: Tokens line
        :rtype: list[formatcode.convert.parts.FormatPart]
        """
        tokens_by_part = split_tokens(tokens, BlockDelimiter)
        
        if len(tokens_by_part) > len(parts_types):
            # There can be only 4 parts
            raise PartsCountError(tokens)

        parts = [pt(fc=self, tokens=ts) for pt, ts in zip_longest(parts_types, tokens_by_part)]
        return parts

    def format(self, value):
        if value not in (None, ''):

            # Shortcut "General" format.
            #if is_general(self.format_string.lower()):
            #    # Values above this amount are rounded.
            #    if value < 1000000000 and value > -1000000000:
            #        return str(value)
            #    else:
            #        return str(round(value))

            # If datetime, use the custom formatter.
            if (isinstance(value, datetime)):
                return self.format_datetime(value)

            for part in self.parts:
                if part.checker(value):
                    return part.format(value)
            else:
                return self.else_part.format(value)
        else:
            return value

    def format_datetime(self, value: datetime) -> str:
        
        # Excel to Python symbol map.
        leading_zero_escape_char = '#' if platform == 'win32' else '-'
        symbol_map = {
            'yyyy' : '%Y',
            'yy': '%y',
            'YYYY' : '%Y',
            'YY': '%y',
            'mmmm': '%B',
            'mmm': '%b',
            'MMM': '%b',
            'MM' : '%m',
            'M' : f"%{leading_zero_escape_char}m",
            # 'mm' and 'm' are special cases in code.
            'dddd': '%A',
            'ddd': '%a',
            'DD': '%d',
            "D":  f"%{leading_zero_escape_char}d",
            'dd': '%d',
            "d":  f"%{leading_zero_escape_char}d",
            #'HH','H','hh''h' are special cases in code.
            'ss': '%S',
            's': f'%{leading_zero_escape_char}S',
            'am/pm': '%p'  
        }

        # Look fr an MA/PM marker.
        format_tokens = self.pos_part.tokens
        has_ampm = False
        for token in format_tokens:
            if isinstance(token, AmPmToken):
                has_ampm = True

        # Start output as an empty string that may be appended to.
        formatted = ''

        # Loop through the token is turn.
        for token_index, token in enumerate(format_tokens):
            
            # Is this a format placeholder?
            if isinstance(token, DateTimeToken):

                # Load the symbol and find its strftime quivalent.
                symbol = token.cleaned_data['value']
                symbol_format_string = None

                # Special case of "m" or "mm", as could be month or minutes.
                if (symbol == "m" or symbol == "mm"):
                    
                    # Look from current node for the next symbol in either direction.
                    prev_symbol = self._find_date_token_symbol(token_index, -1, format_tokens)
                    next_symbol = self._find_date_token_symbol(token_index, +1, format_tokens)

                    # If the next adjacent token is hours or seconds, this means minutes.
                    if self._is_hours_or_seconds(prev_symbol, next_symbol):
                        if (symbol == "mm"):
                            symbol_format_string = '%M'
                        else:
                            symbol_format_string = f'%{leading_zero_escape_char}M'

                    # Otherwise, months.
                    else:
                        if (symbol == "mm"):
                            symbol_format_string = '%m'
                        else:
                            symbol_format_string = f"%{leading_zero_escape_char}m"

                # Special case of "h" or "hh". Use 12 hour if there is an AmPmToken in the string.
                elif (symbol == "h" or symbol == "hh" or symbol == "H" or symbol == "HH"):

                    # All strftime symbols start with "%"
                    symbol_format_string = "%"

                    # If "h", add the marker.
                    if (len(symbol) == 1):
                        symbol_format_string += leading_zero_escape_char
                
                    # If A</PM presetnt, use 12 hour, else 24.
                    symbol_format_string += ("I" if has_ampm else "H")

                # Not a special case, look in the map.
                else:
                    symbol_format_string = symbol_map[symbol]

                # Format this component.
                formatted_per_token = value.strftime(symbol_format_string)
                
                # Add to over all string.
                formatted += formatted_per_token

            # Handle Slashes.
            elif isinstance(token, SlashSymbol):

                # Insert a slash.
                formatted += '/'

            # Handle strings.
            elif isinstance(token, StringSymbol):

                # Load string value and add to fomatted output.
                symbol = token.cleaned_data['value']
                formatted += symbol

            # Handle AmPmToken
            elif isinstance(token, AmPmToken):
                
                # Add either AM or PM.
                formatted += "AM" if value.hour < 12 else "PM"

            # Skip these.
            elif isinstance(token, LocaleCurrencyToken):
                pass

            # Catch other tokens that may need to be coded as elif cases above.
            else:
                raise Exception('Unknown tokne.')
        
        # Return completed formatted string.
        return formatted

    def _find_date_token_symbol(self, start_index, direction, tokens):

        # Find limit. Either one past the end or one past the start.
        stop = len(tokens) if (direction==+1) else -1

        # Loop from the next-to-start item until the end.
        for index in range(start_index + direction, stop, direction):

            # Pull out the current token.
            curr_token = tokens[index]

            # Is this a DateToken?
            if isinstance(curr_token, DateTimeToken):

                # Found it, return the symbol.
                return curr_token.cleaned_data['value']
        
        # Reached the end of the sequence.
        return None

    def _is_hours_or_seconds(self, prev_symbol, next_symbol):

        # Join both, as we're only doing a "contains" search.
        symbols = ((prev_symbol or "") + (next_symbol or "")).upper()

        # If the combined string contains H or S, return true.
        if "H" in symbols or "S" in symbols:
            return True
        else:
            return False


        