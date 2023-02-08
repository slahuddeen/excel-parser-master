# coding: utf-8

from __future__ import division, print_function, unicode_literals

from six.moves import zip_longest

from formatcode.convert.errors import PartsCountError
from formatcode.convert.parts import NegativePart, PositivePart, StringPart, ZeroPart
from formatcode.convert.utils import split_tokens
from formatcode.lexer.lexer import to_tokens_line
from formatcode.lexer.tokens import BlockDelimiter

parts_types = (PositivePart, NegativePart, ZeroPart, StringPart)


class FormatCode(object):
    def __init__(self, line, asterisk_repeat_count=0):
        self.asterisk_repeat_count = asterisk_repeat_count

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
            for part in self.parts:
                if part.checker(value):
                    return part.format(value)
            else:
                return self.else_part.format(value)
        else:
            return value
