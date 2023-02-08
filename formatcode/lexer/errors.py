# coding: utf-8

from __future__ import division, print_function, unicode_literals
from formatcode.base.errors import FormatCodeError


class LexerError(FormatCodeError):
    pass


class MatchError(LexerError):
    pass


class DuplicateUniqueToken(LexerError):
    pass
