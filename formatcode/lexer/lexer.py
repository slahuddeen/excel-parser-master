# coding: utf-8

from __future__ import division, print_function, unicode_literals

from formatcode.lexer.errors import DuplicateUniqueToken, MatchError
from formatcode.lexer.tokens import (AmPmToken, AsteriskSymbol, AtSymbol, BlockDelimiter, ColorToken, CommaDelimiter,
                                     ConditionToken, DateTimeToken, DotDelimiter, EToken, GeneralToken, HashToken,
                                     LocaleCurrencyToken, PercentageSymbol, QToken, SlashSymbol, StringSymbol,
                                     TimeDeltaToken, UnderscoreSymbol, ZeroToken)

token_types = [GeneralToken, ZeroToken, SlashSymbol, QToken, HashToken, CommaDelimiter, DotDelimiter,
               PercentageSymbol, AtSymbol, AsteriskSymbol, UnderscoreSymbol, StringSymbol, EToken, ColorToken,
               ConditionToken, DateTimeToken, TimeDeltaToken, AmPmToken, LocaleCurrencyToken, BlockDelimiter]


def to_tokens_line(line):
    tokens_line = []
    block_tokens = []
    while line:
        for token_type in token_types:
            end = token_type.match(line)

            if end:
                token = token_type(value=line[:end])
                tokens_line.append(token)

                # Some token types are unique to the block
                if token_type in (TimeDeltaToken, ConditionToken, ColorToken, LocaleCurrencyToken,
                                  SlashSymbol, DotDelimiter, EToken):
                    if token_type in block_tokens:
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
