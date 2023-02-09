# coding: utf-8

from __future__ import division, print_function, unicode_literals

from formatcode.lexer.errors import DuplicateUniqueToken, MatchError
from formatcode.lexer.tokens import (AmPmToken, AsteriskSymbol, AtSymbol, BlockDelimiter, ColorToken, CommaDelimiter,
                                     ConditionToken, DateTimeToken, DotDelimiter, EToken, GeneralToken, HashToken,
                                     LocaleCurrencyToken, PercentageSymbol, QToken, SlashSymbol, StringSymbol,
                                     TimeDeltaToken, UnderscoreSymbol, ZeroToken, ForceNumberToken)

token_types = [GeneralToken, ZeroToken, SlashSymbol, QToken, HashToken, CommaDelimiter, DotDelimiter,
               PercentageSymbol, AtSymbol, AsteriskSymbol, UnderscoreSymbol, StringSymbol, EToken, ColorToken,
               ConditionToken, DateTimeToken, TimeDeltaToken, AmPmToken, LocaleCurrencyToken, BlockDelimiter, ForceNumberToken]


def to_tokens_line(line):
    tokens_line = []
    block_tokens = []
    previous_token = None
    while line:
        for token_type in token_types:
            if previous_token == "_":
                line = " " + line[1:]
            end = token_type.match(line)                
            if end:
                token = token_type(value=line[:end])                                   
                if previous_token == "_":
                    tokens_line.append(StringSymbol(" "))
                    previous_token = token_type
                else:
                    if token_type ==  UnderscoreSymbol:
                        previous_token = "_"
                    else:
                        previous_token == token_type
                        tokens_line.append(token)
                    # Some token types are unique to the block
                    # (SlashSymbol fromoved from following list as it stops datetime formatting.)
                    if token_type in (TimeDeltaToken, ConditionToken, ColorToken, LocaleCurrencyToken,
                                    DotDelimiter, EToken):   
                        if token_type in block_tokens and token_type.symbol != '.':
                            raise DuplicateUniqueToken(token, line)
                        else:
                            block_tokens.append(token_type)
                    elif token_type == BlockDelimiter:
                        block_tokens.clear()
                line = line[end:]
                break
        else:
            raise MatchError(line)
    return tokens_line
