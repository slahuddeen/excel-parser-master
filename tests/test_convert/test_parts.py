# coding: utf-8

from __future__ import division, print_function, unicode_literals

from decimal import Decimal

import pytest
from six import text_type

from formatcode.convert.errors import (ConditionError, DateDigitError, DuplicateFractionFormat, GeneralFormatError,
                                       IllegalPartToken)
from formatcode.convert.handlers import (DateHandler, DigitHandler, EmptyHandler, GeneralHandler, StringHandler,
                                         TimeDeltaHandler, UnknownHandler)
from formatcode.convert.parts import NegativePart, PositivePart, StringPart, ZeroPart
from formatcode.lexer.lexer import to_tokens_line


def to_decimal(value):
    try:
        return Decimal(value)
    except:
        pass


@pytest.fixture(scope='module')
def fc():
    class FormatCodeMock(object):
        def __init__(self):
            self.pos_part = PositivePart(fc=self, tokens=[])
            self.neg_part = NegativePart(fc=self, tokens=[])
            self.else_part = ZeroPart(fc=self, tokens=[])
            self.str_part = StringPart(fc=self, tokens=[])

    return FormatCodeMock()


@pytest.mark.parametrize('value', [1234, 1234.1234, 0, u'string', None])
def test_positive_part(value, fc):
    value = to_decimal(value)

    tokens = to_tokens_line('0.0')
    part = PositivePart(fc=fc, tokens=tokens)
    is_positive = isinstance(value, Decimal) and value > 0

    assert part.handler_class == DigitHandler
    assert part.check_value(value) is is_positive


@pytest.mark.parametrize('value', [1234, 1234.1234, 0, u'string', None])
def test_negative_part(value, fc):
    value = to_decimal(value)

    tokens = to_tokens_line('0.0')
    part = NegativePart(fc=fc, tokens=tokens)
    is_negative = isinstance(value, Decimal) and value < 0

    assert part.handler_class == DigitHandler
    assert part.check_value(value) is is_negative


@pytest.mark.parametrize('value', [1234, 1234.1234, 0, u'string', None])
def test_zero_part(value, fc):
    value = to_decimal(value)

    tokens = to_tokens_line('0.0')
    part = ZeroPart(fc=fc, tokens=tokens)
    is_zero = isinstance(value, Decimal) and value == 0

    assert part.handler_class == DigitHandler
    assert part.check_value(value) is is_zero


@pytest.mark.parametrize('value', [1234, 1234.1234, 0, u'string', None])
def test_string_part(value, fc):
    value = to_decimal(value)

    tokens = to_tokens_line('"hello"')
    part = StringPart(fc=fc, tokens=tokens)
    is_digit = isinstance(value, Decimal)

    assert part.handler_class == StringHandler
    assert part.check_value(value) is not is_digit
    assert part.check_value(text_type(value)) is not is_digit


def test_handler_detect(fc):
    assert PositivePart(fc=fc, tokens=to_tokens_line('General')).handler_class == GeneralHandler
    assert PositivePart(fc=fc, tokens=to_tokens_line('0.0')).handler_class == DigitHandler
    assert PositivePart(fc=fc, tokens=to_tokens_line('"hello"')).handler_class == DigitHandler
    assert PositivePart(fc=fc, tokens=to_tokens_line('yy:mm:dd')).handler_class == DateHandler
    assert PositivePart(fc=fc, tokens=to_tokens_line('[h]:mm')).handler_class == TimeDeltaHandler
    assert PositivePart(fc=fc, tokens=to_tokens_line('[h]:mm.00')).handler_class == TimeDeltaHandler
    assert PositivePart(fc=fc, tokens=to_tokens_line('')).handler_class == EmptyHandler
    assert PositivePart(fc=fc, tokens=None).handler_class == UnknownHandler

    assert StringPart(fc=fc, tokens=to_tokens_line('"hello"@')).handler_class == StringHandler


def test_part_validate(fc):
    # GeneralFormatError
    with pytest.raises(GeneralFormatError):
        PositivePart(fc=fc, tokens=to_tokens_line('General0.0General'))

    # DuplicateFractionFormat
    with pytest.raises(DuplicateFractionFormat):
        PositivePart(fc=fc, tokens=to_tokens_line('0.00/0'))

    with pytest.raises(DuplicateFractionFormat):
        PositivePart(fc=fc, tokens=to_tokens_line('0/0E+0'))

    # DateDigitError
    with pytest.raises(DateDigitError):
        PositivePart(fc=fc, tokens=to_tokens_line('yy.00'))

    with pytest.raises(DateDigitError):
        NegativePart(fc=fc, tokens=to_tokens_line('mm.00'))

    with pytest.raises(DateDigitError):
        ZeroPart(fc=fc, tokens=to_tokens_line('dd.00'))

    # ConditionError
    with pytest.raises(ConditionError):
        ZeroPart(fc=fc, tokens=to_tokens_line('[>100]0.0'))

    with pytest.raises(ConditionError):
        StringPart(fc=fc, tokens=to_tokens_line('[>100]0.0'))

    # IllegalPartToken
    with pytest.raises(IllegalPartToken):
        StringPart(fc=fc, tokens=to_tokens_line('0.0'))

    with pytest.raises(IllegalPartToken):
        PositivePart(fc=fc, tokens=to_tokens_line('@0.0'))

    with pytest.raises(IllegalPartToken):
        NegativePart(fc=fc, tokens=to_tokens_line('@0.0'))

    with pytest.raises(IllegalPartToken):
        ZeroPart(fc=fc, tokens=to_tokens_line('@0.0'))

    with pytest.raises(IllegalPartToken):
        ZeroPart(fc=fc, tokens=to_tokens_line('[h]:mm" "?/?'))


@pytest.mark.parametrize('symbol,r1,r2,r3', (
        ('<', False, False, True),
        ('<=', False, True, True),
        ('=', False, True, False),
        ('<>', True, False, True),
        ('>=', True, True, False),
        ('>', True, False, False),
))
@pytest.mark.parametrize('part', (PositivePart, NegativePart))
@pytest.mark.parametrize('value', (-100, 0, 100))
def test_condition_checker(symbol, r1, r2, r3, part, value, fc):
    value = to_decimal(value)

    part = part(fc=fc, tokens=to_tokens_line('[%s%s]0.0' % (symbol, value)))
    assert part.check_value(value + 1) is r1
    assert part.check_value(value) is r2
    assert part.check_value(value - 1) is r3
