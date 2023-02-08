# coding: utf-8

from __future__ import division, print_function, unicode_literals

from formatcode.base.errors import FormatCodeError


class ConverterError(FormatCodeError):
    pass


class ConditionError(ConverterError):
    pass


class PartsCountError(ConverterError):
    pass


class DateDigitError(ConverterError):
    pass


class IllegalPartToken(ConverterError):
    pass


class GeneralFormatError(ConverterError):
    pass


class DuplicateFractionFormat(ConverterError):
    pass
